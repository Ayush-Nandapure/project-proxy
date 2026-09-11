# IIITA Smart Proxy & Network Daemon

Automatically manages Windows proxy settings and Ruckus captive portal authentication based on your connected Wi-Fi network.

## What It Does

1. **Detects** which Wi-Fi network you're connected to
2. **Enables proxy** when on campus networks (BH1, BH2, BH3, BH4, IIITA, etc.)
3. **Disables proxy** when on external networks or disconnected
4. **Auto-authenticates** with the Ruckus captive portal when your session expires
5. **Watches** for session drops in the background and re-authenticates automatically

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your credentials

Copy the example environment file and fill in your details:

```bash
copy .env.example .env
```

Edit `.env` with your values:

```env
RUCKUS_USERNAME=your_enrollment_number
RUCKUS_PASSWORD=your_password
PROXY_ADDRESS=172.31.2.3:8080
PORTAL_URL=https://172.31.1.90
CAMPUS_NETWORKS=BH1,BH2,BH3,BH4,IIITA
```

### 3. Run

```bash
python main.py
```

> **Note:** On some systems you may need to run your terminal as Administrator for proxy registry changes to take effect.

## Project Structure

```
project-proxy/
├── main.py            # Main daemon loop — orchestrates everything
├── config.py          # Loads settings from .env
├── wifi_detector.py   # Detects current Wi-Fi SSID (Windows netsh)
├── proxy_toggle.py    # Toggles Windows proxy via registry
├── statuschecker.py   # Two-phase internet connectivity checker
├── authenticator.py   # Ruckus captive portal auto-login
├── .env               # Your credentials (git-ignored)
├── .env.example       # Template for friends
└── requirements.txt   # Python dependencies
```

## Sharing with Friends

1. Share the repo (your `.env` is git-ignored so credentials stay safe)
2. Have them `copy .env.example .env` and fill in their credentials
3. `pip install -r requirements.txt && python main.py`
