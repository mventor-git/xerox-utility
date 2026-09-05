"""Find ANY device docs in a date range. Listing only — blobs stay lazy."""
from __future__ import annotations
from datetime import date


def filter_docs(docs: list[dict], day_from: date, day_to: date) -> tuple[list[dict], int]:
    """Docs whose device date falls on [day_from, day_to] (inclusive).
    Returns (matches, skipped) — unparseable rows are counted, never silent."""
    from src.lib.filename_date import parse_device_date
    hits: list[dict] = []
    skipped = 0
    for doc in docs:
        try:
            day = parse_device_date(doc.get("date", "")).date()
        except ValueError:
            skipped += 1
            continue
        if day_from <= day <= day_to:
            hits.append(doc)
    hits.sort(key=lambda d: (d.get("file_no", 0)))
    return hits, skipped


def find_docs(base_url: str, boxes: list[int], day_from: date, day_to: date,
              timeout: int = 10) -> tuple[list[dict], dict]:
    """List boxes, filter by range. Returns (items with 'box' set, {'skipped': n, 'errors': {}}).
    Boxes that fail are recorded in errors (same mercy rule as the poller)."""
    from src.core import device_client
    from src.lib.parse_box_lst import parse_doc_list
    items: list[dict] = []
    skipped = 0
    errors: dict = {}
    for box in boxes:
        try:
            raw = device_client.post_raw_doc_list(base_url, int(box), timeout=timeout)
            docs = parse_doc_list(raw)
        except Exception as exc:
            errors[str(box)] = f"{type(exc).__name__}: {exc}"
            continue
        hits, skip = filter_docs(docs, day_from, day_to)
        skipped += skip
        items.extend({"box": int(box), **d} for d in hits)
    return items, {"skipped": skipped, "errors": errors}
