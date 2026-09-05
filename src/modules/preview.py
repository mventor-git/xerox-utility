"""Lazy preview: full TIFF bytes only on expand/click. Bytes live on the card dict (caller-owned), never in module state."""
from __future__ import annotations


def preview_path_hint(item: dict) -> str:
    return f"box{item.get('box')}/{item.get('file_no')}-{item.get('name')}"


def load_preview(item: dict, fetch) -> bytes:
    """fetch(item) injected by app composition; raises loudly on failure."""
    data = fetch(item)
    if not data:
        raise RuntimeError(f"empty preview for {preview_path_hint(item)}")
    return data


def ensure_preview(card: dict, fetch) -> dict:
    """Load bytes into card['preview'] once; later expands reuse them (fetch-count proof)."""
    if card.get("preview") is None:
        card["preview"] = load_preview(card["item"], fetch)
    return card


def release_preview(card: dict) -> dict:
    """Drop bytes after collapse/save to free memory; next expand re-fetches."""
    card.pop("preview", None)
    return card
