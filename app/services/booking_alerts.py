"""
app/services/booking_alerts.py
Wraps NotificationService.send_booking_notification() for the Flask web app.
"""

import time
from datetime import datetime
from app.extensions import db
from app.models.job_run import JobRun


def run():
    job = JobRun(task_name="Send Booking Alerts", status="running")
    db.session.add(job)
    db.session.commit()

    start = time.time()
    try:
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()

        outlook = win32com.client.Dispatch("Outlook.Application")

        from modules.notifications import NotificationService
        notifier = NotificationService(outlook)
        result = notifier.send_booking_notification()

        job.status = "done"
        job.notes  = result
        job.finished_at = datetime.utcnow()
        job.duration_s  = round(time.time() - start, 2)

    except Exception as e:
        job.status      = "failed"
        job.notes       = str(e)
        job.finished_at = datetime.utcnow()
        job.duration_s  = round(time.time() - start, 2)

    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass
        db.session.commit()

    return job.to_dict()