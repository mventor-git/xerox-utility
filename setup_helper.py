"""Office-PC setup, part 2 (called by setup.bat after Python+packages exist).

Finds the Xerox on the LAN, lets you pick a box by name, and writes the
config. Interactive — setup.bat calls it; humans can run it directly too:
    python setup_helper.py
"""
import re
import socket
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

TIMEOUT_CONNECT = 0.7
TIMEOUT_HTTP = 3


def local_subnets() -> list[str]:
    """First three octets of EVERY local IPv4 (multi-homed PCs have several)."""
    found: list[str] = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip.startswith("127."):
                continue
            prefix = ".".join(ip.split(".")[:3])
            if prefix not in found:
                found.append(prefix)
    except OSError:
        pass
    if not found:  # last resort: default-route address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            found = [".".join(s.getsockname()[0].split(".")[:3])]
        finally:
            s.close()
    if not found:
        raise RuntimeError("can't read this PC's network addresses")
    return found


def looks_like_xerox(ip: str) -> str | None:
    """Return a model string if http://ip answers like a Xerox, else None."""
    import requests
    try:
        r = requests.get(f"http://{ip}/", timeout=TIMEOUT_HTTP)
    except Exception:
        return None
    if r.status_code != 200:
        return None
    try:
        text = r.content.decode("windows-1252", errors="replace")
    except Exception:
        return None
    m = re.search(r"<title[^>]*>\s*(Xerox[^<]{0,60})</title>", text, re.I)
    if m:
        return m.group(1).strip()[:60]
    if "Fuji Xerox" in text or "CentreWare" in text:
        return "Xerox (unidentified model)"
    return None


def sweep(subnet: str) -> list[tuple[str, str]]:
    """Probe port 80 across the /24, fingerprint responders. Returns [(ip, model)]."""
    hosts = [f"{subnet}.{i}" for i in range(1, 255)]

    found = []
    with ThreadPoolExecutor(max_workers=64) as pool:
        for hit in pool.map(probe_host, hosts):
            if hit:
                found.append(hit)
                print(f"  found: {hit[0]}  ({hit[1]})")
    return sorted(found)


def pick(options: list[str], prompt: str, default: int = 1) -> int:
    """Show a numbered list, return the chosen INDEX (never parse display text)."""
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    while True:
        raw = input(f"{prompt} [{default}]: ").strip() or str(default)
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print("  Please type one of the numbers above.")


def probe_host(ip: str) -> tuple[str, str] | None:
    """Port-80 probe + Xerox fingerprint for one address."""
    try:
        socket.create_connection((ip, 80), timeout=TIMEOUT_CONNECT).close()
    except OSError:
        return None
    model = looks_like_xerox(ip)
    return (ip, model) if model else None


def main() -> int:
    from src.core import config as C
    from src.core import device_client
    from src.lib.parse_box_lst import parse_boxes

    print("=== Finding your Xerox on the network ===")
    try:
        subnets = local_subnets()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1
    print(f"Checking {', '.join(s + '.1-254' for s in subnets)} plus this PC itself ...")
    found: list[tuple[str, str]] = []
    for subnet in subnets:
        found.extend(h for h in sweep(subnet) if h not in found)
    # NOTE: prints below stay plain ASCII — Windows consoles choke on fancy glyphs.
    local = probe_host("127.0.0.1")  # loopback: catches local test servers/mocks
    if local and local not in found:
        print(f"  found: {local[0]}  ({local[1]})")
        found.append(local)

    if not found:
        print("No Xerox answered. Type the printer's IP yourself")
        print("(find it on the machine: device information / network report).")
        ip = input("Printer IP: ").strip()
        if not ip:
            print("[ERROR] No address given — re-run setup when you have it.")
            return 1
        model = looks_like_xerox(ip) or "unverified address"
        print(f"Using {ip} ({model}).")
    elif len(found) == 1:
        ip, model = found[0]
        yes = input(f"Use {ip} ({model})? [Y/n]: ").strip().lower()
        if yes not in ("", "y", "yes"):
            ip = input("Printer IP instead: ").strip() or ip
    else:
        idx = pick([f"{ip}  ({model})" for ip, model in found], "Which printer is yours?")
        ip = found[idx][0]

    print(f"\nListing scan folders on {ip}...")
    try:
        boxes = parse_boxes(device_client.get_raw_box_page(C.url_for_ip(ip)))
    except Exception as exc:
        print(f"[ERROR] The printer didn't answer ({exc}).")
        print("Check it is on, on this network, and past any error screen - then re-run setup.")
        return 1
    if not boxes:
        print("[ERROR] The printer answered but shows no scan folders.")
        print("Create one on the machine (Store to Folder setup), then re-run setup.")
        return 1
    names = [f"Box {b['no']} - {b['name']}" for b in boxes]
    if len(names) > 1:
        box = boxes[pick(names, "Which folder should the app watch?")]
    else:
        print(f"One folder found: {names[0]} - using it.")
        box = boxes[0]
    box_no = int(box["no"])

    cfg = C.load_config()
    default_store = cfg.get("store_dir") or str(Path.home() / "Documents" / "Scans")
    store = input(f"Where should scans be saved? [{default_store}]: ").strip() or default_store

    cfg["ip"] = ip
    cfg["box"] = box_no
    cfg["store_dir"] = store
    C.save_config(cfg)
    C.store_dir(cfg).mkdir(parents=True, exist_ok=True)
    C.trash_dir(cfg).mkdir(parents=True, exist_ok=True)
    print(f"\nSaved [OK]  printer {ip}, watching Box {box_no} ({box['name']}),")
    print(f"scans go to {store}. Config: {C.default_config_path()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
