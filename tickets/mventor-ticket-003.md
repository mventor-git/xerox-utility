# mventor-ticket-003: read-only device probe (BACKLOG#1)
- Status: Completed
- Created: 2026-09-03 | Priority: high | Dependencies: ticket-002 (scaffold done)
- Goal: lock retrieve/download + delete `.cmd` contract via READ-ONLY probe of 192.168.1.20.
- Scope: GET scpblst.htm (+scan.htm), POST PBDOCLST list only. NEVER delete/create. Update `device_client.py` constants + `docs/cache/device_contract.md` + memory docs.
- Acceptance: [x] scpblst fetched + 7 boxes parsed [x] PBDOCLST lst parsed (Box1, 17 docs) [x] Retrieve tail captured (GET PBDOCLNK.cmd, 15 fields) [x] delete shape known (POST PBDOCRM.cmd {BOX,PWD,ORD,DOC/}), never invoked [x] no state change on device
- Implementation: probe scripts (temp, removed); evidence `logs/probe-20260903T104615Z-*` + retrieve 503 heads. Fixed single-quote tokenizer bug (live names kept quotes), 9-cell lst rows, img- short TS, `retrieve_params`/`build_retrieve_url`/`delete_payload` builders, `docs/cache/device_contract.md`.
- Validation: compileall OK; live-check OK (7 boxes exact, 17 docs, first doc 8107/img-903091643, builders exact, FORM guard); double-quote compat OK. Retrieve blob UNPROVEN: 6 direct-GET variants → 503 REQUEST: ERROR (cookieless device, needs browser-frame flow) — recorded, downloader ticket follows. Delete never called by design.
- Risks: other boxes' PWD untested; filename TS ±11 min on 2 docs (watermark tuple still safe).
