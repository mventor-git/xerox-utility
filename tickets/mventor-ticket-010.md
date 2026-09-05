# mventor-ticket-010: settings model + app composition run_once
- Status: Completed
- Created: 2026-09-03 | Priority: medium | Dependencies: tickets 005-008 (all modules feed it)
- Goal: `build()` wires poll→cards→notify→purge into one headless `run_once()` with seams for tests; settings gains purge-check record + problem hints.
- Scope: `src/app/composition.py` (rewrite), `src/modules/settings.py` (+record/problems/trash), `src/modules/delete.py` (+count_archived). Tray GUI stays deferred.
- Acceptance: [x] fake: baseline→0, repeat→0, new-doc→1 + card + 1 toast [x] purge_due fires purge text via same backend [x] live read-only run_once clean under 3 device states [x] settings record/problems/count asserts [x] sweep green
- Implementation: run_once (first-run baseline, sync, notify, purge nudge, problems); settings record_purge_check/problems/trash fields; delete.count_archived.
- Validation: fake-seam script green + 3 live runs (skips {3-6}, then {2-7}, then {} — device flaky, composition stable throughout) + sweep. Zero real toasts, zero PC state (temp paths).
- Risks: device mailbox service flaky post-restart (not password-specific — varies run to run); skip+record absorbs it; retry/backoff filed as backlog.
