"""Poller: list/metadata only, never full download. Differ via watermark."""
from __future__ import annotations
from typing import Callable


def fetch_box_docs(base_url: str, box_no: int, timeout: int = 10) -> list[dict]:
    """List one box: POST PBDOCLST + parse. No blob download."""
    from src.core import device_client
    from src.lib.parse_box_lst import parse_doc_list
    raw = device_client.post_raw_doc_list(base_url, int(box_no), timeout=timeout)
    return parse_doc_list(raw)


def poll_once(list_box: Callable[[int], list[dict]], boxes: list[int],
              state: dict, ts_of, *, baseline_unseen: bool = False
              ) -> tuple[list[dict], dict, dict]:
    """One sweep. Returns (new_items, updated_state, errors).

    A failing box is skipped (recorded in errors) so one locked box never
    blinds the others. If EVERY box fails, raises — device is down, say so loudly.
    baseline_unseen=True records unseen boxes' watermarks WITHOUT reporting —
    first run ignores files already sitting on the device.
    """
    from src.core.watermark import is_new, update
    fresh: list[dict] = []
    errors: dict = {}
    for box in boxes:
        try:
            docs = list_box(int(box))
        except Exception as exc:
            errors[str(box)] = f"{type(exc).__name__}: {exc}"
            continue
        if baseline_unseen and str(box) not in state:
            if docs:
                latest = max(docs, key=lambda d: (d["file_no"], d["date"], ts_of(d.get("name", ""))))
                update(box, latest["file_no"], latest["date"], ts_of(latest.get("name", "")), state)
            else:
                update(box, 0, "", "", state)  # empty box sentinel: later arrivals still report as new
            continue
        for doc in docs:
            ts = ts_of(doc.get("name", ""))
            if is_new(box, doc["file_no"], doc["date"], ts, state):
                fresh.append({"box": int(box), **doc, "ts": ts})
        box_fresh = [d for d in fresh if d["box"] == int(box)]
        if box_fresh:
            latest = max(box_fresh, key=lambda d: (d["file_no"], d["date"], d["ts"]))
            update(box, latest["file_no"], latest["date"], latest["ts"], state)
    if boxes and len(errors) == len(boxes):
        raise RuntimeError(f"all {len(boxes)} boxes failed; first: {next(iter(errors.values()))}")
    return fresh, state, errors


def poll_all(base_url: str, boxes: list[int], state: dict, timeout: int = 10,
             *, baseline_unseen: bool = False) -> tuple[list[dict], dict, dict]:
    """Full sweep over device boxes. List-only. Returns (new_items, updated_state, errors)."""
    from src.lib.filename_date import extract_ts
    return poll_once(lambda b: fetch_box_docs(base_url, b, timeout),
                     boxes, state, extract_ts, baseline_unseen=baseline_unseen)
