"""Deterministic synthetic dataset. All names, batches and values are fictitious."""

from __future__ import annotations

import random
import sqlite3
from datetime import date, datetime, timedelta

from . import audit
from .db import connect, init_schema
from .regimes import load_regime
from .rounding import evaluate

USERS = [
    ("mfarouk", "Mariam Farouk", "QC Analyst"),
    ("jokafor", "Jide Okafor", "QC Analyst"),
    ("lhansen", "Lotte Hansen", "Senior QC Analyst"),
    ("rsato", "Ren Sato", "QC Analyst"),
    ("adiallo", "Aissatou Diallo", "QC Supervisor"),
    ("tbrennan", "Tomas Brennan", "Stability Coordinator"),
    ("qa.review", "QA Reviewer (role account)", "QA"),
]

STUDIES = [
    (
        "STB-2021-004",
        "Velcarin",
        "50 mg film-coated tablets",
        "SP-0417 r3",
        "2021-06-14",
        "Ongoing",
        "tbrennan",
    ),
    (
        "STB-2022-011",
        "Velcarin",
        "100 mg film-coated tablets",
        "SP-0417 r3",
        "2022-02-07",
        "Ongoing",
        "tbrennan",
    ),
    (
        "STB-2022-019",
        "Ardoline",
        "5 mg/mL oral solution",
        "SP-0533 r1",
        "2022-09-19",
        "Ongoing",
        "tbrennan",
    ),
    (
        "STB-2023-003",
        "Nexaprin",
        "20 mg capsules",
        "SP-0602 r2",
        "2023-01-23",
        "Ongoing",
        "adiallo",
    ),
    (
        "STB-2019-027",
        "Velcarin",
        "25 mg film-coated tablets",
        "SP-0417 r2",
        "2019-11-04",
        "Completed",
        "tbrennan",
    ),
]

CONDITIONS = [
    ("LT", "25 °C / 60 % RH", 25.0, 60.0),
    ("INT", "30 °C / 65 % RH", 30.0, 65.0),
    ("ACC", "40 °C / 75 % RH", 40.0, 75.0),
    ("REF", "5 °C ± 3 °C", 5.0, None),
]

# (test, method, unit, lower, upper, limit text)
SPEC_SETS = {
    "tablet": [
        (
            "Assay",
            "HPLC-UV AM-114",
            "% label claim",
            "95.0",
            "105.0",
            "95.0 - 105.0 % of label claim",
        ),
        ("Any unspecified degradant", "HPLC-UV AM-114", "%", None, "0.15", "NMT 0.15 %"),
        ("Total degradation products", "HPLC-UV AM-114", "%", None, "1.0", "NMT 1.0 %"),
        (
            "Dissolution (30 min)",
            "USP <711> App. 2, AM-120",
            "% dissolved",
            "80",
            None,
            "Q = 80 % at 30 min",
        ),
        ("Water content", "KF AM-131", "%", None, "3.0", "NMT 3.0 %"),
    ],
    "solution": [
        (
            "Assay",
            "HPLC-UV AM-207",
            "% label claim",
            "95.0",
            "105.0",
            "95.0 - 105.0 % of label claim",
        ),
        ("Any unspecified degradant", "HPLC-UV AM-207", "%", None, "0.15", "NMT 0.15 %"),
        ("pH", "USP <791>", "pH units", "4.0", "5.0", "4.0 - 5.0"),
    ],
    "capsule": [
        (
            "Assay",
            "HPLC-UV AM-310",
            "% label claim",
            "95.0",
            "105.0",
            "95.0 - 105.0 % of label claim",
        ),
        ("Any unspecified degradant", "HPLC-UV AM-310", "%", None, "0.15", "NMT 0.15 %"),
        (
            "Dissolution (45 min)",
            "USP <711> App. 1, AM-318",
            "% dissolved",
            "75",
            None,
            "Q = 75 % at 45 min",
        ),
    ],
}

TIMEPOINTS = [0, 3, 6, 9, 12, 18, 24, 36, 48, 60]
INSTRUMENTS = ["HPLC-07", "HPLC-09", "HPLC-12", "KF-03", "DIS-02", "DIS-04", "PH-01"]


def _form(strength: str) -> str:
    if "tablet" in strength:
        return "tablet"
    if "solution" in strength:
        return "solution"
    return "capsule"


def _measured(rng: random.Random, test: str, months: int, cond: str, study_id: str = "") -> str:
    if test.startswith("Any unspecified") and cond == "ACC" and months == 6:
        return {"STB-2021-004": "0.155", "STB-2019-027": "0.148"}.get(study_id, "0.121")
    if test == "Assay" and cond == "ACC" and months == 6 and study_id == "STB-2023-003":
        return "94.93"
    stress = {"LT": 0.4, "INT": 0.7, "ACC": 1.4, "REF": 0.2}[cond] * (months / 12)
    if test == "Assay":
        return f"{rng.gauss(100.2 - 1.1 * stress, 0.6):.2f}"
    if test.startswith("Any unspecified"):
        return f"{max(0.01, rng.gauss(0.04 + 0.05 * stress, 0.015)):.3f}"
    if test.startswith("Total degradation"):
        return f"{max(0.05, rng.gauss(0.18 + 0.22 * stress, 0.05)):.2f}"
    if test.startswith("Dissolution"):
        return f"{min(101, rng.gauss(96 - 2.5 * stress, 2.2)):.1f}"
    if test == "Water content":
        return f"{max(0.3, rng.gauss(1.6 + 0.25 * stress, 0.2)):.2f}"
    if test == "pH":
        return f"{rng.gauss(4.5 - 0.08 * stress, 0.08):.2f}"
    raise ValueError(test)


