import threading
import time
import os
import sys

import pystray
from PIL import Image, ImageDraw
from dotenv import load_dotenv

from wifi_detector import get_network_ssid
from proxy_toggle import set_proxy
from statuschecker import is_internet_active
from authenticator import authenticate_ruckus
from settings_gui import open_settings

# When running as a PyInstaller .exe, __file__ points to a temp folder.
# Use the .exe's directory instead so .env persists next to the executable.
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENV_PATH = os.path.join(BASE_DIR, ".env")


# ============================================================
# Icon Images — colored circles with clean border for system tray
# ============================================================

def make_icon(fill_color, border_color=(40, 40, 40)):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([6, 6, 58, 58], fill=fill_color, outline=border_color, width=3)
    return img

ICON_GREEN  = make_icon((76, 175, 80))     # Connected & proxy ON
ICON_YELLOW = make_icon((255, 193, 7))     # Authenticating...
ICON_GRAY   = make_icon((158, 158, 158))   # External network / proxy OFF
ICON_RED    = make_icon((244, 67, 54))     # No connection


# ============================================================
# App State — shared between the tray and the monitoring thread
# ============================================================

class AppState:
    def __init__(self):
        self.status = "Starting..."
        self.running = True
        self.reload_config = False

state = AppState()
settings_window_open = False


# ============================================================
# Config Loader
# ============================================================

def load_config():
    load_dotenv(ENV_PATH, override=True)
    return {
        "username":   os.getenv("RUCKUS_USERNAME", ""),
        "password":   os.getenv("RUCKUS_PASSWORD", ""),
        "proxy":      os.getenv("PROXY_ADDRESS", "172.31.2.3:8080"),
        "portal":     os.getenv("PORTAL_URL", "https://172.31.1.90"),
        "networks":   [s.strip() for s in os.getenv("CAMPUS_NETWORKS", "").split(",") if s.strip()],
        "poll":       int(os.getenv("POLL_INTERVAL", "5")),
        "stabilize":  int(os.getenv("STABILIZE_WAIT", "10")),
    }


# ============================================================
# Safe Notification Helper
# ============================================================

def send_notification(icon, message, title="IIITA Network Tool"):
    # Replaced desktop notifications with terminal logging
    print(f"[{title}] {message}")


# ============================================================
# Monitoring Loop — runs in a background thread
# ============================================================

