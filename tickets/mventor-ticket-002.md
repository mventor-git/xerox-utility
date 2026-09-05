# mventor-ticket-002: scaffold src layout
- Status: Completed
- Created: 2026-09-03 | Priority: high | Dependencies: ticket-001 (done)
- Goal: create `src/` skeleton per `profile.md` with explicit, import-safe stubs.
- Scope: `src/app/`, `src/core/`, `src/lib/`, `src/modules/`, `requirements.txt`, `.gitignore`. No device probe, no real download/delete logic.
- Acceptance: [x] dirs match profile [x] every module imports cleanly [x] no hardcoded IP [x] no cross-module imports [x] `profile.md`/`.muse` untouched
- Implementation: 22 files — core (config/watermark/device_client), lib (parse_box_lst/filename_date), 8 modules, app (tray/composition). Lazy/guarded 3rd-party imports; IP default only in `core/config.py`.
- Validation: compileall OK; import-sweep OK (14 modules); synthetic smoke OK (parse box/lst, TS `260903091730`→`2026-09-03 09:17:30`, poll_once watermark). Grep: IP in 1 file (config), 0 cross-module imports.
- Risks: UI toolkit not chosen (imports lazy); retrieve/delete `.cmd` still open → BACKLOG#1.
