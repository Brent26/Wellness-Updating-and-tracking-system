"""
modules/notifications.py
Sends HTML email notifications via Outlook.
"""

import os
import pandas as pd
from datetime import datetime

from config import CONFIG


class NotificationService:

    def __init__(self, outlook_app, ui=None):
        self.outlook = outlook_app
        self.ui      = ui

    # ── Booking Alerts ────────────────────────────────────────
    def send_booking_notification(self):
        if self.ui: self.ui.info("Checking for upcoming/overdue exams...")
        try:
            df = pd.read_excel(CONFIG["EXCEL_PATH"],
                               sheet_name=CONFIG["PERIODICS_SHEET"])
        except Exception as e:
            if self.ui: self.ui.error(f"Cannot read Excel: {e}")
            return

        today = datetime.today()
        if "NextDue" not in df.columns:
            if self.ui: self.ui.warn("'NextDue' column missing — cannot alert")
            return

        df["NextDue"]       = pd.to_datetime(df["NextDue"], errors="coerce")
        df["DaysRemaining"] = (df["NextDue"] - today).dt.days

        if "UpdateStatus" in df.columns:
            df = df[df["UpdateStatus"] != "Exited"]

        alert_df = df[df["DaysRemaining"] <= CONFIG["DAYS_WARNING"]].sort_values(
            "DaysRemaining"
        )

        if alert_df.empty:
            if self.ui:
                self.ui.success("No employees overdue or due soon — no email sent")
            return "No alerts due — no email sent"

        overdue  = alert_df[alert_df["DaysRemaining"] < 0]
        due_soon = alert_df[alert_df["DaysRemaining"] >= 0]

        if self.ui:
            self.ui.result("Overdue",  len(overdue),  "\033[38;5;196m")
            self.ui.result("Due Soon", len(due_soon), "\033[38;5;220m")

        total    = len(alert_df)
        date_str = today.strftime("%d %B %Y")
        html     = self._booking_html(overdue, due_soon, total, date_str)
        subject  = (f"[Medical Examinations] {total} "
                    f"Booking{'s' if total != 1 else ''} Required — {date_str}")
        self._send(subject, html)
        return f"Email sent — {len(overdue)} overdue, {len(due_soon)} due soon"

    # ── Headcount Notification ────────────────────────────────
    def send_headcount_notification(self, new_count, exited_count, hc_filename):
        if new_count == 0 and exited_count == 0:
            return

        today    = datetime.today()
        date_str = today.strftime("%d %B %Y")

        try:
            new_df = pd.read_excel(CONFIG["EXCEL_PATH"],
                                   sheet_name=CONFIG["NEW_EMP_SHEET"])
        except Exception:
            new_df = pd.DataFrame()

        html    = self._headcount_html(new_df, new_count, exited_count,
                                       hc_filename, date_str)
        subject = (f"[Headcount Reconciliation] {new_count} "
                   f"New Employee{'s' if new_count != 1 else ''} "
                   f"Detected — {date_str}")
        self._send(subject, html)

    # ── Internal Send ─────────────────────────────────────────
    def _send(self, subject, html_body):
        try:
            mail          = self.outlook.CreateItem(0)
            mail.To       = CONFIG["NOTIFY_EMAIL"]
            if CONFIG["NOTIFY_CC"]:
                mail.CC   = CONFIG["NOTIFY_CC"]
            mail.Subject  = subject
            mail.HTMLBody = html_body
            mail.Send()
            if self.ui:
                self.ui.success(f"Email sent → {CONFIG['NOTIFY_EMAIL']}")
        except Exception as e:
            if self.ui: self.ui.error(f"Failed to send email: {e}")

    # ── HTML Builders ─────────────────────────────────────────
    def _booking_html(self, overdue, due_soon, total, date_str):
        def table(subset, label, colour):
            if subset.empty: return ""
            rows = ""
            for _, row in subset.iterrows():
                name    = row.get("Personnel Names", "N/A")
                emp_id  = row.get("EmployeeID", row.get("Pers.No.", "N/A"))
                ps_grp  = row.get("PSGroup",   row.get("PS group", "N/A"))
                due     = (row["NextDue"].strftime("%d-%b-%Y")
                           if pd.notna(row["NextDue"]) else "Unknown")
                days    = (int(row["DaysRemaining"])
                           if pd.notna(row["DaysRemaining"]) else None)
                if days is None:
                    days_lbl = "N/A"
                elif days < 0:
                    days_lbl = (f'<span style="color:#cc0000;font-weight:bold">'
                                f'{abs(days)} days overdue</span>')
                else:
                    days_lbl = (f'<span style="color:#b8860b;font-weight:bold">'
                                f'In {days} days</span>')
                rows += (f"<tr><td>{name}</td><td>{emp_id}</td>"
                         f"<td>{ps_grp}</td><td>{due}</td>"
                         f"<td>{days_lbl}</td></tr>")
            td = "padding:8px 12px;border-bottom:1px solid #e0e0e0"
            rows = rows.replace("<td>", f'<td style="{td}">')
            hs   = (f"background:{colour};color:white;"
                    "padding:10px 12px;text-align:left")
            return (f'<h3 style="color:{colour};margin-top:24px">'
                    f'{label} ({len(subset)})</h3>'
                    f'<table style="border-collapse:collapse;width:100%;'
                    f'font-family:Calibri,Arial,sans-serif;font-size:13px">'
                    f'<thead><tr>'
                    f'<th style="{hs}">Full Name</th>'
                    f'<th style="{hs}">Employee ID</th>'
                    f'<th style="{hs}">PS Group</th>'
                    f'<th style="{hs}">Next Due</th>'
                    f'<th style="{hs}">Status</th>'
                    f'</tr></thead><tbody>{rows}</tbody></table>')

        src = os.path.basename(CONFIG["EXCEL_PATH"])
        return (f'<html><body style="font-family:Calibri,Arial,sans-serif;'
                f'font-size:14px;color:#333">'
                f'<p>Hello,</p>'
                f'<p>Automated reminder — <strong>{date_str}</strong>.<br>'
                f'<strong>{total} employee{"s" if total != 1 else ""}</strong> '
                f'require a medical examination booking:</p>'
                f'{table(overdue,  "🚨 Overdue",  "#cc0000")}'
                f'{table(due_soon, "⚠️ Due Soon", "#b8860b")}'
                f'<p style="color:#555;font-size:12px">'
                f'Executive / Top Brass: annual (365 days). '
                f'All others: 2 years (730 days).<br>'
                f'Source: <em>{src}</em></p>'
                f'<p style="color:#aaa;font-size:11px">'
                f'— Wellness Updating and Tracking System</p>'
                f'</body></html>')

    def _headcount_html(self, new_df, new_count, exited_count,
                        hc_filename, date_str):
        rows = ""
        if not new_df.empty:
            for _, row in new_df.iterrows():
                td = "padding:8px 12px;border-bottom:1px solid #e0e0e0"
                rows += (f'<tr>'
                         f'<td style="{td}">{row.get("Pers.No.","N/A")}</td>'
                         f'<td style="{td}">{row.get("Personnel Names","N/A")}</td>'
                         f'<td style="{td}">{row.get("PS group","N/A")}</td>'
                         f'<td style="{td}">{row.get("Position","N/A")}</td>'
                         f'<td style="{td}">{row.get("Personnel Area","N/A")}</td>'
                         f'<td style="{td};color:#b8860b;font-weight:bold">'
                         f'{row.get("Action Taken","Pending")}</td></tr>')

        hs       = "background:#1F4E79;color:white;padding:10px 12px;text-align:left"
        new_tbl  = (f'<h3 style="color:#1F4E79;margin-top:24px">'
                    f'🆕 New Employees ({new_count})</h3>'
                    f'<table style="border-collapse:collapse;width:100%;'
                    f'font-family:Calibri,Arial,sans-serif;font-size:13px">'
                    f'<thead><tr>'
                    f'<th style="{hs}">Pers. No.</th>'
                    f'<th style="{hs}">Full Name</th>'
                    f'<th style="{hs}">PS Group</th>'
                    f'<th style="{hs}">Position</th>'
                    f'<th style="{hs}">Area</th>'
                    f'<th style="{hs}">Action</th>'
                    f'</tr></thead><tbody>{rows}</tbody></table>') if rows else ""

        exited_note = ""
        if exited_count > 0:
            exited_note = (f'<h3 style="color:#cc0000;margin-top:24px">'
                           f'🔴 Possible Leavers ({exited_count})</h3>'
                           f'<p style="font-size:13px">{exited_count} employee'
                           f'{"s" if exited_count != 1 else ""} not found in '
                           f'latest headcount — flagged as <strong>Exited</strong>.</p>')

        src = os.path.basename(CONFIG["EXCEL_PATH"])
        return (f'<html><body style="font-family:Calibri,Arial,sans-serif;'
                f'font-size:14px;color:#333">'
                f'<p>Headcount file <strong>{hc_filename}</strong> processed on '
                f'<strong>{date_str}</strong>.</p>'
                f'{new_tbl}{exited_note}'
                f'<p style="color:#555;font-size:12px">Details in '
                f'<strong>\'{CONFIG["NEW_EMP_SHEET"]}\'</strong> sheet of '
                f'<em>{src}</em>.</p>'
                f'<p style="color:#aaa;font-size:11px">'
                f'— Wellness Updating and Tracking System</p>'
                f'</body></html>')
