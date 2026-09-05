# Xerox Utility — profile.md
Sidecar auto-scanner for Xerox WorkCentre (proven: 5325 @ 192.168.1.20).
Watches device folders, notifies, saves/converts. Co-exists with Network Scan3 v1.15, never replaces driver.

## Users
- Office staff using Xerox `Store to Folder` (pick folder → password → feed papers).
- Admin creates folders on device web UI; app never creates folders/users.

## Stack
| Layer | Choice |
|---|---|
| Lang | Python 3.11+ |
| UI | Modern Python UI (CustomTkinter/PySide6) + Win toast + tray |
| HTTP | requests (sync poller, timeout 10s) |
| Parse | regex `var box/lst` (charset windows-1252), no BS for vars |
| Convert | Pillow (PNG/JPG) + pypdf/img2pdf (TIFF multipage→PDF) |
| Store | JSON config + watermark file |

## Device contract (config, never hardcoded)
- `IP` default `192.168.1.20`, `GET scpblst.htm` → `var box=[[n,name...]]`
- `POST PBDOCLST.cmd {BOX,ORD=DD,SET=1,LTOP,LNUM=100,PAGE}` → `var lst=[[fileNo,dateStr,pages,type,name...]]`, `var box=[n,...]`
- Retrieve/delete endpoints: reverse-engineer from Retrieve form tail (open).
- Filename date: `...-8107-260903091730` = `YYMMDDHHMMSS`.

## Architecture
- Poller → Differ (watermark per-box) → Notifier → Queue/Cards → Lazy downloader → Save/Convert → Delete-confirm.
- Modules talk via explicit functions, no cross-imports. No SNMP/SOAP/TWAIN.
- Background timer + UI thread separate; downloads only on expand/click.

## Structure
```
Xerox Utility/
  profile.md | .muse
  src/app/ (tray, composition)
  src/modules/ (discover,poller,notify,cards,preview,save_convert,delete,settings)
  src/core/ (config,watermark,device_client)
  src/lib/ (parse_box_lst, filename_date)
```

## Conventions
- Read-only by default: only `GET` + list `POST`; delete only on explicit user confirm.
- `UTF-16 INI` legacy ignored; own JSON in `%AppData%/Xerox Utility/`.
- Plain text, greppable, fail loudly on device errors.
