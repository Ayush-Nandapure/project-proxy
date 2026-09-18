# IIITA Network Tool

A lightweight Windows system tray application that **automatically manages proxy settings and Ruckus captive portal authentication** for IIITA campus Wi-Fi networks.

Built for students at **IIIT Allahabad** who are tired of manually toggling proxy settings and re-logging into the campus Wi-Fi portal every time their session expires.

---

## What It Does

When you connect to campus Wi-Fi (BH1, BH2, BH3, BH4, IIITA), this tool automatically:

1. **Enables the campus proxy** (`172.31.2.3:8080`) in your Windows settings
2. **Detects the Ruckus captive portal** and logs you in with your saved credentials
3. **Monitors your session** in the background — if your login expires, it re-authenticates silently
4. **Disables the proxy** when you switch to a non-campus network (like your phone hotspot)

All of this happens in the background via a small icon in your system tray (bottom-right corner, near the clock).

### Tray Icon Colors
| Color | Meaning |
|---|---|
| 🟢 Green | Connected to campus Wi-Fi, proxy ON, internet working |
| 🟡 Yellow | Currently authenticating with the portal... |
| 🔴 Red | Authentication failed or no Wi-Fi connection |
| ⚪ Gray | Connected to an external (non-campus) network, proxy OFF |

---

## How It Is Built

The tool is written in **Python** and consists of the following modules:

| File | Purpose |
|---|---|
| `tray_app.py` | Main application — system tray icon, monitoring loop, and state management |
| `authenticator.py` | Mimics a browser to log into the Ruckus captive portal via HTTP requests |
| `wifi_detector.py` | Detects which Wi-Fi network you're connected to using `netsh` (Windows command) |
| `proxy_toggle.py` | Toggles the Windows proxy ON/OFF by writing to the Windows Registry |
| `statuschecker.py` | Checks if the internet is reachable by pinging Google's connectivity endpoint |
| `settings_gui.py` | A dark-themed settings window (built with Tkinter) for entering credentials |
| `main.py` | Legacy CLI-only version (no tray icon, runs in terminal only) |

### Key Technologies
- **Python 3.10+** — Core language
- **requests + BeautifulSoup** — HTTP requests and HTML parsing for captive portal authentication
- **pystray + Pillow** — System tray icon with colored status indicators
- **Tkinter** — Settings GUI window
- **winreg + ctypes** — Direct Windows Registry and Win32 API access for proxy control
- **PyInstaller** — Packages everything into a standalone `.exe`

### Architecture
The app runs two threads:
1. **Main thread** — Keeps the system tray icon responsive (right-click menu)
2. **Background thread** — Runs an infinite loop that checks your Wi-Fi every 5 seconds, toggles proxy, and authenticates when needed

---

## How to Install (For Users)

### Option 1: Download the Executable (No Python Needed)

1. Go to the [Releases](../../releases) page on GitHub
2. Download `IIITA_Network_Tool.exe`
3. Place it in any folder (e.g., your Desktop or Documents)
4. Double-click to run
5. On first launch, a **Settings window** will open — enter your IIITA username and password, then click **Save & Start**
6. The tool will appear as a small colored circle in your system tray
7. That's it! It will automatically manage your proxy and authentication from now on

> **Tip:** Right-click the tray icon to access Settings (to change credentials) or Quit.

### Option 2: Run from Source Code (For Developers)

```bash
# Clone the repository
git clone https://github.com/Ayush-Nandapure/project-proxy.git
cd project-proxy

# Install Python dependencies
pip install -r requirements.txt

# Run the app
python tray_app.py
```

### Building the Executable Yourself

If you want to build the `.exe` from source:

```bash
pip install pyinstaller
pyinstaller --onefile --name "IIITA_Network_Tool" --add-data ".env.example;." tray_app.py
```

The executable will be created in the `dist/` folder.

---

## How to Uninstall

1. Right-click the tray icon → click **Quit** (this turns the proxy OFF)
2. Delete the `IIITA_Network_Tool.exe` file
3. Delete the `.env` file that was created next to the executable (this contains your saved credentials)

**That's it.** The tool does not install any services, drivers, startup entries, or system-wide changes. The only thing it modifies is the Windows proxy setting, which is always turned OFF when you quit. Deleting the files removes all traces.

---

## Security Warnings

> **Please read these before using the tool.**

### Your Password is Stored in Plain Text
Your IIITA username and password are saved in a `.env` file (a simple text file) next to the executable. Anyone with access to your laptop can open this file and read your password. **Do not share the `.env` file with anyone.(I am working on a solution for this)**

### Your Password is Sent Over HTTPS
The tool sends your credentials to the Ruckus captive portal over HTTPS (encrypted). However, the campus portal uses a self-signed SSL certificate, so the tool disables SSL verification for portal requests. This is standard practice for captive portals but means the connection is not verified against a trusted certificate authority.

### The `.env` File is Git-Ignored
If you clone this repository and add your credentials, they will **not** be pushed to GitHub — the `.gitignore` file prevents this. However, always double-check before pushing.

### No Data is Collected
This tool does not send your credentials, browsing data, or any personal information anywhere other than the IIITA campus authentication portal (`172.31.1.90`). The source code is fully open for inspection.

### Antivirus False Positives
The `.exe` file may be flagged by some antivirus programs. This is a [known false positive with PyInstaller](https://github.com/pyinstaller/pyinstaller/issues/6754) — it happens because PyInstaller bundles Python into an executable, which looks suspicious to heuristic scanners. You can verify the tool is safe by reading the source code, or by running `python tray_app.py` directly instead of using the `.exe`.
Solution: To bypass this you have do the following process once:
1. Right click on the .exe file and open properties.
2. In general tab, at bottom click the checkbox for unblock and the tool starts working normally after this. 

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Proxy settings don't change | Run the app as Administrator |
| Authentication keeps failing | Check credentials in Settings. Try turning Wi-Fi off and on |
| Tool doesn't detect Wi-Fi | Make sure you're on Wi-Fi, not Ethernet |
| `.exe` flagged by antivirus | Add an exception for the file (see Security Warnings above) |
| Settings window has no Save button | Update to the latest version — this was a UI sizing bug that has been fixed |
| Browser opens Ruckus login page | This is Windows, not the tool. Close the browser tab — the tool already authenticated you |

---

