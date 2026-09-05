# DECISIONS
- 2026-09-03: Sidecar (not clone) — keep Scan3/TWAIN; only watch/notify/save. Smaller, safer.
- 2026-09-03: Watermark per-box (fileNo+date+filename TS) — ignore old files, catch up after offline.
- 2026-09-03: Lazy download — list on poll, TIFF only on expand/click. Light on network.
- 2026-09-03: Never destroy — post-save popup archives device original (TIF + sidecar) to `%AppData%/Xerox Utility/trash/<box>/`, then removes from device. Purge is manual only; app nudges review every 30 days, never auto-purges.
