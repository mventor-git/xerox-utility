"""Desktop GUI: sidebar + cards + settings. The stylesheet lives in STYLE below —
one place for every color, radius, and font, like CSS variables. Composition
owns every decision; this module only shows things and asks. Problems talk in
dialogs, never silent."""
from __future__ import annotations
import os
import queue
import re
import threading
from pathlib import Path

POLL_INTERVAL_S = 120
FORMATS = ["PDF", "PNG", "JPG", "TIF"]
ASSET_DIR = Path(__file__).resolve().parent.parent.parent / "assets"

STYLE = {
    "font": "Segoe UI",
    "radius": 12,
    "accent": "#0E9F8A",          # primary actions (Poll, Save)
    "accent_hover": "#0B7F6E",
    "accent_text": "#FFFFFF",
    "info": "#2E86DE",            # safe/archive actions
    "info_hover": "#1F6FBE",
    "card_border": ["#D8DEE3", "#2B3542"],
    "muted_text": ["#5D6D7E", "#8A99A8"],
    "pill_ok": "#0E9F8A",
    "pill_warn": "#B7791F",
    "sidebar_w": 228,
}


def box_token(base_url: str, box: int, timeout: int = 10) -> str:
    """Fresh session PWD token for a box (re-list; tokens are per-list)."""
    from src.core import device_client
    raw = device_client.post_raw_doc_list(base_url, int(box), timeout=timeout)
    m = re.search(r"var\s+box=\[(\d+),'([^']*)'", raw)
    if not m:
        raise RuntimeError(f"no session token for box {box}")
    return m.group(2)


def discover_boxes_live(base_url: str, timeout: int = 10) -> list[tuple[int, str]]:
    """Live [(no, name)] for dropdowns. Raises loudly when unreachable."""
    from src.core import device_client
    from src.modules.discover import discover_boxes
    try:
        raw = device_client.get_raw_box_page(base_url, timeout=timeout)
    except Exception as exc:
        raise RuntimeError(f"can't reach the printer at {base_url} ({exc})")
    return [(b["no"], b["name"]) for b in discover_boxes(raw)]


def device_fetch(base_url: str, timeout: int = 30):
    """Blob fetch via retrieve URL. 503s until the downloader ticket lands — loudly."""
    from src.core import device_client
    def fetch(item: dict) -> bytes:
        params = device_client.retrieve_params(
            int(item["box"]), box_token(base_url, int(item["box"]), timeout),
            int(item["file_no"]), form="TIFJPG")
        return device_client.fetch_blob(device_client.build_retrieve_url(base_url, params),
                                        timeout=timeout)
    return fetch


def device_delete(base_url: str, timeout: int = 15):
    """Single-doc delete, ACCEPTED-checked. Call only after user confirm + archive."""
    from src.core import device_client
    import requests
    def do_delete(item: dict) -> None:
        payload = device_client.delete_payload(
            int(item["box"]), box_token(base_url, int(item["box"]), timeout), int(item["file_no"]))
        r = requests.post(base_url.rstrip("/") + device_client.DELETE_PATH,
                          data=payload, timeout=timeout)
        body = r.content.decode(device_client.CHARSET, errors="replace")
        if r.status_code != 200 or "REQUEST: ACCEPTED" not in body:
            raise RuntimeError(f"device refused delete ({r.status_code})")
    return do_delete


