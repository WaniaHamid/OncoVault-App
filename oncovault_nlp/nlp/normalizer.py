import re
from typing import Optional

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()

KNOWN_UNITS = {
    "k/ul": "k/uL",
    "k/microl": "k/uL",
    "10^3/ul": "k/uL",
    "10^9/l": "k/uL",
    "thousand/ul": "k/uL",
    "thou/ul": "k/uL",
    "k": "k/uL",
    "g/dl": "g/dL",
    "gm/dl": "g/dL",
    "m/ul": "M/uL",
    "mil/ul": "M/uL",
    "10^6/ul": "M/uL",
    "%": "%",
    "percent": "%",
    "pct": "%",
    "fl": "fL",
}

def clean_unit(unit_str: Optional[str]) -> Optional[str]:
    if not unit_str:
        return None
    u = unit_str.strip().lower()
    return KNOWN_UNITS.get(u, None)
