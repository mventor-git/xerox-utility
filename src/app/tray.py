"""Tray entry. Keeps UI toolkit import lazy so `src` imports headless."""
from __future__ import annotations


def main() -> int:
    from src.app.composition import build
    app = build()
    app["run"]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
