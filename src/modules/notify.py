"""Notifier: Win toast + tray. Shows which folder (box) was used.

Batching respects toast limits: 1 scan → detail toast; a few → lines;
many → per-box counts. Backend injectable for tests; default = best
available. Callers compose texts (app wires e.g. delete.purge_message).
"""
from __future__ import annotations
from typing import Callable

from src.core.config import APP_NAME as APP_TITLE
DETAIL_LIMIT = 3


def format_message(item: dict) -> str:
    return f"Box {item.get('box')}: {item.get('name')} ({item.get('pages')}p)"


def summarize(items: list[dict]) -> tuple[str, str] | None:
    """(title, body) for a batch, or None when empty."""
    if not items:
        return None
    if len(items) == 1:
        return APP_TITLE, "New scan — " + format_message(items[0])
    if len(items) <= DETAIL_LIMIT:
        return f"{APP_TITLE} — {len(items)} new scans", "\n".join(format_message(it) for it in items)
    counts: dict = {}
    for it in items:
        counts[it.get("box")] = counts.get(it.get("box"), 0) + 1
    lines = [f"Box {b} ×{c}" for b, c in sorted(counts.items(), key=lambda kv: kv[0])]
    return f"{APP_TITLE} — {len(items)} new scans", "\n".join(lines)


def select_backend() -> str:
    """Best available backend name. Side-effect free (import probe only)."""
    try:
        import windows_toasts  # noqa: F401
        return "windows-toasts"
    except ImportError:
        return "print"


def _toast_backend(title: str, message: str) -> str:
    from windows_toasts import Toast, WindowsToaster  # lazy: stays import-safe without dep
    toast = Toast()
    toast.text_fields = [title, message]
    WindowsToaster(APP_TITLE).show_toast(toast)
    return "windows-toasts"


def _print_backend(title: str, message: str) -> str:
    print(f"[{title}] {message}")
    return "print"


def send(title: str, message: str, backend: str | Callable | None = None) -> str:
    """Deliver one notification. backend: name, callable, or None (auto). Returns backend used."""
    if backend is None:
        backend = select_backend()
    if callable(backend):
        return backend(title, message)
    if backend == "windows-toasts":
        return _toast_backend(title, message)
    return _print_backend(title, message)


def notify_new_scans(items: list[dict], backend: str | Callable | None = None) -> int:
    """Batch-notify new scans. Returns item count. Fires zero toasts when empty."""
    summary = summarize(items)
    if summary is None:
        return 0
    send(*summary, backend=backend)
    return len(items)
