# IIITA Network Tool

A lightweight Windows system tray application that **automatically manages proxy settings and Ruckus captive portal authentication** for IIITA campus Wi-Fi networks.

> Built for students at **IIIT Allahabad** who are tired of manually toggling proxy settings and re-logging into the campus Wi-Fi portal every time their session expires.

---

## What It Does

| Feature | Description |
|---|---|
| **Auto Proxy Toggle** | Automatically enables the campus proxy when connected to campus Wi-Fi (BH1–BH4, IIITA) and disables it on external networks |
| **Auto Authentication** | Logs you into the Ruckus captive portal automatically — no more opening a browser to sign in |
| **Session Watchdog** | Monitors your connection in the background and re-authenticates if your session drops |
| **System Tray Icon** | Lives quietly in your taskbar with color-coded status indicators |
| **Settings GUI** | Dark-themed settings window to configure credentials and network preferences |

### Tray Icon Colors
- 🟢 **Green** — Connected to campus Wi-Fi, proxy ON, internet working
- 🟡 **Yellow** — Authenticating with the captive portal...
- 🔴 **Red** — Authentication failed or no Wi-Fi connection
- ⚪ **Gray** — Connected to an external (non-campus) network, proxy OFF

---

## Installation

### Option 1: Download the Executable (Recommended)

1. Go to the [Releases](../../releases) page
2. Download `IIITA_Network_Tool.exe`
3. Double-click to run — no Python installation needed
4. On first launch, a Settings window will open. Enter your IIITA credentials and click **Save & Start**
5. The tool will appear in your system tray (bottom-right of your taskbar, near the clock)

> **Note:** Your credentials are saved locally in a `.env` file next to the executable. They are never sent anywhere except to the campus authentication portal.

### Option 2: Run from Source (For Developers)

**Prerequisites:** Python 3.10+ installed on Windows

```bash
# Clone the repository
git clone https://github.com/Ayush-Nandapure/project-proxy.git
cd project-proxy

# Install dependencies
pip install -r requirements.txt

# Run the app
python tray_app.py
```

On first run, a Settings window will pop up to configure your credentials.

---

## Usage

Once running, the tool works **completely automatically**:

1. **Connect to campus Wi-Fi** (BH1, BH2, BH3, BH4, or IIITA) — the tool detects it, enables proxy, and authenticates you
2. **Switch to a hotspot or home Wi-Fi** — the tool detects the change and disables the proxy
3. **Session expires** — the tool detects the drop and re-authenticates in the background

### System Tray Menu
Right-click the tray icon to access:
- **Status** — Shows your current connection state
- **Settings** — Open the settings window to update credentials or network config
- **Quit** — Stop the tool and disable the proxy

---

## Configuration

All settings are stored in a `.env` file. You can edit them through the **Settings** GUI or manually:

```env
# Your IIITA login credentials
RUCKUS_USERNAME=your_enrollment_number
RUCKUS_PASSWORD=your_password

# Campus proxy server
PROXY_ADDRESS=172.31.2.3:8080

# Ruckus portal IP
PORTAL_URL=https://172.31.1.90

# Campus Wi-Fi network names (comma-separated)
CAMPUS_NETWORKS=BH1,BH2,BH3,BH4,IIITA

# How often to check connection (seconds)
POLL_INTERVAL=5

# Wait time after authentication before checking again (seconds)
STABILIZE_WAIT=10
```

---

## Uninstalling

1. Right-click the tray icon → **Quit**
2. Delete the `IIITA_Network_Tool.exe` file (or the project folder if running from source)
3. Delete the `.env` file to remove saved credentials

That's it. The tool does not modify anything permanently — the proxy is always turned OFF when you quit.

---

## Project Structure

```
project-proxy/
├── tray_app.py         # Main app — system tray icon + monitoring loop
├── authenticator.py    # Ruckus captive portal auto-login
├── wifi_detector.py    # Detects current Wi-Fi SSID via netsh
├── proxy_toggle.py     # Toggles Windows proxy via registry
├── statuschecker.py    # Checks if internet is reachable
├── settings_gui.py     # Tkinter settings window
├── main.py             # Legacy CLI-only version (no tray icon)
├── .env                # Your credentials (git-ignored)
├── .env.example        # Template for new users
└── requirements.txt    # Python dependencies
```

## Building the Executable

To build the `.exe` yourself from source:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "IIITA_Network_Tool" --add-data ".env.example;." tray_app.py
```

The executable will be created in the `dist/` folder.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Proxy settings don't change | Run the app as Administrator |
| Authentication keeps failing | Verify your credentials in Settings. Try turning Wi-Fi off and on |
| Tool doesn't detect Wi-Fi | Make sure you're connected to Wi-Fi (not Ethernet) |
| `.exe` gets flagged by antivirus | This is a known false positive with PyInstaller. Add an exception for the file |

---

## License

MIT

