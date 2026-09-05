# HANDOVER
- Completed: bootstrap through tray app, all proven; retrieve verdict is device-side.
- Current: ticket-017 completed. Next: delete UI wiring; downloader waits on healthy machine.
- Notes: IP `192.168.1.20` is config default, never hardcode; legacy UTF-16 INI ignored; retrieve blob 503s direct — don't retry blindly, drive browser flow.
- Warnings: never create folders/users on device; delete only on confirm; don't edit `profile.md`/`.muse`.
