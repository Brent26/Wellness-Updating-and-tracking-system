"""
app/services/medic_reconciler.py
Wraps MedicIdentificationReconciler for the Flask web app.
"""

import time
from datetime import datetime


def _safe_int(val):
    if val is None or val == "":
        return None
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return None
from app.extensions import db
from app.models.job_run import JobRun
from app.models.medic_record import MedicRecord


def run(file_path=None):
    from config import CONFIG
    from modules.medic_identification import MedicIdentificationReconciler

    path = file_path or CONFIG["MEDIC_ID_FOLDER"]

    job = JobRun(task_name="Reconcile MEDIC ID Records", status="running")
    db.session.add(job)
    db.session.commit()

    start = time.time()
    try:
        reconciler = MedicIdentificationReconciler()
        result     = reconciler.reconcile(path)

        if result:
            mismatches, exits, synced = result

            # Save findings to the database
            for m in (mismatches or []):
                record = MedicRecord(
                    personnel_name      = m.get("Personnel Names", ""),
                    employee_number     = _safe_int(m.get("Employee Number")),
                    department          = m.get("Department", ""),
                    personnel_subarea   = m.get("Personnel Subarea", ""),
                    position            = m.get("Position", ""),
                    ps_group            = m.get("PS Group", ""),
                    record_type         = "mismatch",
                    date_in_periodics   = m.get("Date in DCC PERIODICS", ""),
                    date_in_medic_id    = m.get("Date in MEDIC IDENTIFICATION", ""),
                    date_to_update_to   = m.get("Date to Update To", ""),
                    difference_days     = m.get("Difference (days)"),
                    type_of_medical     = m.get("Type of Medical", ""),
                    source_file         = str(path),
                    job_run_id          = job.id,
                )
                db.session.add(record)

            for e in (exits or []):
                record = MedicRecord(
                    personnel_name         = e.get("Personnel Names", ""),
                    employee_number        = _safe_int(e.get("Employee Number")),
                    department             = e.get("Department", ""),
                    personnel_subarea      = e.get("Personnel Subarea", ""),
                    position               = e.get("Position", ""),
                    ps_group               = e.get("PS Group", ""),
                    record_type            = "exit",
                    last_medical_periodics = e.get("Last Medical (DCC PERIODICS)", ""),
                    exit_status            = e.get("Exit Status", ""),
                    type_of_medical        = "Exit",
                    source_file            = str(path),
                    job_run_id             = job.id,
                )
                db.session.add(record)

            job.status      = "done"
            job.notes       = f"{len(mismatches)} mismatches, {len(exits)} exits, {synced} synced"
            job.finished_at = datetime.utcnow()
            job.duration_s  = round(time.time() - start, 2)
        else:
            job.status      = "done"
            job.notes       = "No findings"
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