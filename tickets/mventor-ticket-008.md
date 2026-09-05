# mventor-ticket-008: cards queue sync + lazy preview
- Status: Completed
- Created: 2026-09-03 | Priority: medium | Dependencies: ticket-006 (poll deltas), ticket-007 (toasts fire per sweep)
- Goal: queue merges poll deltas into cards (collapsed by default, state preserved, stale flagged, dismissible); preview bytes load only on expand, once, releasable. Device-independent.
- Scope: `src/modules/cards.py` (card_id, sync_queue, mark_stale, dismiss), `src/modules/preview.py` (ensure_preview, release_preview). No UI toolkit, no cross-module imports.
- Acceptance: [x] deltas merge without dupes, expanded/preview preserved [x] stale flagged, dismiss removes [x] expand×2 → 1 fetch [x] release drops bytes, re-expand re-fetches once [x] empty-fetch raises, stores nothing
- Implementation: queue owns card dicts; bytes live on cards (caller-owned), never module state; app wires expand→ensure_preview, collapse/save→release/dismiss.
- Validation: temp fetch-spy script green (exact fetch counts) + compileall + 14-module sweep.
- Risks: none (pure data + injected fetch; real blob still blocked on downloader ticket).
