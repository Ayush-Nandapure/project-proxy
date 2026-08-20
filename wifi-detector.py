import subprocess
import re

def get_network_ssid():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output = True, text = True, check = True)
        output = result.stdout

        match = re.search(r"^\s+SSID\s+:\s+(.+)$", output, re.MULTILINE)

        if match:
            ssid = match.group(1).strip()
            return ssid     


    except subprocess.CalledProcessError as e:
        print(f"Error executing the command: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None

if __name__ == "__main__":
    wifi = get_network_ssid()
    if wifi:
        print(f"Connected to Wi-Fi: '{wifi}'")
    else:
        print("Not connected to any Wi-Fi network.")