# mventor-ticket-005: trash-archive delete + 30-day purge nudge
- Status: Completed
- Created: 2026-09-03 | Priority: high | Dependencies: ticket-004 (PBDOCRM proven)
- Goal: app NEVER destroys — post-save popup archives device original (TIF) to `%AppData%/Xerox Utility/trash/<box>/` with sidecar, THEN deletes from device; every 30 days nudge user to review/purge trash.
- Scope: `core/config.py` (trash defaults), `modules/delete.py` (archive-then-delete, purge-due). No UI, no notifier change.
- Acceptance: [ ] confirm=False → zero I/O [ ] fetch/archive failure → device delete NEVER called [ ] archive layout `trash/<box>/<fileNo>-<name>.tif + .json` [ ] purge due at 30d, not before [ ] import-sweep + safety checks green
- Implementation: `delete.py` rewritten (archive-then-delete, two-phase, collision suffix, purge-due); `config.py` gains trash_dir/last_purge_check/purge_check_days + resolvers.
- Validation: temp safety script green (confirm=False zero I/O; fetch/empty-blob failure → 0 device deletes; layout + sidecar + sanitize + collision; purge 29d False/30d True; config defaults) + compileall + 14-module import-sweep.
- Risks: trash growth unbounded until user purges — 30d nudge is reminder-only, never auto-purge.
