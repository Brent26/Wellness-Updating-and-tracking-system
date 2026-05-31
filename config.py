"""
config.py — Central configuration for WUTS.
All paths, constants, and tunable parameters live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    # ── Paths ────────────────────────────────────────────────
    "SAVE_FOLDER":    os.getenv("SAVE_FOLDER", r"C:\path\to\periodics"),
    "EXCEL_PATH":     os.getenv("EXCEL_PATH", r"C:\path\to\periodic_medicals.xlsx"),
    "HC_FOLDER":      os.getenv("HC_FOLDER", r"C:\path\to\headcount"),
    "CONFLICT_LOG":   os.getenv("CONFLICT_LOG", r"C:\path\to\conflict_log.csv"),

    # ── Biometric Screening ──────────────────────────────────
    "BIOMETRIC_EXCEL_PATH": os.getenv("BIOMETRIC_EXCEL_PATH", r"C:\path\to\biometric_screening.xlsx"),
    "BIOMETRIC_SHEET":      os.getenv("BIOMETRIC_SHEET", "2026"),
    "BIOMETRIC_PDF_FOLDER": os.getenv("BIOMETRIC_PDF_FOLDER", r"C:\path\to\biometric_pdfs"),

    # ── MEDIC IDENTIFICATION ─────────────────────────────────
    "MEDIC_ID_FOLDER":        os.getenv("MEDIC_ID_FOLDER", r"C:\path\to\medic_classification"),
    "MEDIC_ID_OUTPUT_FOLDER": os.getenv("MEDIC_ID_OUTPUT_FOLDER", r"C:\path\to\medic_classification_output"),

    # ── Email ────────────────────────────────────────────────
    "NOTIFY_EMAIL":   os.getenv("NOTIFY_EMAIL", "notifications@example.com"),
    "NOTIFY_CC":      os.getenv("NOTIFY_CC", ""),

    # ── Business Rules ───────────────────────────────────────
    "DAYS_WARNING":   30,
    "EXAM_INTERVALS": {
        "Executive":  365,
        "Top Brass":  365,
        "default":    730,
    },

    # ── Sheet Names ──────────────────────────────────────────
    "PERIODICS_SHEET": "DCC Medicals",
    "NEW_EMP_SHEET":   "New Employees",
    "EXITS_SHEET":     "Exits",

    # ── Fuzzy Name Matching ──────────────────────────────────
    "FUZZY_NAME_THRESHOLD": 85,

    # ── Filename Noise Words ─────────────────────────────────
    "FILENAME_NOISE":  ["HHS", "form", "medical", "exam",
                        "examination", "report", "results"],

    # ── Email Time Window (hours) ────────────────────────────
    "EMAIL_HOURS": 24,

    # ── Department Column Mappings ───────────────────────────
    "DEPT_COLUMN_MAP": {
        "Personnel Names":   "Personnel Names",
        "Employee Number":   "EmployeeID",
        "Department":        "Department",
        "Personnel Subarea": "Sub Area",
        "Position":          "Role",
        "Sub Section":       "Sub Section",
        "Section":           "Section",
        "Age":               "Age",
        "PS Group":          "PSGroup",
        "Last Medical":      "DateDone",
        "Due Date":          "NextDue",
        "Comment":           "Comment",
    },
}
