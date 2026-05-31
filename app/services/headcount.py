"""
app/services/headcount.py
Wraps HeadcountReconciler for the Flask web app.
"""

import time
import pandas as pd
from datetime import datetime
from app.extensions import db
from app.models.job_run import JobRun
from app.models.headcount_record import HeadcountRecord


def _safe_str(val):
    return str(val) if pd.notna(val) else None


def _safe_int(val):
    if not pd.notna(val):
        return None
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return None


def run(file_path=None):
    from config import CONFIG
    from modules.headcount import HeadcountReconciler

    path = file_path or CONFIG["HC_FOLDER"]

    job = JobRun(task_name="Headcount Reconciliation", status="running")
    db.session.add(job)
    db.session.commit()

    start = time.time()
    try:
        reconciler = HeadcountReconciler()
        new_df, exited_df = reconciler.reconcile(path)
        new_c  = len(new_df)
        exit_c = len(exited_df)

        for _, row in new_df.iterrows():
            db.session.add(HeadcountRecord(
                personnel_name    = _safe_str(row.get("Personnel Names", "")),
                employee_number   = _safe_int(row.get("Pers.No.")),
                department        = _safe_str(row.get("Personnel Area")),
                personnel_subarea = _safe_str(row.get("Personnel Subarea")),
                position          = _safe_str(row.get("Position")),
                ps_group          = _safe_str(row.get("PS group")),
                flag_type         = "new",
                source_file       = file_path,
                job_run_id        = job.id,
            ))

        for _, row in exited_df.iterrows():
            db.session.add(HeadcountRecord(
                personnel_name    = _safe_str(row.get("Personnel Names", "")),
                employee_number   = _safe_int(row.get("EmployeeID")),
                department        = _safe_str(row.get("Department")),
                personnel_subarea = _safe_str(row.get("SubArea")),
                position          = _safe_str(row.get("Role")),
                ps_group          = _safe_str(row.get("PSGroup")),
                flag_type         = "exited",
                source_file       = file_path,
                job_run_id        = job.id,
            ))

        job.status      = "done"
        job.notes       = f"{new_c} new, {exit_c} exits"
        job.finished_at = datetime.utcnow()
        job.duration_s  = round(time.time() - start, 2)

    except Exception as e:
        job.status      = "failed"
        job.notes       = str(e)
        job.finished_at = datetime.utcnow()
        job.duration_s  = round(time.time() - start, 2)

    finally:
        db.session.commit()

    return job.to_dict()
