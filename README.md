# Xerox Utility

A little sidecar that watches your Xerox WorkCentre's scan folder, taps you
on the shoulder when new scans land, and files them where you want —
without ever replacing your Xerox drivers.

**It never destroys a scan.** Removing a file from the machine first tucks
the original into a local trash folder. Purging that trash is always your
call — the app just reminds you once every 30 days.

## How it works

1. **Poll** — every couple of minutes it lists the scan folder (Box 1 `Scans`).
2. **Notify** — new arrivals pop up as one tidy Windows toast.
3. **Queue** — each scan becomes a card: expand to preview, pick a
   name and format (PDF, PNG, JPG, TIF), save where you like.
4. **Archive** — after saving, one confirm moves the original off the
   machine into `%AppData%/Xerox Utility/trash/<box>/`.

## Quickstart

Double-click **`setup.bat`** — it installs Python (if missing), all
packages, and a desktop shortcut, then offers to start the app.

Prefer the manual route:

```bat
pip install -r requirements.txt
python -m src.app.tray
```

📖 **New here? Read [guide.md](guide.md)** — prerequisites (your Xerox
on the LAN + finding its IP), first run, everyday use, the trash
safety net, and troubleshooting.

On first run it quietly notes what's already on the machine, so you only
hear about genuinely new scans from then on.

## Settings

Stored in `%AppData%/Xerox Utility/config.json`:

| Key | Meaning | Default |
|---|---|---|
| `ip` | Printer address | `192.168.1.20` |
| `store_dir` | Where your scans go | (you pick) |
| `trash_dir` | Safety net for originals | AppData `trash/` |
| `purge_check_days` | How often to nudge a trash review | `30` |

Check the machine is reachable any time from Settings → Check device.

## Layout

```
src/app/        tray entry + wiring (nothing else may wire modules)
src/core/       config, watermark, device client
src/lib/        little parsers (box lists, filename dates)
src/modules/    one job each: discover, poll, notify, cards,
                preview, save/convert, delete, settings
docs/           AI memory (state, handover, backlog, decisions…)
tickets/        one file per finished step of work
```

Modules never import each other — only `src/app/` connects them.

## Device notes

- Tested against a WorkCentre 5325: folder list, per-file list, and
  per-file delete are proven live (see `docs/cache/device_contract.md`).
- Full-file download still needs the browser-style retrieve flow —
  that's the next big step (BACKLOG #1).
- If the panel ever shows a system error, restart the machine and give
  it a few minutes; the app waits patiently and catches up.

## Credits — how this was built

Designed and built by **Mventor**, the Software Development Operating
System (architecture, engineering, QA, docs, and release care in one
loop), together with **Muse** thinking agents (product thinking and
project profiles).

Powered by **Muse Spark 1.3 Free** · **OpenCode Zen** · **xhigh**.
