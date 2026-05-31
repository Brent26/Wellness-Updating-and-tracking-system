"""
app/services/pdf_processor.py
Wraps PDFExtractor + ExcelUpdater for the Flask web app.
"""

import time
from datetime import datetime
from app.extensions import db
from app.models.job_run import JobRun


def run(file_path=None):
    from config import CONFIG
    from modules.pdf_extractor import PDFExtractor
    from modules.excel_updater import ExcelUpdater

    path = file_path or CONFIG["SAVE_FOLDER"]

    job = JobRun(task_name="Manual PDF Processing", status="running")
    db.session.add(job)
    db.session.commit()

    start = time.time()
    try:
        extractor = PDFExtractor()
        updater   = ExcelUpdater()
        data      = extractor.extract(path)
        updater.update(data)

        job.status      = "done"
        job.notes       = f"Processed: {path}"
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