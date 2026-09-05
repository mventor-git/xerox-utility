# HANDOVER
- Completed: bootstrap→run_once plus single-box verify (user deleted boxes 2-7; flakiness retired).
- Current: ticket-011 completed. Next: tray GUI; downloader browser-flow.
- Notes: IP `192.168.1.20` is config default, never hardcode; legacy UTF-16 INI ignored; retrieve blob 503s direct — don't retry blindly, drive browser flow.
- Warnings: never create folders/users on device; delete only on confirm; don't edit `profile.md`/`.muse`.
