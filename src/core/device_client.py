"""Sync device HTTP client. Read-only except explicit delete path.

Locked by live probe (see docs/cache/device_contract.md for addresses):
- PROVEN: GET scpblst.htm, POST PBDOCLST.cmd (list).
- SHAPE-KNOWN, blob UNPROVEN: GET PBDOCLNK.cmd (retrieve; direct calls → 503
  REQUEST: ERROR, needs browser-flow session; see downloader ticket).
- SHAPE-KNOWN, never auto-called: POST PBDOCRM.cmd (per-doc delete, confirm-only).
"""
from __future__ import annotations

LIST_PATH = "/scpblst.htm"
DOC_LIST_CMD = "/PBDOCLST.cmd"
RETRIEVE_PATH = "/PBDOCLNK.cmd"   # GET; shape-known, blob unproven (503)
DELETE_PATH = "/PBDOCRM.cmd"      # POST; confirm-only, never auto-called
CHARSET = "windows-1252"
RETRIEVE_FORMS = ("TIFJPG", "PDF")  # device `var formOpt`


def _requests():
    try:
        import requests  # local import: keeps module import-safe without deps
    except ImportError as exc:
        raise RuntimeError("missing dependency: pip install -r requirements.txt") from exc
    return requests


def get_raw_box_page(base_url: str, timeout: int = 10) -> str:
    r = _requests().get(base_url.rstrip("/") + LIST_PATH, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"device GET {LIST_PATH} -> HTTP {r.status_code}")
    return r.content.decode(CHARSET, errors="replace")


def post_raw_doc_list(base_url: str, box: int, page: int = 1, per_page: int = 100,
                      timeout: int = 10) -> str:
    payload = {"BOX": int(box), "ORD": "DD", "SET": 1, "LTOP": "", "LNUM": per_page, "PAGE": page}
    r = _requests().post(base_url.rstrip("/") + DOC_LIST_CMD, data=payload, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"device POST {DOC_LIST_CMD} BOX={box} -> HTTP {r.status_code}")
    return r.content.decode(CHARSET, errors="replace")


def fetch_blob(url: str, timeout: int = 30) -> bytes:
    """Full-file download. Called only lazily (expand/click), never by poller."""
    r = _requests().get(url, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"device download -> HTTP {r.status_code} ({url})")
    return r.content


def retrieve_params(box: int, pwd: str, doc: int, form: str = "PDF") -> dict:
    """Pure builder for GET PBDOCLNK.cmd (device-exact field set).

    DOC is slash-joined (`8025/`); multi-select joins more (`8025/8026/`).
    PWD is the session token from PBDOCLST `var box=[n,pwd,...]`.
    Blob fetch currently 503s outside browser flow — callers must fail loudly.
    """
    if form not in RETRIEVE_FORMS:
        raise ValueError(f"FORM must be one of {RETRIEVE_FORMS}")
    return {"BOX": int(box), "PWD": pwd, "ORD": "DD", "DGACNT": "", "GACNT": "",
            "ACNTUID": "", "DOC": f"{int(doc)}/", "FORM": form, "PAGE": "",
            "SMNL": 0, "HCMP": 0, "ICMP": 0, "OCR": 0, "LANG": 0, "TCMP": 0}


def build_retrieve_url(base_url: str, params: dict) -> str:
    from urllib.parse import urlencode
    return base_url.rstrip("/") + RETRIEVE_PATH + "?" + urlencode(params)


def delete_payload(box: int, pwd: str, doc: int) -> dict:
    """Pure builder for POST PBDOCRM.cmd. Send ONLY after explicit user confirm."""
    return {"BOX": int(box), "PWD": pwd, "ORD": "DD", "DOC": f"{int(doc)}/"}
