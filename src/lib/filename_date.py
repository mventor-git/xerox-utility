"""Filename dates.

Legacy: trailing `YYMMDDHHMMSS`, e.g. `...-8107-260903091730`.
Live (5325, probe 2026-09-03): `img-MDDHHMMSS`, e.g. `img-903091643`
= Sept 3, 09:16:43 (device omits year; device `date` column is authoritative).
"""
from __future__ import annotations
import re
from datetime import datetime

TS_RE = re.compile(r"(\d{12})\b")
IMG_RE = re.compile(r"img-(\d{9,10})\b")


def extract_ts(filename: str) -> str:
    """12-digit TS preferred, else img- short TS, else ''."""
    found = TS_RE.findall(filename or "")
    if found:
        return found[-1]
    m = IMG_RE.search(filename or "")
    return m.group(1) if m else ""


def extract_datetime(filename: str, year: int | None = None) -> datetime | None:
    """12-digit → datetime. Short img- TS needs `year` (device omits it)."""
    ts = extract_ts(filename)
    if not ts:
        return None
    try:
        if len(ts) == 12:
            return datetime.strptime(ts, "%y%m%d%H%M%S")
        if year is not None and len(ts) in (9, 10):
            head = ts[:-6]
            month, day = (int(head[0]), int(head[1:])) if len(ts) == 9 else (int(head[:2]), int(head[2:]))
            return datetime(int(year), month, day, int(ts[-6:-4]), int(ts[-4:-2]), int(ts[-2:]))
    except ValueError:
        return None
    return None


DEVICE_DATE_FMT = "%d/%m/%Y %I:%M %p"  # e.g. '03/09/2026 09:17 AM'


def parse_device_date(text: str) -> datetime:
    """Device `date` column → datetime. Raises ValueError on garbage (caller counts skips)."""
    return datetime.strptime((text or "").strip(), DEVICE_DATE_FMT)
