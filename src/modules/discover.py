"""Discover all device boxes. Pure function: caller passes raw page text."""
from __future__ import annotations


def discover_boxes(raw_page: str) -> list[dict]:
    from src.lib.parse_box_lst import parse_boxes
    return parse_boxes(raw_page)