def monitoring_loop(icon):
    config = load_config()

    # If credentials are missing, launch settings
    if not config["username"] or not config["password"]:
        state.status = "Setup required"
        icon.icon = ICON_RED
        send_notification(icon, "Please set your credentials in Settings.")
        launch_settings()
        config = load_config()

    previous_wifi = None
    last_auth_fail = 0
    RETRY_COOLDOWN = 10  # Reduced from 60s to 10s to recover faster from transient errors
    
    wifi_miss_count = 0
    last_notified_state = None

    while state.running:
        # Reload config if user changed settings
        if state.reload_config:
            config = load_config()
            state.reload_config = False
            previous_wifi = None  # Force re-check

        current_wifi = get_network_ssid()

        # Handle flaky Wi-Fi detection
        if not current_wifi:
            wifi_miss_count += 1
            if previous_wifi and wifi_miss_count < 3:
                # Assume still connected to prevent jitter
                current_wifi = previous_wifi
        else:
            wifi_miss_count = 0

        # --- Wi-Fi Changed ---
        if current_wifi != previous_wifi:
            last_auth_fail = 0  # Reset cooldown on network change

            if current_wifi and current_wifi in config["networks"]:
                # Campus network detected
                icon.icon = ICON_GREEN
                state.status = f"Connected: {current_wifi} (Proxy ON)"
                icon.title = f"IIITA Tool: {current_wifi}"
                set_proxy(enable=True, proxy_server=config["proxy"])
                
                # Give Windows 3 seconds to assign an IP address after connecting 
                # to prevent WinError 10051 (Network Unreachable)
                time.sleep(3)

                if is_internet_active(proxy=config["proxy"]):
                    if last_notified_state != "connected":
                        send_notification(icon, f"Connected to {current_wifi}. Proxy ON ✓")
                        last_notified_state = "connected"
                else:
                    # Need to authenticate
                    icon.icon = ICON_YELLOW
                    state.status = f"{current_wifi} — Authenticating..."
                    icon.title = "IIITA Tool: Authenticating..."

                    if authenticate_ruckus(config["username"], config["password"], config["portal"]):
                        icon.icon = ICON_GREEN
                        state.status = f"Connected: {current_wifi} (Proxy ON)"
                        icon.title = f"IIITA Tool: {current_wifi}"
                        if last_notified_state != "connected":
                            send_notification(icon, f"Authenticated on {current_wifi} ✓")
                            last_notified_state = "connected"
                        time.sleep(config["stabilize"])
                    else:
                        icon.icon = ICON_RED  # Turn red so it doesn't stay stuck yellow
                        state.status = f"{current_wifi} — Auth failed (retry in {RETRY_COOLDOWN}s)"
                        icon.title = "IIITA Tool: Auth failed"
                        if last_notified_state != "auth_failed":
                            send_notification(icon, f"Auth failed. Retrying in {RETRY_COOLDOWN}s.")
                            last_notified_state = "auth_failed"
                        last_auth_fail = time.time()

            elif current_wifi:
                # External network
                icon.icon = ICON_GRAY
                state.status = f"Connected: {current_wifi} (Proxy OFF)"
                icon.title = f"IIITA Tool: {current_wifi} (Proxy OFF)"
                set_proxy(enable=False)
                if last_notified_state != "external":
                    send_notification(icon, f"External network ({current_wifi}). Proxy OFF.")
                    last_notified_state = "external"

            else:
                # No Wi-Fi
                icon.icon = ICON_RED
                state.status = "No Wi-Fi connection"
                icon.title = "IIITA Tool: No Wi-Fi"
                set_proxy(enable=False)
                if last_notified_state != "disconnected":
                    send_notification(icon, "Disconnected from Wi-Fi. Proxy OFF.")
                    last_notified_state = "disconnected"

            previous_wifi = current_wifi

        # --- Watchdog (same campus network, periodic check) ---
        elif current_wifi and current_wifi in config["networks"]:
            if last_auth_fail and (time.time() - last_auth_fail) < RETRY_COOLDOWN:
                pass  # Still in cooldown, skip
            elif not is_internet_active(proxy=config["proxy"]):
                icon.icon = ICON_YELLOW
                state.status = f"{current_wifi} — Re-authenticating..."
                icon.title = "IIITA Tool: Re-authenticating..."
                set_proxy(enable=True, proxy_server=config["proxy"])

                if authenticate_ruckus(config["username"], config["password"], config["portal"]):
                    icon.icon = ICON_GREEN
                    state.status = f"Connected: {current_wifi} (Proxy ON)"
                    icon.title = f"IIITA Tool: {current_wifi}"
                    if last_notified_state == "auth_failed":
                        send_notification(icon, "Session restored ✓")
                    last_notified_state = "connected"
                    last_auth_fail = 0
                    time.sleep(config["stabilize"])
                else:
                    icon.icon = ICON_RED
                    state.status = f"{current_wifi} — Auth failed (retry in {RETRY_COOLDOWN}s)"
                    icon.title = "IIITA Tool: Auth failed"
                    if last_notified_state != "auth_failed":
                        send_notification(icon, f"Auth failed. Retrying in {RETRY_COOLDOWN}s.")
                        last_notified_state = "auth_failed"
                    last_auth_fail = time.time()

        time.sleep(config["poll"])


# ============================================================
# Tray Menu Callbacks
# ============================================================

def launch_settings():
    global settings_window_open
    if settings_window_open:
        return
    settings_window_open = True
    try:
        open_settings(on_save=lambda: setattr(state, "reload_config", True))
    finally:
        settings_window_open = False


def on_settings(icon, item):
    threading.Thread(target=launch_settings, daemon=True).start()


def on_quit(icon, item):
    state.running = False
    set_proxy(enable=False)
    try:
        icon.visible = False
        icon.stop()
    except Exception:
        pass


# ============================================================
# Main
# ============================================================

def main():
    menu = pystray.Menu(
        pystray.MenuItem(lambda text: state.status, None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Settings", on_settings),
        pystray.MenuItem("Quit", on_quit),
    )

    icon = pystray.Icon(
        name="iiita-network-tool",
        icon=ICON_GRAY,
        title="IIITA Network Tool",
        menu=menu,
    )

    # 1. Start the tray icon detached so it runs in its own thread
    icon.run_detached()
    # 2. Make visible explicitly
    icon.visible = True

    # 3. Start monitoring in a background daemon thread
    thread = threading.Thread(target=monitoring_loop, args=(icon,), daemon=True)
    thread.start()

    print("==================================================")
    print("IIITA Network Tool is running in the system tray.")
    print("Press Ctrl+C in this terminal to stop.")
    print("==================================================")

    # 4. Keep main thread alive and responsive to Ctrl+C
    try:
        while state.running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping IIITA Network Tool...")
        on_quit(icon, None)
        print("Done. Cleaned up and exited.")


if __name__ == "__main__":
    main()
