"""
modules/conflict_logger.py
Logs duplicate/conflict records to a CSV and displays them in the CLI.
"""

import os
import pandas as pd
from datetime import datetime

from config import CONFIG


class ConflictLogger:

    def __init__(self, ui=None):
        self.ui   = ui
        self.path = CONFIG["CONFLICT_LOG"]

    def log(self, extracted_data, existing_id):
        record = {
            "Timestamp":       datetime.today().strftime("%d-%b-%Y %H:%M"),
            "Personnel Names": extracted_data.get("Personnel Names"),
            "Incoming ID":     extracted_data.get("EmployeeID"),
            "Existing ID":     existing_id,
            "FallbackUsed":    extracted_data.get("FallbackUsed", "None"),
            "Action":          "Skipped — manual review needed",
        }
        df = pd.DataFrame([record])
        if os.path.exists(self.path):
            existing = pd.read_csv(self.path)
            df       = pd.concat([existing, df], ignore_index=True)
        df.to_csv(self.path, index=False)
        if self.ui:
            self.ui.warn(f"Conflict logged → {self.path}")

    def display(self):
        if not os.path.exists(self.path):
            if self.ui: self.ui.info("No conflict log found — all clear ✔")
            return

        try:
            df = pd.read_csv(self.path)
        except Exception as e:
            if self.ui: self.ui.error(f"Cannot read conflict log: {e}")
            return

        if df.empty:
            if self.ui: self.ui.info("Conflict log is empty — all clear ✔")
            return

        if self.ui:
            self.ui.result("Total conflicts", len(df))
            print()

        cols   = list(df.columns)
        widths = [max(len(str(c)), df[col].astype(str).str.len().max()) + 2
                  for col, c in zip(df.columns, cols)]

        if self.ui:
            self.ui.table_row(cols, widths)
            self.ui.table_row(["─" * (w - 1) for w in widths], widths)
            for _, row in df.iterrows():
                self.ui.table_row(
                    [row[c] for c in cols], widths
                )
        else:
            print(df.to_string(index=False))
