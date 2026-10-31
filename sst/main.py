from __future__ import annotations

import os
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from . import __version__, audit
from .db import connect, init_schema
from .regimes import Regime, available_regimes, load_app_config, load_regime
from .rounding import evaluate

BASE = Path(__file__).resolve().parent
app = FastAPI(title="Stability Sample Tracker", version=__version__, docs_url="/api/docs")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

_state: dict = {}
# A plain Lock (not RLock): FastAPI may run a generator dependency's setup and teardown on
# different worker threads, and only Lock may be released from a thread other than the acquirer.
_conn_lock = threading.Lock()

DELETE_ROLES = {"QC Supervisor", "QA"}
AMEND_ROLES = {"QC Analyst", "Senior QC Analyst", "QC Supervisor"}
VERIFY_ROLES = {"QC Supervisor"}
PENDING_VERIFICATION = "Amended - pending verification"
DECIMAL_RE = re.compile(r"^-?\d+(\.\d+)?$")


def get_conn():
    """One connection, one request at a time: each request's writes + audit rows form one transaction."""
    _conn_lock.acquire()
    try:
        if "conn" not in _state:
            conn = connect()
            init_schema(conn)
            _state["conn"] = conn
        yield _state["conn"]
    finally:
        _conn_lock.release()


def get_regime() -> Regime:
    if "regime" not in _state:
        _state["regime"] = load_regime()
    return _state["regime"]


def reset_state(conn: sqlite3.Connection | None = None, regime: Regime | None = None) -> None:
    _state.clear()
    if conn is not None:
        _state["conn"] = conn
    if regime is not None:
        _state["regime"] = regime


def current_user(request: Request) -> str:
    # Authentication is delegated to the site SSO reverse proxy, which sets X-User on every request
    # and strips any client-supplied value. The app is not exposed without the proxy.
    return request.headers.get("x-user") or os.environ.get("SST_USER", "mfarouk")


