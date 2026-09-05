# Device contract (locked 2026-09-03, live probe 5325 @ 192.168.1.20)
Evidence: `logs/probe-20260903T104615Z-*`. Read-only probe: GET + list-POST only.

## Proven
- `GET /scpblst.htm` → `var box=[[no,name,'',0,1]...]`. Single box since 2026-09-03
  (user deleted the rest): `[[1,'Scans','',0,1]]`. Was 7 boxes (Scans, DC_Opal,
  ahmedOpalIT, DC_Opal&Agoza, Agoza@@Opal, Opal#@#@#DC, momo).
- `POST /PBDOCLST.cmd {BOX,ORD=DD,SET=1,LTOP,LNUM,PAGE}` → `var box=[n,pwd,ord,0,name,0]`
  (cells[1] = session PWD token) + `var lst=[[fileNo,'DD/MM/YYYY hh:mm AM',pages,?,kind,name,0,0,0]...]`
  (Box1: 17 docs; kind=2; names `img-MDDHHMMSS`, e.g. `img-903091643`).

## Shape-known (from Retrieve-form tail)
- Retrieve: `GET /PBDOCLNK.cmd`, 15 fields: BOX,PWD,ORD,DGACNT,GACNT,ACNTUID,
  DOC (slash-joined `8025/`), FORM∈{TIFJPG,PDF} (`var formOpt`), PAGE, SMNL,
  HCMP, ICMP, OCR, LANG, TCMP. Blob UNPROVEN (see exhaustion log).
- Print: `POST /PBDOCPRT.cmd` (same DOC style). Out of scope.
- Box-level: `POST /PBLST.cmd`, `/PBINFO.cmd`, `/PBOXRMLST[KO].cmd`. Out of scope (never touch boxes).

## Retrieve verdict (ticket-017): DEVICE-SIDE outage, not our code
Handler census (all read-only): scpblst ✓, PBDOCLST ✓, PBDOCSORT ✓,
PBDOCRM ✓ (proven) vs PBLST ✗, PBINFO ✗, PBDOCLNK ✗ (all 503).
Sibling endpoints on the same box disagree → the controller's web service is
partially crashed (fits the recent panel system error). No client variant and
no browser automation can fix a server-side 503. Next step is at the machine:
clean restart, then re-probe PBINFO; if still 503 with no panel error, call a
technician. Re-run the T15 variant log only after INFO answers 200 again.

## Delete (proven)
- Delete: `POST /PBDOCRM.cmd {BOX,PWD,ORD,DOC slash-joined}`. PROVEN 2026-09-03
  (ticket-004, user-confirmed): Box1/DOC `8107/` → HTTP 200 + `REQUEST: ACCEPTED`
  + "successfully processed"; verify-after 17→16 docs, only 8107 gone.
  Always re-list first (PWD is a per-list session token); assert before/after diff.

## Notes
- No cookies set by device. Box1 at 17 docs (newest 8134) as of 2026-09-05.
- History: boxes 2-7 intermittently 503 pre-restart (flaky service, varied run to
  run); user deleted them 2026-09-03 — rows retired, per-box skip retained as safety.
- Filename TS ≈ `date` column (±2 min; 2 docs ±11 min) — watermark uses (fileNo,date,ts) tuple, safe.
- `GET /scan.htm` = nav shell, 0 forms, no cmds.
