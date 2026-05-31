"""
modules/Biometric_pdf_extractor.py

Extracts patient biometric data from lab results PDFs.

Fields extracted:
    Date, First name, Last name, Age of employee, Gender,
    Glucose level, Total Cholesterol, HIV, PSA, Mammo, Pap Smear
"""

import os
import re
import pdfplumber
from datetime import datetime

from config import CONFIG

_FILENAME_NOISE = {
    w.lower() for w in CONFIG.get("FILENAME_NOISE", [
        "HHS", "form", "medical", "exam", "examination",
        "report", "results", "biometric", "screening", "lab",
        "blood", "test", "copy", "final", "scan",
    ])
}

# ── Regex patterns ───────────────────────────────────────────────
_RE_PATIENT_NAME = re.compile(
    r"Patient\s*:\s*([A-Za-z][A-Za-z '\-]{2,60}?)(?:\n|$|\s{2,})",
    re.IGNORECASE,
)
_RE_DATE = re.compile(
    r"(?:Date\s+of\s+[Tt]est|Date\s+of\s+[Ee]xam|Registered\s+at\s+FO)\s*[:\-]?\s*"
    r"(\d{1,2}/\d{2}/\d{4})",
    re.IGNORECASE,
)
_RE_GENDER = re.compile(
    r"(?:Sex\s*&\s*Age|Age\s*/\s*Gender|Gender)\s*[:/]?\s*(Male|Female)",
    re.IGNORECASE,
)
_RE_AGE = re.compile(
    r"(?:Sex\s*&\s*Age\s*:.*?/\s*(\d{1,3})\s*Y"
    r"|Age\s*/\s*Gender\s*[:/]?\s*(\d{1,3})\s*(?:Male|Female)"
    r"|Age\s*[:/]\s*(\d{1,3}))",
    re.IGNORECASE,
)
_RE_GLUCOSE = re.compile(
    r"GLUCOSE\s*(?:\([^)]*\))?\s*([\d.]+)",
    re.IGNORECASE,
)
_RE_CHOLESTEROL = re.compile(
    r"TOTAL\s*CHOLESTEROL\s*(?:\([^)]*\))?\s*([\d.]+)",
    re.IGNORECASE,
)
# HIV alone on left, lots of whitespace, then NEGATIVE/POSITIVE on right
_RE_HIV = re.compile(
    r"^HIV\s{2,}(NEGATIVE|POSITIVE)",
    re.IGNORECASE | re.MULTILINE,
)
_RE_PSA = re.compile(
    r"\bPSA\b\s+([\d.]+|NOT\s+DONE|N/A|[\w ]+?)(?:\n|$|\s{2,})",
    re.IGNORECASE,
)
_RE_MAMMO = re.compile(
    r"MAMMO(?:GRAM)?\s+([\w][^\n]{0,40}?)(?:\n|$|\s{2,})",
    re.IGNORECASE,
)
_RE_PAP_SMEAR = re.compile(
    r"PAP\s*SMEAR\s+([\w][^\n]{0,40}?)(?:\n|$|\s{2,})",
    re.IGNORECASE,
)


class BiometricPDFExtractor:

    def extract(self, pdf_path: str) -> dict:
        filename = os.path.basename(pdf_path)
        pdf_text = self._read_pdf(pdf_path)

        name, fallback_used = self._extract_name(filename, pdf_text)
        first_name, last_name = self._split_name(name)

        needs_review   = False
        review_reasons = []

        if not name:
            needs_review = True
            review_reasons.append("Name could not be extracted")

        date_val = self._extract_date(pdf_text)
        if date_val is None:
            needs_review = True
            review_reasons.append("Date could not be extracted")

        hiv = self._extract_hiv(pdf_text)
        if hiv is None:
            needs_review = True
            review_reasons.append("HIV result could not be extracted")

        return {
            "Date":              date_val,
            "First name":        first_name,
            "Last name":         last_name,
            "Age of employee":   self._extract_age(pdf_text),
            "Gender":            self._extract_gender(pdf_text),
            "Glucose level":     self._extract_glucose(pdf_text),
            "Total Cholesterol": self._extract_cholesterol(pdf_text),
            "HIV":               hiv,
            "PSA":               self._extract_psa(pdf_text),
            "Mammo":             self._extract_mammo(pdf_text),
            "Pap Smear":         self._extract_pap_smear(pdf_text),
            "SourceFile":        filename,
            "NeedsReview":       needs_review,
            "ReviewReason":      "; ".join(review_reasons),
            "FallbackUsed":      fallback_used,
            "_raw_text":         pdf_text,   # for snapshot view only, not written to Excel
        }

    # ── PDF reading ──────────────────────────────────────────────

    def _read_pdf(self, pdf_path: str) -> str:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
            return "\n".join(pages)
        except Exception:
            return ""

    # ── Name ────────────────────────────────────────────────────

    def _extract_name(self, filename: str, pdf_text: str):
        stem  = os.path.splitext(filename)[0]
        stem  = re.sub(r"[_\-]", " ", stem)
        words = [
            w for w in stem.split()
            if w.lower() not in _FILENAME_NOISE and re.match(r"^[A-Za-z]{2,}$", w)
        ]
        if len(words) >= 2:
            return " ".join(words), "Filename"

        match = _RE_PATIENT_NAME.search(pdf_text)
        if match:
            name = match.group(1).strip()
            if len(name.split()) >= 1:
                return name, "PDF Body"

        if len(words) == 1:
            return words[0], "Filename only"

        return "", "None"

    def _split_name(self, full_name: str):
        parts = full_name.strip().split()
        if len(parts) >= 2:
            return parts[0], " ".join(parts[1:])
        if len(parts) == 1:
            return "", parts[0]
        return "", ""

    # ── Field extractors ─────────────────────────────────────────

    def _extract_date(self, text: str):
        m = _RE_DATE.search(text)
        if m:
            raw = m.group(1)
            for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%-d/%m/%Y"):
                try:
                    return datetime.strptime(raw, fmt)
                except ValueError:
                    continue
        return None

    def _extract_gender(self, text: str):
        m = _RE_GENDER.search(text)
        return m.group(1).capitalize() if m else None

    def _extract_age(self, text: str):
        m = _RE_AGE.search(text)
        if m:
            val = m.group(1) or m.group(2) or m.group(3)
            try:
                return int(val)
            except (ValueError, TypeError):
                pass
        return None

    def _extract_glucose(self, text: str):
        m = _RE_GLUCOSE.search(text)
        return m.group(1).strip() if m else None

    def _extract_cholesterol(self, text: str):
        m = _RE_CHOLESTEROL.search(text)
        return m.group(1).strip() if m else None

    def _extract_hiv(self, text: str):
        m = _RE_HIV.search(text)
        return m.group(1).strip().upper() if m else None

    def _extract_psa(self, text: str):
        m = _RE_PSA.search(text)
        return m.group(1).strip().upper() if m else None

    def _extract_mammo(self, text: str):
        m = _RE_MAMMO.search(text)
        return m.group(1).strip().upper() if m else None

    def _extract_pap_smear(self, text: str):
        m = _RE_PAP_SMEAR.search(text)
        return m.group(1).strip().upper() if m else None
