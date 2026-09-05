"""Settings model: device IP + checker, store/trash folders, purge-check record."""
from __future__ import annotations


def current_settings(cfg: dict) -> dict:
    return {"ip": cfg.get("ip", ""), "timeout": cfg.get("timeout", 10),
            "box": cfg.get("box", 1), "store_dir": cfg.get("store_dir", ""),
            "trash_dir": cfg.get("trash_dir", ""), "purge_check_days": cfg.get("purge_check_days", 30)}


def apply_settings(cfg: dict, ip: str | None = None, store_dir: str | None = None,
                   trash_dir: str | None = None, box: int | str | None = None) -> dict:
    if ip is not None:
        ip = ip.strip()
        if not ip:
            raise ValueError("IP must not be empty")
        cfg["ip"] = ip
    if store_dir is not None:
        cfg["store_dir"] = store_dir
    if trash_dir is not None:
        cfg["trash_dir"] = trash_dir
    if box is not None:
        try:
            box = int(box)
        except (TypeError, ValueError):
            raise ValueError("box must be a number (0 = all boxes)")
        if box < 0:
            raise ValueError("box must be 0 or higher")
        cfg["box"] = box
    return cfg


def record_purge_check(cfg: dict, today: str | None = None) -> dict:
    """Stamp the trash review as done today. Caller persists cfg."""
    from datetime import date
    stamp = today or date.today().isoformat()
    date.fromisoformat(stamp)  # fail loudly on bad stamp
    cfg["last_purge_check"] = stamp
    return cfg


def problems(cfg: dict) -> list[str]:
    """Human hints for the settings screen. Empty = healthy."""
    from src.core.config import APP_DIR_NAME
    out = []
    if not (cfg.get("ip") or "").strip():
        out.append("device IP is empty")
    if not (cfg.get("store_dir") or "").strip():
        out.append(f"no store folder — files fall back to ~/{APP_DIR_NAME}")
    return out


def check_device(base_url: str, get_page) -> bool:
    """get_page(base_url) injected; True iff device answers with var box."""
    try:
        return "var box" in get_page(base_url)
    except Exception:
        return False
