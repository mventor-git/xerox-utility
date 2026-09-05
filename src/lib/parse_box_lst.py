"""Parse `var box` / `var lst` with regex. Input is windows-1252 decoded text."""
from __future__ import annotations
import re

BOX_RE = re.compile(r"var\s+box\s*=\s*\[(.*?)\]\s*;", re.S)
LST_RE = re.compile(r"var\s+lst\s*=\s*\[(.*?)\]\s*;", re.S)
ROW_RE = re.compile(r"\[(.*?)\]", re.S)
CELL_RE = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"|([^,\]]+)")


def _cells(row: str) -> list[str]:
    out: list[str] = []
    for m in CELL_RE.finditer(row):
        sq, dq, raw = m.group(1), m.group(2), m.group(3)
        out.append(sq if sq is not None else (dq if dq is not None else (raw or "").strip()))
    return out


def _rows(inner: str) -> list[list[str]]:
    return [_cells(m.group(1)) for m in ROW_RE.finditer(inner)]


def parse_boxes(text: str) -> list[dict]:
    """From scpblst.htm `var box=[[n,name...]]`. Returns [{no, name}]."""
    m = BOX_RE.search(text)
    if not m:
        raise ValueError("var box not found in device page")
    boxes = []
    for cells in _rows(m.group(1)):
        if not cells:
            continue
        try:
            no = int(cells[0].strip())
        except ValueError:
            continue
        boxes.append({"no": no, "name": cells[1] if len(cells) > 1 else f"Box {no}"})
    return boxes


def parse_doc_list(text: str) -> list[dict]:
    """From PBDOCLST `var lst`.

    Live (5325, probe 2026-09-03): 9 cells
    `[fileNo,dateStr,pages,?,kind,name,0,0,0]`, e.g.
    `[8107,'03/09/2026 09:17 AM',3,2,2,'img-903091643',0,0,0]`.
    Legacy 5-cell `[fileNo,dateStr,pages,kind,name]` still accepted.
    """
    m = LST_RE.search(text)
    if not m:
        raise ValueError("var lst not found in device response")
    docs = []
    for cells in _rows(m.group(1)):
        try:
            file_no = int(cells[0].strip())
        except (ValueError, IndexError):
            continue
        if len(cells) >= 6:
            kind, name = cells[4].strip(), cells[5].strip()
        elif len(cells) >= 5:
            kind, name = cells[3].strip(), cells[4].strip()
        else:
            continue
        docs.append({
            "file_no": file_no, "date": cells[1].strip(), "pages": cells[2].strip(),
            "kind": kind, "name": name,
        })
    return docs
