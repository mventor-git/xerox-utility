# mventor-ticket-006: discover + poller + watermark differ (BACKLOG#2)
- Status: Completed
- Created: 2026-09-03 | Priority: high | Dependencies: ticket-003/004 (list proven)
- Goal: working poll sweep — discover boxes, list each, watermark-differ, first-run baseline ignores old files.
- Scope: `modules/poller.py` (fetch_box_docs, baseline flag, poll_all, per-box skip), `core/config.py` (watermark path). List-POST only, read-only.
- Acceptance: [x] live Box1 = 16 docs (8091 newest, 8107 gone) [x] baseline → 0 fresh, watermarks recorded [x] 2nd run → 0 fresh [x] catch-up unseen box → 16 docs [x] watermark roundtrip [x] locked boxes 3-6 skipped, recorded, sweep survives
- Implementation: poll_once returns (fresh, state, errors); per-box try/except; all-fail → loud raise; empty-box sentinel; live run found boxes 3-6 → 503 (likely password-locked), box7 = 1 doc, box2 empty.
- Validation: compileall + import-sweep OK; fault-tolerance unit OK (skip/raise/empty); LIVE POLL OK after machine restart (earlier 503 was device service down).
- Risks: boxes 3-6 unwatched until per-box PWD auth exists → BACKLOG item filed.
