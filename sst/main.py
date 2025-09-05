from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
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


def get_conn() -> sqlite3.Connection:
    if "conn" not in _state:
        conn = connect()
        init_schema(conn)
        _state["conn"] = conn
    return _state["conn"]


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
    # Authentication is delegated to the site SSO reverse proxy, which sets X-User.
    return request.headers.get("x-user") or os.environ.get("SST_USER", "mfarouk")


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
    r = _get_result(conn, result_id, include_deleted=True)
    trail = conn.execute(
        "SELECT * FROM audit_trail WHERE entity='assay_result' AND entity_id=? ORDER BY audit_id",
        (str(result_id),),
    ).fetchall()
    return templates.TemplateResponse(request, "result.html", ctx(request, r=r, trail=trail))


@app.get("/audit", response_class=HTMLResponse)
def audit_view(request: Request, limit: int = 200, conn: sqlite3.Connection = Depends(get_conn)):
    rows = conn.execute(
        "SELECT * FROM audit_trail ORDER BY audit_id DESC LIMIT ?", (min(limit, 1000),)
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
    tested_at: str


class DeleteIn(BaseModel):
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
    sp = conn.execute("SELECT * FROM specifications WHERE spec_id=?", (body.spec_id,)).fetchone()
    if not sp or not conn.execute("SELECT 1 FROM samples WHERE sample_id=?", (body.sample_id,)).fetchone():
        raise HTTPException(404, "sample or specification not found")
    rv, oos = evaluate(
        body.measured_value,
        sp["lower_limit"],
        sp["upper_limit"],
        regime.results.rounding,
        regime.results.limit_inclusive,
    )
    actor = current_user(request)
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
            body.tested_at,
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
