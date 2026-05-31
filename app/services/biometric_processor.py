"""
app/services/biometric_processor.py

Two-phase biometric PDF processing:
  1. extract(file_path)  — runs the PDF extractor, returns dict for review
  2. confirm(data)       — writes the (possibly edited) dict to Excel + logs a JobRun
"""

import time
from datetime import datetime

from app.extensions import db
from app.models.job_run import JobRun


def extract(file_path: str) -> dict:
    """
    Phase 1: Extract biometric fields from *file_path*.
    Returns the raw extraction dict (including metadata keys).
    Raises on hard failures so the API can return a 500.
    """
    from modules.Biometric_pdf_extractor import BiometricPDFExtractor
    extractor = BiometricPDFExtractor()
    return extractor.extract(file_path)


def confirm(data: dict, file_path: str) -> dict:
    """
    Phase 2: Write the reviewed/edited *data* to the biometric Excel sheet
    and log a JobRun record.  Returns the JobRun dict.
    """
    from modules.Biometric_excel_writer import BiometricExcelWriter

    job = JobRun(task_name="Biometric Screening", status="running")
    db.session.add(job)
    db.session.commit()

    start = time.time()
    try:
        writer  = BiometricExcelWriter()
        success = writer.write(data)

        name = f"{data.get('First name', '')} {data.get('Last name', '')}".strip()
        if success:
            job.status = "done"
            job.notes  = f"Saved: {name} — {data.get('Date', '—')}"
            if data.get("NeedsReview"):
                job.status = "warning"
                job.notes += f" | Review: {data.get('ReviewReason', '')}"
        else:
            job.status = "failed"
            job.notes  = f"Write failed for {name}"

    except Exception as e:
        job.status = "failed"
        job.notes  = str(e)

    finally:
        job.finished_at = datetime.utcnow()
        job.duration_s  = round(time.time() - start, 2)
        db.session.commit()

    return job.to_dict()
