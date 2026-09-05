# mventor-ticket-007: notifier — batched toasts + backend selection
- Status: Completed
- Created: 2026-09-03 | Priority: high | Dependencies: ticket-006 (poll items feed toasts)
- Goal: `notify` batches scans into toast-limit-friendly summaries via injectable backend; real Win backend proven by import (no popup spam in validation).
- Scope: `src/modules/notify.py`, `requirements.txt` (+windows-toasts, win10toast dropped as dead). No tray icon yet (composition ticket).
- Acceptance: [x] 0/1/3/5-item formatting incl. multi-box grouping [x] backend injection records exact calls [x] select_backend probes without side effects [x] windows-toasts installed + import-safe [x] import-sweep green
- Implementation: summarize (1→detail, ≤3→lines, else per-box counts) + send/select_backend with lazy windows-toasts import; purge text composed by callers (no cross-module import). Dep review: necessary/single-purpose/maintained; installed 1.3.1 (helper-exe file-lock ignored, package imports fine).
- Validation: temp fake-backend script green (batching, routing, real backend detected, zero toasts fired) + compileall + 14-module sweep.
- Risks: Win-version toast quirks surface in tray ticket; real toast pop deferred to UI wiring.
