"""Tray entry. GUI first; headless machines fall back to one quiet sweep.

Flags: --minimized  start parked in the tray (used by the autostart shortcut).
"""
from __future__ import annotations
import sys


def main(argv: list[str] | None = None) -> int:
    from src.app.composition import build
    hidden = "--minimized" in (argv if argv is not None else sys.argv[1:])
    app = build()
    try:
        from src.app.gui import launch
        launch(app, start_hidden=hidden)
    except Exception as exc:
        print(f"GUI unavailable ({exc}); running one headless sweep instead.")
        app["run"]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
