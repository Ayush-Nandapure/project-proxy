import tkinter as tk
from pathlib import Path


# Path to .env file (same folder as this script)
ENV_PATH = Path(__file__).parent / ".env"


def read_env():
    """Read current values from .env file."""
    values = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                values[key.strip()] = val.strip()
    return values


def write_env(values):
    """Write values to .env file."""
    content = f"""# Ruckus Credentials
RUCKUS_USERNAME={values.get('RUCKUS_USERNAME', '')}
RUCKUS_PASSWORD={values.get('RUCKUS_PASSWORD', '')}

# Proxy Configuration
PROXY_ADDRESS={values.get('PROXY_ADDRESS', '172.31.2.3:8080')}

# Ruckus Portal URL
PORTAL_URL={values.get('PORTAL_URL', 'https://172.31.1.90')}

# Campus network SSIDs (comma-separated)
CAMPUS_NETWORKS={values.get('CAMPUS_NETWORKS', 'BH1,BH2,BH3,BH4,IIITA')}

# Polling intervals (seconds)
POLL_INTERVAL={values.get('POLL_INTERVAL', '5')}
STABILIZE_WAIT={values.get('STABILIZE_WAIT', '10')}
"""
    ENV_PATH.write_text(content, encoding="utf-8")


def open_settings(on_save=None):
    """Open the settings window. Blocks until the window is closed."""
    current = read_env()
    saved = [False]

    # --- Window Setup ---
    root = tk.Tk()
    root.title("IIITA Network Tool — Settings")
    root.geometry("440x480")
    root.resizable(False, False)

    # Colors (dark theme)
    BG = "#1e1e2e"
    FG = "#cdd6f4"
    ACCENT = "#89b4fa"
    ENTRY_BG = "#313244"
    BORDER = "#45475a"

    root.configure(bg=BG)

    # --- Title ---
    tk.Label(
        root, text="IIITA Network Tool", bg=BG, fg=ACCENT,
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(20, 5))

    tk.Label(
        root, text="Configure your campus network settings", bg=BG, fg="#6c7086",
        font=("Segoe UI", 9)
    ).pack(pady=(0, 15))

    # --- Form Fields ---
    form = tk.Frame(root, bg=BG)
    form.pack(padx=35, fill="x")

    fields = {}
    field_defs = [
        ("Username", "RUCKUS_USERNAME", "", False),
        ("Password", "RUCKUS_PASSWORD", "", True),
        ("Proxy Address", "PROXY_ADDRESS", "172.31.2.3:8080", False),
        ("Campus Networks", "CAMPUS_NETWORKS", "BH1,BH2,BH3,BH4,IIITA", False),
    ]

    for label_text, key, default, is_password in field_defs:
        tk.Label(
            form, text=label_text, bg=BG, fg=FG,
            font=("Segoe UI", 10), anchor="w"
        ).pack(fill="x", pady=(8, 2))

        entry = tk.Entry(
            form, font=("Segoe UI", 10), bg=ENTRY_BG, fg=FG,
            insertbackground=FG, relief="flat",
            highlightthickness=1, highlightcolor=ACCENT, highlightbackground=BORDER,
        )
        if is_password:
            entry.config(show="•")
        entry.insert(0, current.get(key, default))
        entry.pack(fill="x", ipady=5)
        fields[key] = entry

    # --- Save Button ---
    def save():
        values = {key: entry.get() for key, entry in fields.items()}
        # Keep non-GUI settings from current .env
        values["PORTAL_URL"] = current.get("PORTAL_URL", "https://172.31.1.90")
        values["POLL_INTERVAL"] = current.get("POLL_INTERVAL", "5")
        values["STABILIZE_WAIT"] = current.get("STABILIZE_WAIT", "10")
        write_env(values)
        saved[0] = True
        if on_save:
            on_save()
        root.destroy()

    tk.Button(
        root, text="Save & Start", font=("Segoe UI", 11, "bold"),
        bg=ACCENT, fg="#1e1e2e", activebackground="#74a0e0",
        relief="flat", cursor="hand2", command=save,
    ).pack(pady=20, ipadx=25, ipady=6)

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 440) // 2
    y = (root.winfo_screenheight() - 480) // 2
    root.geometry(f"440x480+{x}+{y}")

    root.mainloop()
    return saved[0]


if __name__ == "__main__":
    result = open_settings()
    print("Settings saved!" if result else "Closed without saving.")
