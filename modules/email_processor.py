"""
modules/email_processor.py
Monitors inbox and routes medical PDFs and headcount files.
"""

import os
import time
from datetime import datetime, timedelta

from config import CONFIG

class EmailProcessor:

    def __init__(self, outlook_app, pdf_extractor, excel_updater,
                 reconciler, notifier, ui=None):
        self.outlook      = outlook_app
        self.extractor    = pdf_extractor
        self.updater      = excel_updater
        self.reconciler   = reconciler
        self.notifier     = notifier
        self.ui           = ui

    def run(self):
        namespace = self.outlook.GetNamespace("MAPI")
        inbox     = namespace.GetDefaultFolder(6)

        processed_medical   = self._get_or_create(inbox, "Processed Medical")
        processed_headcount = self._get_or_create(inbox, "Processed Headcount")

        messages   = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        hours      = CONFIG["EMAIL_HOURS"]
        time_window = datetime.now() - timedelta(hours=hours)
        all_msgs   = list(messages)

        if self.ui:
            self.ui.info(f"Scanning {len(all_msgs)} inbox items "
                         f"(last {hours}h)")

        processed = 0
        for message in all_msgs:
            try:
                if not hasattr(message, "Subject") or message.Class != 43:
                    continue
                received = message.ReceivedTime.replace(tzinfo=None)
                if received < time_window:
                    break  # sorted descending, safe to stop

                subject = (message.Subject or "").lower()
                body    = (message.Body    or "").lower()

                if "headcount" in subject or "headcount" in body:
                    self._handle_headcount(
                        message, processed_headcount
                    )
                    processed += 1

                elif "medical" in subject or "medical" in body:
                    self._handle_medical(
                        message, processed_medical
                    )
                    processed += 1

            except Exception as e:
                if self.ui:
                    self.ui.error(f"Error processing message: {e}")

        if self.ui:
            self.ui.success(f"Processed {processed} relevant email(s)")

    # ── Handlers ──────────────────────────────────────────────
    def _handle_headcount(self, message, dest_folder):
        if self.ui:
            self.ui.info(f"Headcount email: {message.Subject}")
        save_folder = CONFIG["HC_FOLDER"]
        for att in message.Attachments:
            fname = att.FileName.lower()
            if fname.endswith((".xlsx", ".xls", ".csv")):
                fpath = self._unique_path(save_folder, att.FileName)
                att.SaveAsFile(fpath)
                new_c, exit_c = self.reconciler.reconcile(fpath)
                self.notifier.send_headcount_notification(
                    new_c, exit_c, att.FileName
                )
        message.UnRead = False
        message.Move(dest_folder)

    def _handle_medical(self, message, dest_folder):
        if self.ui:
            self.ui.info(f"Medical email: {message.Subject}")
        save_folder = CONFIG["SAVE_FOLDER"]
        for att in message.Attachments:
            if att.FileName.lower().endswith(".pdf"):
                fpath = self._unique_path(save_folder, att.FileName)
                att.SaveAsFile(fpath)
                data = self.extractor.extract(fpath)

                # Email-address fallback if name still missing
                if not (data or {}).get("Personnel Names"):
                    sender = (message.SenderEmailAddress or "").lower()
                    if data is None: data = {}
                    data["_sender_email"] = sender

                self.updater.update(data)
        message.UnRead = False
        message.Move(dest_folder)

    # ── Helpers ───────────────────────────────────────────────
    @staticmethod
    def _get_or_create(parent, name):
        for f in parent.Folders:
            if f.Name == name:
                return f
        return parent.Folders.Add(name)

    @staticmethod
    def _unique_path(folder, filename):
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            base, ext = os.path.splitext(path)
            path = f"{base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        return path
