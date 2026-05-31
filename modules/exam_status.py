"""
modules/exam_status.py
Reads DCC PERIODICS and returns overdue / due-soon / up-to-date counts.
"""

import pandas as pd
from datetime import datetime
from config import CONFIG


def get_exam_status_counts():
    try:
        df = pd.read_excel(CONFIG["EXCEL_PATH"],
                           sheet_name=CONFIG["PERIODICS_SHEET"])
    except Exception:
        return {"overdue": 0, "due_soon": 0, "up_to_date": 0}

    if "NextDue" not in df.columns:
        return {"overdue": 0, "due_soon": 0, "up_to_date": 0}

    if "UpdateStatus" in df.columns:
        df = df[df["UpdateStatus"] != "Exited"]

    if "Personnel Names" in df.columns:
        df = df[df["Personnel Names"].notna() & (df["Personnel Names"] != "")]

    today = datetime.today()
    df["NextDue"] = pd.to_datetime(df["NextDue"], errors="coerce")
    df["_days"]   = (df["NextDue"] - today).dt.days

    valid      = df[df["_days"].notna()]
    warn       = CONFIG.get("DAYS_WARNING", 30)
    overdue    = int((valid["_days"] < 0).sum())
    due_soon   = int(((valid["_days"] >= 0) & (valid["_days"] <= warn)).sum())
    up_to_date = int((valid["_days"] > warn).sum())

    return {"overdue": overdue, "due_soon": due_soon, "up_to_date": up_to_date}
