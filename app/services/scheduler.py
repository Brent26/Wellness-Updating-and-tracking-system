from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def start_scheduler():
    """Register all cron jobs and start the scheduler."""
    # TODO: import service functions and add jobs here
    # scheduler.add_job(process_inbox, "cron", hour=7, minute=0)
    # scheduler.add_job(full_cycle,    "cron", hour=6, minute=0)
    if not scheduler.running:
        scheduler.start()
