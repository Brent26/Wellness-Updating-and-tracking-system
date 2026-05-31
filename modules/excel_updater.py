"""
modules/excel_updater.py
Handles all reads/writes to the Medical_Examinations.xlsx Periodics sheet.
Includes robust duplicate detection and conflict logging.
"""

import re
import os
import pandas as pd
from datetime import datetime, timedelta
from openpyxl import load_workbook

from config import CONFIG
from modules.conflict_logger import ConflictLogger

REQUIRED_COLS = ["UpdateDate", "UpdateStatus", "DaysRemaining",
                 "StatusFlag", "FallbackUsed"]

class ExcelUpdater:

    def __init__(self, ui=None):
        self.ui      = ui
        self.logger  = ConflictLogger(ui=ui)
        self.path    = CONFIG["EXCEL_PATH"]
        self.sheet   = CONFIG["PERIODICS_SHEET"]

    # ── Public ────────────────────────────────────────────────
    def update(self, extracted_data):
        if not extracted_data:
            if self.ui: self.ui.warn("Skipping — no data extracted")
            return

        has_id   = bool(extracted_data.get("EmployeeID"))
        has_name = bool(extracted_data.get("Personnel Names"))

        if not has_id and not has_name:
            if self.ui:
                self.ui.warn("Skipping — no EmployeeID or name found")
            return

        df = self._load()
        self._ensure_columns(df)

        # Calculate NextDue
        date_done = extracted_data.get("DateDone")
        if pd.notna(date_done) if date_done is not None else False:
            ps_group = extracted_data.get("PSGroup", "")
            intervals = CONFIG["EXAM_INTERVALS"]
            interval  = intervals.get(ps_group, intervals["default"])
            extracted_data["NextDue"] = date_done + timedelta(days=interval)
        else:
            extracted_data["NextDue"] = None

        extracted_data["UpdateStatus"] = "Confirmed"
        extracted_data["UpdateDate"]   = datetime.today().strftime("%d-%b-%Y")

        # Duplicate check
        is_dup, match_type, match_idx = self._is_duplicate(df, extracted_data)

        if is_dup:
            # Conflict: same name but different IDs
            if match_type == "Name" and has_id:
                existing_id = df.loc[match_idx, "EmployeeID"]
                if (pd.notna(existing_id) and
                        str(existing_id) != str(extracted_data["EmployeeID"])):
                    if self.ui:
                        self.ui.warn(
                            f"ID conflict — existing: {existing_id} "
                            f"vs incoming: {extracted_data['EmployeeID']} "
                            f"— logged for manual review"
                        )
                    self.logger.log(extracted_data, existing_id)
                    return

            if self.ui:
                self.ui.info(
                    f"Existing record found (matched by {match_type}) — updating"
                )
            for col, val in extracted_data.items():
                if col in df.columns:
                    df.loc[match_idx, col] = val
        else:
            if self.ui: self.ui.success("New record — adding to sheet")
            df = pd.concat(
                [df, pd.DataFrame([extracted_data])], ignore_index=True
            )

        self._recalculate(df)
        self._save(df)
        if self.ui: self.ui.success("Periodics sheet saved")

    # ── Private ───────────────────────────────────────────────
    def _load(self):
        df = pd.read_excel(self.path, sheet_name=self.sheet)
        df["DateDone"] = pd.to_datetime(df.get("DateDone"), errors="coerce")
        df["NextDue"]  = pd.to_datetime(df.get("NextDue"),  errors="coerce")
        return df

    def _ensure_columns(self, df):
        for col in REQUIRED_COLS:
            if col not in df.columns:
                df[col] = None

    def _is_duplicate(self, df, data):
        emp_id = data.get("EmployeeID")
        name   = self._normalise(data.get("Personnel Names", ""))

        # Priority 1 — EmployeeID
        if emp_id and "EmployeeID" in df.columns:
            match = df[df["EmployeeID"].astype(str) == str(emp_id)]
            if not match.empty:
                return True, "EmployeeID", match.index[0]

        # Priority 2 — Normalised name
        if name and "Personnel Names" in df.columns:
            df["_norm"] = df["Personnel Names"].apply(self._normalise)
            match = df[df["_norm"] == name]
            if not match.empty:
                return True, "Name", match.index[0]

        return False, None, None

    def _recalculate(self, df):
        today               = datetime.today()
        df["DateDone"]      = pd.to_datetime(df["DateDone"], errors="coerce")
        df["NextDue"]       = pd.to_datetime(df["NextDue"],  errors="coerce")
        df["DaysRemaining"] = (df["NextDue"] - today).dt.days
        df["StatusFlag"]    = df["DaysRemaining"].apply(self._flag)
        df["DateDone"]      = df["DateDone"].dt.strftime("%d-%b-%Y")
        df["NextDue"]       = df["NextDue"].dt.strftime("%d-%b-%Y")

    def _save(self, df):
        # Drop any temp columns before saving
        df = df.drop(columns=["_norm"], errors="ignore")
        with pd.ExcelWriter(
            self.path, engine="openpyxl", mode="a",
            if_sheet_exists="replace"
        ) as writer:
            df.to_excel(writer, sheet_name=self.sheet, index=False)

    @staticmethod
    def _flag(d):
        if pd.isna(d):  return "Unknown"
        if d < 0:       return "Overdue"
        if d <= 30:     return "Due Soon"
        return "Up to Date"

    @staticmethod
    def _normalise(name):
        if pd.isna(name): return ""
        return re.sub(r"\s+", " ", str(name).strip().lower())
