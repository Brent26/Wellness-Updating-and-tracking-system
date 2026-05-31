"""
modules/name_utils.py
Name normalisation and fuzzy matching utilities.
"""

import re
from config import CONFIG

try:
    from thefuzz import fuzz
    _FUZZY_AVAILABLE = True
except ImportError:
    _FUZZY_AVAILABLE = False


def normalise(name):
    """Lowercase, strip punctuation and extra spaces."""
    if not isinstance(name, str):
        return ""
    name = name.lower().strip()
    name = re.sub(r"[^a-z\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def fuzzy_match(norm_name, norm_series, threshold=None):
    """
    Find the best fuzzy match for norm_name in norm_series.
    Returns (index, score) or (None, 0).
    """
    if not _FUZZY_AVAILABLE or not norm_name:
        return None, 0

    threshold = threshold or CONFIG.get("FUZZY_NAME_THRESHOLD", 85)
    best_idx   = None
    best_score = 0

    for idx, candidate in norm_series.items():
        if not candidate:
            continue
        score = fuzz.token_set_ratio(norm_name, candidate)
        if score > best_score:
            best_score = score
            best_idx   = idx

    if best_score >= threshold:
        return best_idx, best_score
    return None, 0


def find_name_in_df(name, df, name_col="Personnel Names", threshold=None):
    """
    Search for name in df[name_col].
    Returns (index, match_type, score) or (None, None, 0).
    match_type: "Exact" or "Fuzzy"
    """
    if not isinstance(name, str) or df.empty:
        return None, None, 0

    norm = normalise(name)

    # Exact match first
    if "_norm" in df.columns:
        exact = df[df["_norm"] == norm]
        if not exact.empty:
            return exact.index[0], "Exact", 100

    # Fuzzy match
    if "_norm" in df.columns and _FUZZY_AVAILABLE:
        idx, score = fuzzy_match(norm, df["_norm"], threshold)
        if idx is not None:
            return idx, "Fuzzy", score

    return None, None, 0