def provisioned_user(conn: sqlite3.Connection, user_id: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM users WHERE user_id=? AND active=1", (user_id,)).fetchone()
    if not row:
        raise HTTPException(403, f"user {user_id!r} is not provisioned in SST")
    return row


def ctx(request: Request, **kw):
    cfg = load_app_config()
    return {
        "request": request,
        "cfg": cfg,
        "regime": get_regime(),
        "regimes": available_regimes(),
        "user": current_user(request),
        "version": __version__,
        **kw,
    }


# ---------- HTML views ----------


@app.get("/", response_class=HTMLResponse)
def home(request: Request, conn: sqlite3.Connection = Depends(get_conn)):
    rows = conn.execute(
        """SELECT s.*, u.full_name AS owner_name,
                  (SELECT COUNT(*) FROM batches b JOIN samples sm ON sm.batch_id=b.batch_id
                     WHERE b.study_id=s.study_id) AS n_samples,
                  (SELECT COUNT(*) FROM batches b JOIN samples sm ON sm.batch_id=b.batch_id
                     JOIN assay_results r ON r.sample_id=sm.sample_id
                     WHERE b.study_id=s.study_id AND r.oos=1 AND r.deleted=0) AS n_oos
           FROM studies s JOIN users u ON u.user_id=s.owner ORDER BY s.start_date DESC"""
    ).fetchall()
    return templates.TemplateResponse(request, "studies.html", ctx(request, studies=rows))


@app.get("/samples", response_class=HTMLResponse)
def samples(
    request: Request,
    study: str | None = None,
    status: str | None = None,
    conn: sqlite3.Connection = Depends(get_conn),
):
    q = """SELECT sm.*, b.study_id, c.label AS cond_label, u.full_name AS assignee,
                  (SELECT COUNT(*) FROM assay_results r
                     WHERE r.sample_id=sm.sample_id AND r.deleted=0) AS n_results,
                  (SELECT COUNT(*) FROM assay_results r
                     WHERE r.sample_id=sm.sample_id AND r.deleted=0 AND r.oos=1) AS n_oos
           FROM samples sm JOIN batches b ON b.batch_id=sm.batch_id
           JOIN storage_conditions c ON c.cond_id=sm.cond_id
           LEFT JOIN users u ON u.user_id=sm.assigned_to WHERE 1=1"""
    args: list = []
    if study:
        q += " AND b.study_id=?"
        args.append(study)
    if status:
        q += " AND sm.status=?"
        args.append(status)
    q += " ORDER BY sm.due_date DESC, sm.sample_id"
    rows = conn.execute(q, args).fetchall()
    studies = [r[0] for r in conn.execute("SELECT study_id FROM studies ORDER BY study_id")]
    return templates.TemplateResponse(
        request, "samples.html", ctx(request, samples=rows, studies=studies, f_study=study, f_status=status)
    )


@app.get("/samples/{sample_id}", response_class=HTMLResponse)
def sample_detail(request: Request, sample_id: str, conn: sqlite3.Connection = Depends(get_conn)):
    sm = conn.execute(
        """SELECT sm.*, b.study_id, b.mfg_date, b.pack, c.label AS cond_label, st.product, st.strength
           FROM samples sm JOIN batches b ON b.batch_id=sm.batch_id JOIN studies st ON st.study_id=b.study_id
           JOIN storage_conditions c ON c.cond_id=sm.cond_id WHERE sm.sample_id=?""",
        (sample_id,),
    ).fetchone()
    if not sm:
        raise HTTPException(404, "sample not found")
    results = conn.execute(
        """SELECT r.*, sp.test_name, sp.method, sp.unit, sp.limit_text, u.full_name AS analyst_name
           FROM assay_results r JOIN specifications sp ON sp.spec_id=r.spec_id
           JOIN users u ON u.user_id=r.analyst WHERE r.sample_id=? AND r.deleted=0 ORDER BY sp.spec_id""",
        (sample_id,),
    ).fetchall()
    specs = conn.execute(
        "SELECT * FROM specifications WHERE study_id=? ORDER BY spec_id", (sm["study_id"],)
    ).fetchall()
    return templates.TemplateResponse(
        request, "sample.html", ctx(request, s=sm, results=results, specs=specs)
    )


@app.get("/results/{result_id}", response_class=HTMLResponse)
def result_detail(request: Request, result_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    # Deleted results stay viewable with their history (SOP-DI-004 s4.3: soft delete, record retained).
    return _result_page(request, conn, result_id, None, 200)


@app.get("/audit", response_class=HTMLResponse)
def audit_view(request: Request, limit: int = 200, conn: sqlite3.Connection = Depends(get_conn)):
    rows = conn.execute(
        "SELECT * FROM audit_trail ORDER BY audit_id DESC LIMIT ?", (max(1, min(limit, 1000)),)
    ).fetchall()
    return templates.TemplateResponse(request, "audit.html", ctx(request, trail=rows))


@app.get("/config", response_class=HTMLResponse)
def config_view(request: Request):
    return templates.TemplateResponse(request, "config.html", ctx(request))


# ---------- JSON API ----------


class ResultIn(BaseModel):
    sample_id: str
    spec_id: str
    measured_value: str = Field(pattern=r"^-?\d+(\.\d+)?$")
    instrument: str | None = None
    tested_at: datetime  # instrument/measurement time, ISO 8601 with offset; stored as UTC

    def tested_at_utc(self) -> str:
        if self.tested_at.tzinfo is None:
            raise ValueError("tested_at must carry a timezone offset")
        return self.tested_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class DeleteIn(BaseModel):
    reason: str


class AmendIn(BaseModel):
    measured_value: str = Field(pattern=r"^-?\d+(\.\d+)?$")
    reason: str


class VerifyIn(BaseModel):
    reason: str


def _get_result(conn: sqlite3.Connection, result_id: int, include_deleted: bool = False) -> sqlite3.Row:
    r = conn.execute(
        """SELECT r.*, sp.test_name, sp.method, sp.unit, sp.limit_text, sp.lower_limit, sp.upper_limit,
                  u.full_name AS analyst_name
           FROM assay_results r JOIN specifications sp ON sp.spec_id=r.spec_id
           JOIN users u ON u.user_id=r.analyst WHERE r.result_id=? AND (r.deleted=0 OR ?)""",
        (result_id, int(include_deleted)),
    ).fetchone()
    if not r:
        raise HTTPException(404, "result not found")
    return r


def _row(r: sqlite3.Row) -> dict:
    return {k: r[k] for k in r.keys()}


@app.get("/api/results/{result_id}")
def api_get_result(result_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    return _row(_get_result(conn, result_id))


@app.post("/api/results", status_code=201)
def api_create_result(
    body: ResultIn,
    request: Request,
    conn: sqlite3.Connection = Depends(get_conn),
    regime: Regime = Depends(get_regime),
):
    actor = current_user(request)
    provisioned_user(conn, actor)
    sp = conn.execute("SELECT * FROM specifications WHERE spec_id=?", (body.spec_id,)).fetchone()
    sample = conn.execute(
        "SELECT sm.sample_id, b.study_id FROM samples sm JOIN batches b ON b.batch_id=sm.batch_id"
        " WHERE sm.sample_id=?",
        (body.sample_id,),
    ).fetchone()
    if not sp or not sample:
        raise HTTPException(404, "sample or specification not found")
    if sp["study_id"] != sample["study_id"]:
        raise HTTPException(
            422, f"specification {body.spec_id} does not belong to study {sample['study_id']}"
        )
    try:
        tested_at = body.tested_at_utc()
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    rv, oos = evaluate(
        body.measured_value,
        sp["lower_limit"],
        sp["upper_limit"],
        regime.results.rounding,
        regime.results.limit_inclusive,
    )
    cur = conn.execute(
        "INSERT INTO assay_results(sample_id, spec_id, measured_value, reportable_value, oos, analyst,"
        " instrument, tested_at) VALUES (?,?,?,?,?,?,?,?)",
        (
            body.sample_id,
            body.spec_id,
            body.measured_value,
            str(rv),
            int(oos),
            actor,
            body.instrument,
            tested_at,
        ),
    )
    audit.record(
        conn,
        regime,
        actor=actor,
        entity="assay_result",
        entity_id=cur.lastrowid,
        action="create",
        field="measured_value",
        new_value=body.measured_value,
        reason="Initial result entry",
    )
    conn.commit()
    return _row(_get_result(conn, cur.lastrowid))


@app.delete("/api/results/{result_id}")
def api_delete_result(
    result_id: int,
    body: DeleteIn,
    request: Request,
    conn: sqlite3.Connection = Depends(get_conn),
    regime: Regime = Depends(get_regime),
):
    r = _get_result(conn, result_id)
    actor = current_user(request)
    if provisioned_user(conn, actor)["role"] not in DELETE_ROLES:
        raise HTTPException(403, "deleting results requires the QC Supervisor or QA role")
    try:
        audit.record(
            conn,
            regime,
            actor=actor,
            entity="assay_result",
            entity_id=result_id,
            action="delete",
            field="status",
            old_value=r["status"],
            new_value="Deleted",
            reason=body.reason,
        )
    except audit.ReasonRequired as e:
        conn.rollback()
        raise HTTPException(422, str(e)) from e
    conn.execute("UPDATE assay_results SET deleted=1, status='Deleted' WHERE result_id=?", (result_id,))
    conn.commit()
    return {"result_id": result_id, "status": "Deleted"}


@app.get("/api/results/{result_id}/audit")
def api_result_audit(result_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    rows = conn.execute(
        "SELECT * FROM audit_trail WHERE entity='assay_result' AND entity_id=? ORDER BY audit_id",
        (str(result_id),),
    ).fetchall()
    return [_row(r) for r in rows]


@app.get("/api/health")
def health(regime: Regime = Depends(get_regime)):
    return {"status": "ok", "version": __version__, "regime": regime.code}


# ---------- Result amendment and verification (CHG-4127; SOP-DI-004 s4-s5, SOP-QC-021 s6.2) ----------


def _audit_updates(conn, regime, actor: str, result_id: int, changes: list[tuple], reason: str) -> None:
    for field, old, new in changes:
        audit.record(
            conn,
            regime,
            actor=actor,
            entity="assay_result",
            entity_id=result_id,
            action="update",
            field=field,
            old_value=old,
            new_value=new,
            reason=reason,
        )


def _amend(
    conn: sqlite3.Connection, regime: Regime, actor: str, result_id: int, measured_value: str, reason: str
) -> sqlite3.Row:
    if provisioned_user(conn, actor)["role"] not in AMEND_ROLES:
        raise HTTPException(403, "amending results requires an analyst or QC Supervisor role")
    measured_value = measured_value.strip()
    if not DECIMAL_RE.match(measured_value):
        raise HTTPException(422, "measured_value must be a decimal number, e.g. 0.155")
    r = _get_result(conn, result_id)
    if r["status"] == PENDING_VERIFICATION:
        raise HTTPException(409, "result has an amendment awaiting second-person verification")
    if measured_value == r["measured_value"]:
        raise HTTPException(422, "measured_value is unchanged; nothing to amend")
    rv, oos = evaluate(
        measured_value,
        r["lower_limit"],
        r["upper_limit"],
        regime.results.rounding,
        regime.results.limit_inclusive,
    )
    oos_changed = int(oos) != r["oos"]
    status = (
        PENDING_VERIFICATION
        if oos_changed and regime.records.second_person_verification_on_oos_change
        else "Amended"
    )
    changes = [
        (f, old, new)
        for f, old, new in [
            ("measured_value", r["measured_value"], measured_value),
            ("reportable_value", r["reportable_value"], str(rv)),
            ("oos", r["oos"], int(oos)),
            ("status", r["status"], status),
        ]
        if str(old) != str(new)
    ]
    try:
        _audit_updates(conn, regime, actor, result_id, changes, reason)
    except audit.ReasonRequired as e:
        conn.rollback()
        raise HTTPException(422, str(e)) from e
    conn.execute(
        "UPDATE assay_results SET measured_value=?, reportable_value=?, oos=?, status=? WHERE result_id=?",
        (measured_value, str(rv), int(oos), status, result_id),
    )
    conn.commit()
    return _get_result(conn, result_id)


def _amended_by(conn: sqlite3.Connection, result_id: int) -> str | None:
    row = conn.execute(
        "SELECT actor FROM audit_trail WHERE entity='assay_result' AND entity_id=? AND field='status'"
        " AND new_value=? ORDER BY audit_id DESC LIMIT 1",
        (str(result_id), PENDING_VERIFICATION),
    ).fetchone()
    return row["actor"] if row else None


def _verify(conn: sqlite3.Connection, regime: Regime, actor: str, result_id: int, reason: str) -> sqlite3.Row:
    if provisioned_user(conn, actor)["role"] not in VERIFY_ROLES:
        raise HTTPException(403, "verifying an amendment requires the QC Supervisor role")
    r = _get_result(conn, result_id)
    if r["status"] != PENDING_VERIFICATION:
        raise HTTPException(409, "result has no amendment awaiting verification")
    if _amended_by(conn, result_id) == actor:
        raise HTTPException(403, "the verifier must not be the analyst who amended the result")
    try:
        _audit_updates(conn, regime, actor, result_id, [("status", r["status"], "Amended")], reason)
    except audit.ReasonRequired as e:
        conn.rollback()
        raise HTTPException(422, str(e)) from e
    conn.execute("UPDATE assay_results SET status='Amended' WHERE result_id=?", (result_id,))
    conn.commit()
    return _get_result(conn, result_id)


@app.patch("/api/results/{result_id}")
def api_amend_result(
    result_id: int,
    body: AmendIn,
    request: Request,
    conn: sqlite3.Connection = Depends(get_conn),
    regime: Regime = Depends(get_regime),
):
    return _row(_amend(conn, regime, current_user(request), result_id, body.measured_value, body.reason))


@app.post("/api/results/{result_id}/verify")
def api_verify_amendment(
    result_id: int,
    body: VerifyIn,
    request: Request,
    conn: sqlite3.Connection = Depends(get_conn),
    regime: Regime = Depends(get_regime),
):
    return _row(_verify(conn, regime, current_user(request), result_id, body.reason))


def _result_page(request: Request, conn: sqlite3.Connection, result_id: int, error: str | None, status: int):
    r = _get_result(conn, result_id, include_deleted=True)
    trail = conn.execute(
        "SELECT * FROM audit_trail WHERE entity='assay_result' AND entity_id=? ORDER BY audit_id",
        (str(result_id),),
    ).fetchall()
    return templates.TemplateResponse(
        request,
        "result.html",
        ctx(request, r=r, trail=trail, error=error, pending=PENDING_VERIFICATION),
        status_code=status,
    )


@app.post("/results/{result_id}/amend", response_class=HTMLResponse)
def amend_result_form(
    request: Request,
    result_id: int,
    measured_value: str = Form(""),
    reason: str = Form(""),
    conn: sqlite3.Connection = Depends(get_conn),
    regime: Regime = Depends(get_regime),
):
    try:
        _amend(conn, regime, current_user(request), result_id, measured_value, reason)
    except HTTPException as e:
        if e.status_code == 404:
            raise
        return _result_page(request, conn, result_id, e.detail, e.status_code)
    return RedirectResponse(f"/results/{result_id}", status_code=303)


@app.post("/results/{result_id}/verify", response_class=HTMLResponse)
def verify_amendment_form(
    request: Request,
    result_id: int,
    reason: str = Form(""),
    conn: sqlite3.Connection = Depends(get_conn),
    regime: Regime = Depends(get_regime),
):
    try:
        _verify(conn, regime, current_user(request), result_id, reason)
    except HTTPException as e:
        if e.status_code == 404:
            raise
        return _result_page(request, conn, result_id, e.detail, e.status_code)
    return RedirectResponse(f"/results/{result_id}", status_code=303)
