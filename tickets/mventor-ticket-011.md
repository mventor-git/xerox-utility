# mventor-ticket-011: device reduced to Box 1 — verify + sync docs
- Status: Completed
- Created: 2026-09-03 | Priority: high | Dependencies: ticket-010 (run_once)
- Goal: confirm live device shows only Box 1 and app runs clean against it; retire multi-box flakiness rows.
- Scope: read-only verify (discover + run_once temp-state) + docs. No code change expected (skip logic stays as safety net).
- Acceptance: [x] discover == [1] [x] box1 lists 200 (16 docs, newest 8091) [x] run_once fresh 0, errors {} [x] contract/issues/backlog single-box current
- Implementation: docs-only. Live: boxes [(1,'Scans')]; run_once clean, zero skips; census 16 docs / newest 8091 (unchanged).
- Validation: temp live scripts (temp state, fake backend); compileall unaffected (no code touched).
- Risks: none. Old per-box flakiness retired with the deleted boxes; skip logic retained.