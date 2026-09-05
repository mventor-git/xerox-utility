"""JSON config in %AppData%/Xerox Utility. Single place for device IP default."""
from __future__ import annotations
import json
import os
from pathlib import Path

DEFAULT_IP = "192.168.1.20"
DEFAULT_TIMEOUT = 10
DEFAULT_POLL_INTERVAL = 120
APP_NAME = "Xerox Utility"
APP_DIR_NAME = APP_NAME
TRASH_DIR_NAME = "trash"
WATERMARK_NAME = "watermark.json"
DEFAULT_PURGE_CHECK_DAYS = 30


def default_config_path() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / APP_DIR_NAME / "config.json"


def default_config() -> dict:
    return {"ip": DEFAULT_IP, "timeout": DEFAULT_TIMEOUT, "box": 1, "store_dir": "",
            "trash_dir": "", "last_purge_check": "", "purge_check_days": DEFAULT_PURGE_CHECK_DAYS,
            "poll_interval": DEFAULT_POLL_INTERVAL}


def load_config(path: Path | None = None) -> dict:
    p = path or default_config_path()
    if not p.exists():
        return default_config()
    try:
        return {**default_config(), **json.loads(p.read_text(encoding="utf-8"))}
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"unreadable config {p}: {exc}") from exc


def save_config(cfg: dict, path: Path | None = None) -> Path:
    p = path or default_config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return p


def base_url(cfg: dict) -> str:
    return url_for_ip((cfg.get("ip") or DEFAULT_IP).strip())


def url_for_ip(ip: str) -> str:
    """Single place that turns an address into a device URL."""
    if not (ip or "").strip():
        raise ValueError("empty device IP")
    return f"http://{ip.strip()}"


def default_store_dir() -> Path:
    return Path.home() / APP_DIR_NAME


def store_dir(cfg: dict) -> Path:
    override = (cfg.get("store_dir") or "").strip()
    return Path(override) if override else default_store_dir()


def default_trash_dir() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / APP_DIR_NAME / TRASH_DIR_NAME


def trash_dir(cfg: dict) -> Path:
    override = (cfg.get("trash_dir") or "").strip()
    return Path(override) if override else default_trash_dir()


def default_watermark_path() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / APP_DIR_NAME / WATERMARK_NAME
