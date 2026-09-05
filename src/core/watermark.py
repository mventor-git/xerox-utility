"""Per-box watermark: remember last seen (fileNo, date, filename TS)."""
from __future__ import annotations
import json
from pathlib import Path

State = dict  # {box_no: {"file_no": int, "date": str, "ts": str}}


def load(path: Path) -> State:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"unreadable watermark {path}: {exc}") from exc


def save(state: State, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def entry_key(file_no: int, date: str, ts: str) -> tuple:
    return (int(file_no), str(date), str(ts))


def is_new(box_no: str, file_no: int, date: str, ts: str, state: State) -> bool:
    prev = state.get(str(box_no))
    if prev is None:
        return True  # first sighting of box; caller decides bulk-ignore on first run
    return entry_key(file_no, date, ts) > (
        int(prev.get("file_no", -1)),
        str(prev.get("date", "")),
        str(prev.get("ts", "")),
    )


def update(box_no: str, file_no: int, date: str, ts: str, state: State) -> State:
    if is_new(box_no, file_no, date, ts, state) or str(box_no) not in state:
        state[str(box_no)] = {"file_no": int(file_no), "date": date, "ts": ts}
    return state
