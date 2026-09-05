"""Safe delete: app NEVER destroys. Archive original (TIF) to trash, THEN remove from device.

Layout: `<trash>/<box>/<fileNo>-<safe name>.tif` + `.json` sidecar
`{box,file_no,name,date,pages,kind,deleted_at}`.
Flow: post-save popup → confirm → fetch blob → archive ALL → delete ALL.
Any archive failure aborts before ANY device delete. Purge is manual only;
app nudges review every 30 days (`purge_check_due`), never auto-purges.
"""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path

PURGE_CHECK_DAYS = 30


def candidates_for_delete(saved_ok: list[dict]) -> list[dict]:
    return [dict(it, _delete_ok=True) for it in saved_ok]


def confirm_delete_text(items: list[dict]) -> str:
    names = "\n".join(f"Box {it.get('box')}: {it.get('name')}" for it in items)
    return (f"Move from device to app trash?\n{names}\n"
            f"Originals stay recoverable in trash; review purge every {PURGE_CHECK_DAYS} days.")


def trash_box_dir(trash_root: str | Path, box: int) -> Path:
    return Path(trash_root) / str(int(box))


def archive_path(trash_root: str | Path, item: dict) -> Path:
    safe = "".join(c if c.isalnum() or c in "._- " else "_" for c in item.get("name", "scan"))
    base = trash_box_dir(trash_root, item.get("box", 0)) / f"{item.get('file_no')}-{safe}"
    if base.with_suffix(".tif").exists():
        i = 2
        while (base.parent / f"{base.name}-{i}.tif").exists():
            i += 1
        base = base.parent / f"{base.name}-{i}"
    return base


def archive_doc(blob: bytes, trash_root: str | Path, item: dict, deleted_at: str | None = None) -> Path:
    """Write blob + sidecar. Raises on empty blob or I/O error — caller must NOT delete then."""
    if not blob:
        raise RuntimeError(f"refusing to archive empty blob for {item.get('box')}:{item.get('file_no')}")
    dest = archive_path(trash_root, item).with_suffix(".tif")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)
    dest.with_suffix(".json").write_text(json.dumps({
        "box": item.get("box"), "file_no": item.get("file_no"), "name": item.get("name"),
        "date": item.get("date"), "pages": item.get("pages"), "kind": item.get("kind"),
        "deleted_at": deleted_at or today_iso(),
    }, indent=2), encoding="utf-8")
    return dest


def archive_and_delete(items: list[dict], confirmed: bool, fetch, trash_root: str | Path,
                       do_delete) -> list[Path]:
    """Two phases: archive every item first, delete from device only after ALL archived."""
    if not confirmed or not items:
        return []
    archived = [archive_doc(fetch(it), trash_root, it) for it in items]
    for it in items:
        do_delete(it)
    return archived


def today_iso() -> str:
    return date.today().isoformat()


def purge_check_due(last_check: str | None, days: int = PURGE_CHECK_DAYS,
                    today: date | None = None) -> bool:
    """True when a trash-review nudge is owed. Fail-open (bad/empty stamp → due)."""
    if not last_check:
        return True
    try:
        last = date.fromisoformat(last_check)
    except ValueError:
        return True
    return ((today or date.today()) - last).days >= days


def nudge_due(cfg: dict, today: str | None = None) -> bool:
    """One nudge per day, only while a review is actually owed."""
    now = today or date.today().isoformat()
    if cfg.get("last_purge_nudge") == now:
        return False
    return purge_check_due(cfg.get("last_purge_check"),
                           days=int(cfg.get("purge_check_days", PURGE_CHECK_DAYS)),
                           today=date.fromisoformat(now))


def stamp_nudge(cfg: dict, today: str | None = None) -> dict:
    """Remember today's nudge so it fires once. Caller persists cfg."""
    stamp = today or date.today().isoformat()
    date.fromisoformat(stamp)  # fail loudly on bad stamp
    cfg["last_purge_nudge"] = stamp
    return cfg


def purge_message(n_archived: int) -> str:
    return (f"App trash holds {n_archived} archived scan(s). "
            f"Review and purge what you no longer need — nothing is deleted automatically.")


def count_archived(trash_root: str | Path) -> int:
    """How many originals sit in trash. Missing trash = 0, never an error."""
    root = Path(trash_root)
    if not root.exists():
        return 0
    return sum(1 for p in root.rglob("*.tif") if p.is_file())
