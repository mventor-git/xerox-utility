"""Tray entry. GUI first; headless machines fall back to one quiet sweep."""
from __future__ import annotations


def main() -> int:
    from src.app.composition import build
    app = build()
    try:
        from src.app.gui import launch
        launch(app)
    except Exception as exc:
        print(f"GUI unavailable ({exc}); running one headless sweep instead.")
        app["run"]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