class XeroxApp:
    """Thin Tk shell; built on first show so imports stay headless-safe."""

    def __init__(self, app: dict, fetch=None, poll_interval: int | None = None):
        import customtkinter as ctk
        from src.core import config as cfgmod
        self.ctk = ctk
        self.app = app
        self.cfg = app["config"]
        self.base_url = cfgmod.base_url(self.cfg)
        self.fetch = fetch or device_fetch(self.base_url)
        self.poll_interval = poll_interval or self.cfg.get("poll_interval", POLL_INTERVAL_S)
        self._results: queue.Queue = queue.Queue()
        self._card_widgets: dict = {}
        self._box_names: dict = {}
        F = STYLE["font"]

        ctk.set_appearance_mode("system")
        self.root = ctk.CTk()
        self.root.title(cfgmod.APP_NAME)
        self.root.geometry("980x640")
        self.root.minsize(760, 480)
        try:
            from PIL import Image, ImageTk
            icon = ImageTk.PhotoImage(Image.open(ASSET_DIR / "icon.png").resize((32, 32)))
            self.root.iconphoto(True, icon)
            self._icon_photo = icon
        except Exception:
            pass
        self._tray = None
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        side = ctk.CTkFrame(self.root, width=STYLE["sidebar_w"], corner_radius=0)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        from src.core.config import APP_NAME
        ctk.CTkLabel(side, text=f"◉  {APP_NAME}", font=(F, 20, "bold")).pack(pady=(20, 0), padx=16, anchor="w")
        ctk.CTkLabel(side, text="never miss a scan", font=(F, 12),
                     text_color=STYLE["muted_text"]).pack(padx=18, anchor="w", pady=(0, 12))
        self.status = ctk.CTkLabel(side, text="●  starting…", font=(F, 12, "bold"),
                                   fg_color=STYLE["pill_warn"], text_color="#FFFFFF", corner_radius=8)
        self.status.pack(pady=6, padx=14, fill="x")
        ctk.CTkButton(side, text="⟳   Poll now", font=(F, 13, "bold"),
                      fg_color=STYLE["accent"], hover_color=STYLE["accent_hover"],
                      text_color=STYLE["accent_text"], corner_radius=10, height=34,
                      command=self.poll_now).pack(pady=(10, 4), padx=14, fill="x")
        for label, cmd in (("🗑   Review trash", self.review_trash),
                           ("⚙   Settings", self.open_settings)):
            ctk.CTkButton(side, text=label, font=(F, 13), fg_color="transparent",
                          border_width=1, border_color=STYLE["card_border"],
                          corner_radius=10, height=34, command=cmd).pack(pady=4, padx=14, fill="x")
        ctk.CTkLabel(side, text="Originals are always\nkept in trash first.", font=(F, 11),
                     text_color=STYLE["muted_text"], justify="left").pack(side="bottom", pady=(0, 4), padx=16, anchor="w")
        self.footer_boxes = ctk.CTkLabel(side, text="watching…", font=(F, 11),
                                            text_color=STYLE["muted_text"])
        self.footer_boxes.pack(side="bottom", pady=(0, 14), padx=16, anchor="w")

        self.cards_box = ctk.CTkScrollableFrame(self.root, label_text="…",
                                                label_font=(F, 14, "bold"), corner_radius=0)
        self.cards_box.pack(side="right", fill="both", expand=True)

        self.refresh_cards()
        self.root.after(1000, self._drain)
        self.root.after(self.poll_interval * 1000, self._tick)
        self._ensure_tray()

    # -- system tray -----------------------------------------------------------
    def _tray_image(self):
        from PIL import Image
        return Image.open(ASSET_DIR / "icon.png")

    def _ensure_tray(self) -> None:
        """Create (once) and run the tray icon detached. Import-safe: no pystray, no tray."""
        if self._tray is not None:
            return
        try:
            import pystray
        except ImportError:
            return
        from src.core.config import APP_NAME
        menu = pystray.Menu(
            pystray.MenuItem("Open", lambda icon, item: self.root.after(0, self.show_window)),
            pystray.MenuItem("Poll now", lambda icon, item: self.poll_now()),
            pystray.MenuItem("Quit", self._quit_from_tray),
        )
        self._tray = pystray.Icon(APP_NAME, self._tray_image(), APP_NAME, menu)
        self._tray.run_detached()

    def hide_to_tray(self) -> None:
        """Closing the window parks the app in the tray; polling continues."""
        self._ensure_tray()
        self.root.withdraw()

    def show_window(self) -> None:
        self.root.deiconify()
        self.root.lift()

    def _quit_from_tray(self, icon, item) -> None:
        icon.stop()
        self.root.after(0, self.root.destroy)

    # -- background polling -------------------------------------------------
    def _tick(self) -> None:
        threading.Thread(target=self.poll_now, daemon=True).start()
        self.root.after(self.poll_interval * 1000, self._tick)

    def poll_now(self) -> None:
        try:
            self._results.put(("ok", self.app["run_once"]()))
        except Exception as exc:  # worker thread: never kill UI silently
            self._results.put(("err", f"{type(exc).__name__}: {exc}"))

    def _drain(self) -> None:
        try:
            while True:
                kind, payload = self._results.get_nowait()
                if kind == "err":
                    self._set_status("●  poll failed — retrying", warn=True)
                else:
                    n = len(payload["fresh"])
                    skipped = len(payload["errors"])
                    self._set_status(f"●  {n} new" + (f" · {skipped} skipped" if skipped else " · up to date"),
                                     warn=False)
                    names = payload.get("box_names") or {}
                    if names:
                        self._box_names = dict(names)
                        self.footer_boxes.configure(
                            text=", ".join(f"Box {b} · {names[b]}" for b in sorted(names)))
                    self.refresh_cards()
        except queue.Empty:
            pass
        self.root.after(1000, self._drain)

    def _set_status(self, text: str, warn: bool) -> None:
        self.status.configure(text=text,
                              fg_color=STYLE["pill_warn"] if warn else STYLE["pill_ok"])

    # -- cards ---------------------------------------------------------------
    def refresh_cards(self) -> None:
        ctk = self.ctk
        F = STYLE["font"]
        names = list(self._box_names.values())
        self.cards_box.configure(label_text=names[0] if len(names) == 1 else "…")
        for w in self.cards_box.winfo_children():
            w.destroy()
        self._card_widgets = {}
        for card in self.app["queue"]:
            f = ctk.CTkFrame(self.cards_box, corner_radius=STYLE["radius"],
                             border_width=1, border_color=STYLE["card_border"])
            f.pack(fill="x", pady=6, padx=8)
            head = ctk.CTkFrame(f, fg_color="transparent")
            head.pack(fill="x", padx=12, pady=(10, 0))
            stale = "  ·  gone from machine" if card.get("_stale") else ""
            ctk.CTkLabel(head, text=card["title"], font=(F, 14, "bold")).pack(side="left")
            ctk.CTkLabel(head, text=f"{card['subtitle']}{stale}", font=(F, 12),
                         text_color=STYLE["muted_text"]).pack(side="left", padx=10)
            row = ctk.CTkFrame(f, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=8)
            ctk.CTkButton(row, text="▸ Preview", width=92, height=30, corner_radius=8,
                          fg_color="transparent", border_width=1, border_color=STYLE["card_border"],
                          command=lambda cid=card["id"]: self.expand_card(cid)).pack(side="left", padx=(0, 6))
            name = ctk.CTkEntry(row, height=30, corner_radius=8,
                                placeholder_text="Name for the saved file…")
            name.insert(0, card["title"])
            name.pack(side="left", padx=2, fill="x", expand=True)
            fmt = ctk.CTkOptionMenu(row, values=FORMATS, width=96, height=30,
                                    corner_radius=8, button_color=STYLE["info"],
                                    button_hover_color=STYLE["info_hover"])
            fmt.pack(side="left", padx=6)
            ctk.CTkButton(row, text="⬇ Save", width=84, height=30, corner_radius=8,
                          font=(F, 13, "bold"), fg_color=STYLE["accent"],
                          hover_color=STYLE["accent_hover"], text_color=STYLE["accent_text"],
                          command=lambda cid=card["id"]: self.save_card(cid)).pack(side="left", padx=2)
            ctk.CTkButton(row, text="To trash", width=84, height=30, corner_radius=8,
                          fg_color="transparent", border_width=1, border_color=STYLE["card_border"],
                          command=lambda cid=card["id"]: self.archive_card(cid)).pack(side="left", padx=2)
            self._card_widgets[card["id"]] = {"frame": f, "name": name, "fmt": fmt, "preview": None}
        if not self.app["queue"]:
            ctk.CTkLabel(self.cards_box, text="✓", font=(F, 40)).pack(pady=(60, 0))
            ctk.CTkLabel(self.cards_box, text="All caught up — nothing new.",
                         font=(F, 15, "bold")).pack()
            ctk.CTkLabel(self.cards_box, text="New scans will appear here on their own.",
                         font=(F, 12), text_color=STYLE["muted_text"]).pack(pady=(0, 40))
            return
        for card in self.app["queue"]:
            if card.get("expanded") and card.get("preview"):
                self._attach_preview(card["id"], card)

    def _find(self, card_id: str) -> dict:
        for c in self.app["queue"]:
            if c["id"] == card_id:
                return c
        raise RuntimeError("card is gone — poll again")

    def expand_card(self, card_id: str) -> None:
        from tkinter import messagebox
        from src.modules import cards as cardsmod, preview as prevmod
        try:
            cardsmod.expand(self.app["queue"], card_id)
            card = self._find(card_id)
            prevmod.ensure_preview(card, self.fetch)
            self.refresh_cards()
        except Exception as exc:
            messagebox.showerror("Preview isn't ready",
                                 f"Couldn't download this scan yet:\n{exc}\n\n"
                                 f"Full downloads arrive with the downloader update — nothing was changed.")

    def _attach_preview(self, card_id: str, card: dict) -> None:
        box = self._card_widgets.get(card_id)
        if not box:
            return
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(card["preview"])).convert("RGB")
            img.thumbnail((560, 360))
            photo = self.ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            lbl = self.ctk.CTkLabel(box["frame"], image=photo, text="")
            lbl.pack(padx=12, pady=(0, 10))
            box["preview"] = lbl
        except Exception:
            from tkinter import messagebox
            messagebox.showinfo("Preview", "Downloaded, but this file can't be shown as a picture.")

    def save_card(self, card_id: str) -> None:
        from tkinter import messagebox
        from src.modules import save_convert as sc
        try:
            card = self._find(card_id)
            box = self._card_widgets[card_id]
            wanted = box["name"].get().strip() or card["title"]
            item = dict(card["item"], name=wanted)
            ext = "." + box["fmt"].get().lower()
            store = self.cfg.get("store_dir", "")
            out = sc.convert_blob(self.fetch(item), ext, sc.dest_path(store, item, ext))
            messagebox.showinfo("Saved ✓", f"Your scan is here:\n{out}")
            self.ask_archive(card)
        except Exception as exc:
            messagebox.showerror("Couldn't save", f"Nothing was written. What happened:\n{exc}")

    def ask_archive(self, card: dict) -> None:
        from tkinter import messagebox
        from src.core import config as cfgmod
        from src.modules import cards as cardsmod, delete as delmod, preview as prevmod
        if not messagebox.askyesno("Saved — clear the machine?",
                                   delmod.confirm_delete_text([card["item"]]) +
                                   "\n\nThe original is copied to trash first. Nothing is destroyed."):
            return
        try:
            blob = card.get("preview") or self.fetch(card["item"])
            where = delmod.archive_doc(blob, cfgmod.trash_dir(self.cfg), card["item"])
            device_delete(self.base_url)(card["item"])
            prevmod.release_preview(card)
            self.app["queue"][:] = cardsmod.dismiss(self.app["queue"], card["id"])
            self.refresh_cards()
            messagebox.showinfo("Archived ✓", f"Original kept safe in trash:\n{where}")
        except Exception as exc:
            messagebox.showerror("Left untouched",
                                 f"Something failed, so NOTHING was removed from the machine:\n{exc}")

    def archive_card(self, card_id: str) -> None:
        try:
            self.ask_archive(self._find(card_id))
        except Exception as exc:
            from tkinter import messagebox
            messagebox.showerror("Left untouched", str(exc))

    # -- trash + settings ------------------------------------------------------
    def review_trash(self) -> None:
        from tkinter import messagebox
        from src.core import config as cfgmod
        from src.modules import delete as delmod, settings as setmod
        troot = cfgmod.trash_dir(self.cfg)
        n = delmod.count_archived(troot)
        setmod.record_purge_check(self.cfg)
        cfgmod.save_config(self.cfg)
        try:
            os.startfile(str(troot))  # type: ignore[attr-defined]
        except Exception:
            pass
        messagebox.showinfo("Trash reviewed ✓",
                            f"{n} archived scan(s) live in\n{troot}\n\n"
                            f"Delete what you no longer need — today's review is stamped.")

    def open_settings(self) -> None:
        ctk = self.ctk
        F = STYLE["font"]
        from tkinter import filedialog, messagebox
        from src.core import config as cfgmod, device_client
        from src.modules import settings as setmod
        win = ctk.CTkToplevel(self.root)
        win.title("Settings")
        win.geometry("440x520")
        cur = setmod.current_settings(self.cfg)
        try:
            found = discover_boxes_live(self.base_url)
            box_values = [f"{n} - {name}" for n, name in found]
        except Exception:
            box_values = []
        cur_box = int(cur.get("box") or 0)
        box_initial = next((v for v in box_values if v.startswith(f"{cur_box} - ")),
                           f"{cur_box} - (current)" if cur_box else "0 - all boxes")
        if not box_values:
            box_values = [box_initial]

        rows = {}
        widgets: list = []

        def add_row(label: str, key: str, kind: str = "entry", values: list | None = None):
            ctk.CTkLabel(win, text=label, font=(F, 12, "bold")).pack(anchor="w", padx=14, pady=(8, 0))
            if kind == "option":
                w = ctk.CTkOptionMenu(win, values=values or [box_initial], width=250, height=30,
                                      corner_radius=8, button_color=STYLE["info"],
                                      button_hover_color=STYLE["info_hover"])
                w.set(box_initial if box_initial in (values or []) else (values or [box_initial])[0])
            else:
                w = ctk.CTkEntry(win, width=250, height=30, corner_radius=8)
                w.insert(0, cur.get(key, ""))
            w.pack(anchor="w", padx=14)
            rows[key] = w
            widgets.append(w)

        add_row("Printer address", "ip")
        add_row("Watch folder (0 = all folders)", "box", kind="option", values=box_values)
        add_row("My scans folder", "store_dir")
        add_row("Trash folder", "trash_dir")
        add_row("Check every (seconds)", "poll_interval")
        add_row("Trash review reminder (days)", "purge_check_days")
        msg = ctk.CTkLabel(win, text="The app keeps your originals in trash, always.", font=(F, 11),
                           text_color=STYLE["muted_text"])
        msg.pack(pady=6)

        def browse_scans():
            d = filedialog.askdirectory(title="Where should your scans go?")
            if d:
                rows["store_dir"].delete(0, "end")
                rows["store_dir"].insert(0, d)

        def browse_trash():
            d = filedialog.askdirectory(title="Where should originals be kept?")
            if d:
                rows["trash_dir"].delete(0, "end")
                rows["trash_dir"].insert(0, d)

        def check():
            from src.core.config import url_for_ip
            try:
                ok = setmod.check_device(url_for_ip(rows["ip"].get()), device_client.get_raw_box_page)
            except ValueError:
                ok = False
            msg.configure(text="Reachable - looking good." if ok else "Not reachable - check the address and network.")

        def _int(key: str, minimum: int) -> int:
            try:
                value = int(str(rows[key].get()).strip())
            except (TypeError, ValueError):
                raise ValueError(f"{key} must be a whole number")
            if value < minimum:
                raise ValueError(f"{key} must be at least {minimum}")
            return value

        def save():
            try:
                box_no = int(str(rows["box"].get()).split("-", 1)[0].strip() or 0)
                setmod.apply_settings(self.cfg, ip=rows["ip"].get(),
                                      store_dir=rows["store_dir"].get(),
                                      trash_dir=rows["trash_dir"].get() or None,
                                      box=box_no)
                self.cfg["poll_interval"] = _int("poll_interval", 30)
                self.cfg["purge_check_days"] = _int("purge_check_days", 1)
                self.poll_interval = int(self.cfg["poll_interval"])
                cfgmod.save_config(self.cfg)
                self.base_url = cfgmod.base_url(self.cfg)
                msg.configure(text="Saved - new values apply on the next poll")
            except Exception as exc:
                messagebox.showerror("Settings", str(exc))

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(pady=6)
        browse_btn = ctk.CTkButton(btn_row, text="Scans…", width=110, corner_radius=8,
                                   fg_color="transparent", border_width=1,
                                   border_color=STYLE["card_border"], command=browse_scans)
        browse_btn.pack(side="left", padx=4)
        trash_btn = ctk.CTkButton(btn_row, text="Trash…", width=110, corner_radius=8,
                                  fg_color="transparent", border_width=1,
                                  border_color=STYLE["card_border"], command=browse_trash)
        trash_btn.pack(side="left", padx=4)
        check_btn = ctk.CTkButton(btn_row, text="Check device", width=130, corner_radius=8,
                                  fg_color=STYLE["info"], hover_color=STYLE["info_hover"],
                                  command=check)
        check_btn.pack(side="left", padx=4)
        save_btn = ctk.CTkButton(win, text="Save", font=(F, 13, "bold"), corner_radius=8,
                                 fg_color=STYLE["accent"], hover_color=STYLE["accent_hover"],
                                 text_color=STYLE["accent_text"], command=save)
        save_btn.pack(pady=10)
        self._settings = {"window": win, "rows": rows, "msg": msg,
                          "browse": browse_btn, "trash_browse": trash_btn,
                          "check": check_btn, "save": save_btn}

    def mainloop(self) -> None:
        self.root.mainloop()


def launch(app: dict, **kwargs) -> None:
    """Show the window. Raises on headless machines (caller falls back)."""
    XeroxApp(app, **kwargs).mainloop()