def seed(conn: sqlite3.Connection, today: date | None = None) -> dict:
    rng = random.Random(20210614)
    regime = load_regime()
    today = today or date.today()
    init_schema(conn)
    conn.executemany("INSERT INTO users(user_id, full_name, role) VALUES (?,?,?)", USERS)
    conn.executemany("INSERT INTO storage_conditions VALUES (?,?,?,?)", CONDITIONS)
    analysts = [u[0] for u in USERS if "Analyst" in u[2]]
    n_samples = n_results = 0
    for study in STUDIES:
        sid, product, strength, protocol, start, status, owner = study
        conn.execute("INSERT INTO studies VALUES (?,?,?,?,?,?,?)", study)
        start_d = date.fromisoformat(start)
        form = _form(strength)
        for k, (test, method, unit, lo, hi, text) in enumerate(SPEC_SETS[form], 1):
            conn.execute(
                "INSERT INTO specifications VALUES (?,?,?,?,?,?,?,?)",
                (f"{sid}-S{k:02d}", sid, test, method, unit, lo, hi, text),
            )
        n_batches = 1
        for b in range(n_batches):
            prefix = "VC" if product == "Velcarin" else product[:2].upper()
            batch_id = f"{prefix}{start_d.year % 100:02d}{rng.randint(100, 999)}{chr(65 + b)}"
            conn.execute(
                "INSERT INTO batches VALUES (?,?,?,?,?)",
                (
                    batch_id,
                    sid,
                    (start_d - timedelta(days=rng.randint(20, 45))).isoformat(),
                    "Site 02",
                    "HDPE bottle, 30s" if form != "solution" else "Amber glass 100 mL",
                ),
            )
            conds = ["LT", "ACC"] if form != "solution" else ["REF", "INT"]
            for cond in conds:
                for tp in TIMEPOINTS:
                    if cond in ("ACC", "INT") and tp > 6:
                        continue
                    due = start_d + timedelta(days=int(tp * 30.44))
                    if due > today + timedelta(days=60):
                        continue
                    sample_id = f"{batch_id}-{cond}-{tp:02d}M"
                    if due > today:
                        st, pull, assigned = "Scheduled", "", None
                    else:
                        pull_d = due + timedelta(days=rng.randint(0, 4))
                        pull, assigned = pull_d.isoformat(), rng.choice(analysts)
                        st = (
                            "Reported"
                            if pull_d < today - timedelta(days=45)
                            else rng.choice(["In testing", "Pending review"])
                        )
                    conn.execute(
                        "INSERT INTO samples VALUES (?,?,?,?,?,?,?,?,?)",
                        (
                            sample_id,
                            batch_id,
                            cond,
                            tp,
                            pull,
                            due.isoformat(),
                            st,
                            assigned,
                            f"Chamber {cond}-{rng.randint(1, 3)} / Rack {rng.randint(1, 12)}",
                        ),
                    )
                    n_samples += 1
                    if st == "Scheduled":
                        continue
                    specs = conn.execute(
                        "SELECT * FROM specifications WHERE study_id=? ORDER BY spec_id", (sid,)
                    ).fetchall()
                    for sp in specs:
                        if st == "In testing" and rng.random() < 0.5:
                            continue
                        if (
                            st == "Reported"
                            and sp["spec_id"].endswith(("S03", "S05"))
                            and rng.random() < 0.45
                        ):
                            continue
                        measured = _measured(rng, sp["test_name"], tp, cond, sid)
                        rv, oos = evaluate(
                            measured, sp["lower_limit"], sp["upper_limit"], regime.results.rounding
                        )
                        tested = datetime.fromisoformat(pull) + timedelta(
                            days=rng.randint(1, 9),
                            hours=rng.randint(8, 17),
                            minutes=rng.randint(0, 59),
                        )
                        analyst = assigned or rng.choice(analysts)
                        instrument = rng.choice(
                            INSTRUMENTS[:3] if "HPLC" in sp["method"] else INSTRUMENTS[3:]
                        )
                        cur = conn.execute(
                            "INSERT INTO assay_results(sample_id, spec_id, measured_value, reportable_value,"
                            " oos, analyst, instrument, tested_at, status) VALUES (?,?,?,?,?,?,?,?,?)",
                            (
                                sample_id,
                                sp["spec_id"],
                                measured,
                                str(rv),
                                int(oos),
                                analyst,
                                instrument,
                                tested.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "Reviewed" if st == "Reported" else "Entered",
                            ),
                        )
                        audit.record(
                            conn,
                            regime,
                            actor=analyst,
                            entity="assay_result",
                            entity_id=cur.lastrowid,
                            action="create",
                            field="measured_value",
                            new_value=measured,
                            reason="Initial result entry",
                            at=tested.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                        )
                        n_results += 1
    conn.commit()
    return {"samples": n_samples, "results": n_results}


def main() -> None:
    conn = connect()
    if conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='samples'").fetchone()[0]:
        if conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]:
            print("database already seeded")
            return
    stats = seed(conn)
    print(f"seeded {stats['samples']} samples, {stats['results']} results")


if __name__ == "__main__":
    main()
