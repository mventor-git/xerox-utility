"""Save/convert: user picks name+format → file on disk.

- .pdf: img2pdf (multipage fidelity) with Pillow save_all fallback.
- .png/.jpg: Pillow still of page 1 (documented; stills have no pages).
- .tif/.tiff: byte-identical passthrough (device original).
Unknown formats and empty blobs fail loudly. Converters lazy-imported.
"""
from __future__ import annotations
from pathlib import Path

SUPPORTED = (".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff")


def dest_path(store_dir: str | Path, item: dict, ext: str) -> Path:
    base = Path(store_dir) if str(store_dir) else Path.home() / "Xerox Utility"
    safe = "".join(c if c.isalnum() or c in "._- " else "_" for c in item.get("name", "scan"))
    return base / f"{safe}{ext if ext.startswith('.') else '.' + ext}"


def _check(blob: bytes, ext: str) -> str:
    if not blob:
        raise RuntimeError("refusing to convert empty blob")
    norm = ext.lower() if ext.startswith(".") else "." + ext.lower()
    if norm not in SUPPORTED:
        raise ValueError(f"unsupported format {ext!r}; use one of {SUPPORTED}")
    return norm


def _frames(blob: bytes) -> list:
    """All TIFF pages as PIL images. Raises loudly when nothing decodes."""
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(blob))
    out = []
    try:
        while True:
            out.append(img.copy())
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    if not out:
        raise RuntimeError("no decodable pages in blob")
    return out


def _pdf_via_pillow(blob: bytes, out: Path) -> Path:
    pages = [f.convert("RGB") for f in _frames(blob)]
    pages[0].save(out, save_all=True, append_images=pages[1:])
    return out


def convert_blob(blob: bytes, ext: str, out: Path) -> Path:
    """Convert blob to ext at out (parents created). Returns out."""
    norm = _check(blob, ext)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if norm in (".tif", ".tiff"):
        out.write_bytes(blob)
        return out
    if norm == ".pdf":
        try:
            import img2pdf
            out.write_bytes(img2pdf.convert(blob))
            return out
        except ImportError:
            return _pdf_via_pillow(blob, out)
    page = _frames(blob)[0]
    if norm in (".jpg", ".jpeg") and page.mode in ("RGBA", "LA", "P"):
        page = page.convert("RGB")
    page.save(out)
    return out
