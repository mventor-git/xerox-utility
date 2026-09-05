"""Composition root: the ONLY place that wires modules together."""
from __future__ import annotations
from pathlib import Path


def build(cfg_path: Path | None = None, *, state_path: Path | None = None,
          trash_root: Path | None = None, backend=None,
          box_nos: list[int] | None = None, list_box=None) -> dict:
    """Wire everything. Seams (paths/backend/box_nos/list_box) are for tests;
    defaults hit the live device (list-only) and real AppData paths."""
    from src.core import config as cfgmod
    cfg = cfgmod.load_config(cfg_path)
    wm_path = Path(state_path) if state_path else cfgmod.default_watermark_path()
    troot = Path(trash_root) if trash_root else cfgmod.trash_dir(cfg)
    queue: list = []

    def run_once() -> dict:
        from src.core import device_client, watermark as W
        from src.lib.filename_date import extract_ts
        from src.modules import poller, discover, cards, notify
        from src.modules import delete as delmod
        from src.modules import settings as setmod
        base = cfgmod.base_url(cfg)
        first = not wm_path.exists()
        if box_nos is not None:
            boxes = list(box_nos)
        else:
            boxes = [b["no"] for b in discover.discover_boxes(device_client.get_raw_box_page(base))]
        fetch = list_box or (lambda b: poller.fetch_box_docs(base, b, cfg.get("timeout", 10)))
        state = W.load(wm_path)
        fresh, state, errors = poller.poll_once(fetch, boxes, state, extract_ts,
                                                baseline_unseen=first)
        W.save(state, wm_path)
        cards.sync_queue(queue, fresh)
        notified = notify.notify_new_scans(fresh, backend=backend)
        purge_due = delmod.purge_check_due(cfg.get("last_purge_check"),
                                           days=cfg.get("purge_check_days", delmod.PURGE_CHECK_DAYS))
        if purge_due:
            notify.send("Xerox Utility", delmod.purge_message(delmod.count_archived(troot)),
                        backend=backend)
        return {"fresh": fresh, "errors": errors, "notified": notified,
                "purge_due": purge_due, "queue": queue, "problems": setmod.problems(cfg)}

    def run() -> None:
        out = run_once()
        print(f"Xerox Utility: {len(out['fresh'])} new, "
              f"{len(out['errors'])} boxes skipped, purge_due={out['purge_due']}")

    return {"config": cfg, "queue": queue, "run_once": run_once, "run": run}
