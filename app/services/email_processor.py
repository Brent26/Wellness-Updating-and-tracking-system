"""
app/services/email_processor.py
Wraps EmailProcessor for the Flask web app.
"""

import time
from datetime import datetime
from app.extensions import db
from app.models.job_run import JobRun


def run():
    from config import CONFIG
    from modules.email_processor import EmailProcessor
    from modules.pdf_extractor   import PDFExtractor
    from modules.excel_updater   import ExcelUpdater
    from modules.headcount       import HeadcountReconciler
    from modules.notifications   import NotificationService

    try:
        import win32com.client
        outlook = win32com.client.Dispatch("Outlook.Application")
    except Exception as e:
        job = JobRun(
            task_name   = "Process Inbox Emails",
            status      = "failed",
            notes       = f"Outlook unavailable: {e}",
            started_at  = datetime.utcnow(),
            finished_at = datetime.utcnow(),
            duration_s  = 0,
        )
        db.session.add(job)
        db.session.commit()
        return job.to_dict()

    job = JobRun(task_name="Process Inbox Emails", status="running")
    db.session.add(job)
    db.session.commit()

    start = time.time()
    try:
        processor = EmailProcessor(
            outlook_app   = outlook,
            pdf_extractor = PDFExtractor(),
            excel_updater = ExcelUpdater(),
            reconciler    = HeadcountReconciler(),
            notifier      = NotificationService(outlook),
        )
        count = processor.run()

        job.status      = "done"
        job.notes       = f"{count} email(s) processed"
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