# mventor-ticket-009: save/convert (TIFF multipage→PDF, PNG/JPG, TIF passthrough)
- Status: Completed
- Created: 2026-09-03 | Priority: medium | Dependencies: ticket-008 (cards feed save flow)
- Goal: user picks name+format → converted file on disk; multipage fidelity via img2pdf, Pillow fallback; unknown formats and empty blobs fail loudly. Device-independent.
- Scope: `src/modules/save_convert.py` only. Deps (Pillow 12.2 present, img2pdf 0.6.3 + pypdf 6.16.2 installed as declared).
- Acceptance: [x] 2-page TIFF→PDF keeps 2 pages (img2pdf + fallback) [x] PNG/JPG valid stills [x] TIF byte-identical passthrough [x] bad ext + empty blob raise [x] import-sweep green
- Implementation: SUPPORTED guard; img2pdf.convert proven to take raw bytes; Pillow save_all fallback; JPEG RGB-convert; TIF passthrough. Stills = page 1 by design.
- Validation: temp 2-page-TIFF script green (pypdf page counts, still sizes, passthrough bytes, guards) + compileall + 14-module sweep.
- Risks: device color modes vary — _frames fails loudly on undecodable blobs; helper-exe pip quirk harmless (libs import).
