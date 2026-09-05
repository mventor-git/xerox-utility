# Xerox Utility — User Guide

Welcome! This little app watches your Xerox machine's scan folder and
taps you on the shoulder whenever new scans arrive. Nothing to learn —
it does the watching, you do the filing.

## Before you start — your machine and network

The app talks to your Xerox over your office network, so two things
must be true first:

1. **The Xerox is set up on your local network (LAN)** — connected by
   Ethernet cable or Wi-Fi, powered on, and past any error screens.
2. **You know the machine's LAN IP address.** Find it on the machine
   itself: open its **device information** (usually under *Machine
   Status* or *Information* on the panel, or a printed configuration /
   network report) and look for the **IPv4 address** — something like
   `192.168.1.20`. Type that address into the app under
   **Settings → Printer address**, then press **Check device**. If it
   says reachable, you're good to go.

The PC and the printer must stay on the same network — if either moves
to a different Wi-Fi or subnet, the app will tell you it can't reach
the device until the address is updated.

## 1. Install (once per PC)

1. Copy the **Xerox Utility** folder onto the PC (e.g. `Documents`).
2. Double-click **`setup.bat`** — it does everything itself:
   Python (if missing), all packages, and a desktop shortcut.
3. When it asks, say **Y** to start the app right away — or later,
   double-click **`run.bat`** (or the desktop shortcut). No typing needed.

## 2. First run

1. Start the app: `python -m src.app.tray` (or your desktop shortcut).
2. The first run is deliberately quiet — it just notes what's already
   sitting on the machine, so from now on you only hear about
   **genuinely new** scans.

## 3. Everyday use

1. Scan as usual on the machine: **Store to Folder → pick folder →
   feed your papers**.
2. A Windows toast appears: which folder was used and how many pages.
3. Open the app to see each scan as a **card**:
   - **Expand** a card to preview it.
   - Type the name you want, pick a format (**PDF, PNG, JPG, TIF**),
     choose your folder, and **Save**.
4. After saving, the app asks: *move the original off the machine?*
   Say **yes** — the original is first copied to the app's trash
   folder, and only then removed from the machine. **Nothing is ever
   just deleted.**

## 4. The trash folder (your safety net)

Originals live in:

```
%AppData%\Xerox Utility\trash\<folder>\
```

- Every archived scan sits next to a small `.json` note saying where
  it came from and when.
- **Every 30 days** the app reminds you to have a look. To purge,
  simply delete the files you no longer need from that folder.
  The app itself never throws anything away.

## 5. Settings

Open **Settings** in the app to change:

- **Printer address (IP)** — normally `192.168.1.20`. Use
  *Check device* to confirm the app can reach the machine.
- **Store folder** — your default home for saved scans.
- **Trash folder** — where originals are kept (leave it unless you
  have a reason).

Settings live in `%AppData%\Xerox Utility\config.json`.

## 6. Troubleshooting

| Symptom | Try this |
|---|---|
| Machine panel shows a system error | Restart the machine (power switch, wait 30 s), give it 3–5 min to boot fully |
| No toasts appear | Windows Settings → Notifications → allow notifications for Python/apps |
| “Can't reach device” | Same Wi-Fi/network as the printer? IP changed? Ask IT for the printer's address and update Settings |
| `python` not recognized | Reinstall Python with **Add to PATH** ticked, re-run `setup.bat` |
| A scan vanished from the machine | Check the trash folder first — archiving moves it there, never deletes it |

Still stuck? Note what the app said (exact message), what the
machine's panel shows, and pass both to whoever supports you.
