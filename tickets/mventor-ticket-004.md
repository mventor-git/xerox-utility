# mventor-ticket-004: user-confirmed single-file delete (Box1/DOC 8107)
- Status: Completed
- Created: 2026-09-03 | Priority: high | Dependencies: ticket-003 (delete shape locked)
- Goal: delete ONLY file 8107 in Box 1 (Scans) per explicit user request; prove PBDOCRM path.
- Scope: 1× fresh list (verify-before) + 1× POST PBDOCRM.cmd {BOX:1,PWD:fresh,ORD:DD,DOC:8107/} + 1× list (verify-after). No other docs, no boxes.
- Acceptance: [x] 8107 present before [x] single-DOC payload sent, logged [x] 8107 absent after, other 16 docs intact [x] no other state change
- Implementation: `delete004.py` (temp, removed). Before: 17 docs incl. 8107 (img-903091643, 03/09/2026 09:17 AM, 3p). Payload single-DOC only. DELETE → 200 (727B, `REQUEST: ACCEPTED`). After: 16 docs, removed=[8107], added=[]. Evidence `logs/delete-20260903T105243Z-*`.
- Validation: before/after diff asserted in-script (no-gone + exact-set-diff). Success signature: HTTP 200 + `<TITLE>REQUEST: ACCEPTED</TITLE>` + "successfully processed" (vs 503 `REQUEST: ERROR`).
- Risks: none remaining on this path; PWD token is per-list session value — always re-list first.
