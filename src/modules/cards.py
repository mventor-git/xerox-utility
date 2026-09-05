"""Queue/cards model: small card -> expanded on click. No UI toolkit here."""
from __future__ import annotations


def card_id(item: dict) -> str:
    return f"{item.get('box')}:{item.get('file_no')}"


def build_cards(items: list[dict]) -> list[dict]:
    return [{
        "id": card_id(it),
        "title": it.get("name", ""),
        "subtitle": f"Box {it.get('box')} · {it.get('date')} · {it.get('pages')}p",
        "expanded": False, "item": it,
    } for it in items]


def expand(cards: list[dict], card_id: str) -> list[dict]:
    for c in cards:
        c["expanded"] = (c["id"] == card_id)
    return cards


def sync_queue(cards: list[dict], items: list[dict]) -> list[dict]:
    """Merge poll deltas: new ids append collapsed; existing cards keep state."""
    known = {c["id"] for c in cards}
    cards.extend(c for c in build_cards(items) if c["id"] not in known)
    return cards


def mark_stale(cards: list[dict], active_ids: set[str]) -> list[dict]:
    """Flag cards whose docs vanished from the device (deleted elsewhere)."""
    for c in cards:
        c["_stale"] = c["id"] not in active_ids
    return cards


def dismiss(cards: list[dict], card_id: str) -> list[dict]:
    """Remove one card. Use after save+archive, or user discard."""
    return [c for c in cards if c["id"] != card_id]
