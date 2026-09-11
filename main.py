import time
import os
from dotenv import load_dotenv

from wifi_detector import get_network_ssid
from proxy_toggle import set_proxy
from statuschecker import is_internet_active
from authenticator import authenticate_ruckus

# Load settings from .env
load_dotenv()
CAMPUS_NETWORKS = [s.strip() for s in os.getenv("CAMPUS_NETWORKS", "BH1,BH2,BH3,BH4,IIITA").split(",")]
PROXY_ADDRESS = os.getenv("PROXY_ADDRESS", "172.31.2.3:8080")
USERNAME = os.getenv("RUCKUS_USERNAME")
PASSWORD = os.getenv("RUCKUS_PASSWORD")
PORTAL_URL = os.getenv("PORTAL_URL", "https://172.31.1.90")

def main():
    if not USERNAME or not PASSWORD:
        print("[Error] RUCKUS_USERNAME or RUCKUS_PASSWORD missing in .env file!")
        print("Please check your .env file.")
        return

    previous_wifi = None
    last_auth_fail = 0  # Timestamp of last failed auth attempt
    RETRY_COOLDOWN = 60  # Wait 60 seconds after a failed auth before retrying
    
    print("=" * 50)
    print("IIITA Smart Network & Authentication Daemon Started")
    print(f"Monitoring networks: {CAMPUS_NETWORKS}")
    print("Press Ctrl+C to stop.")
    print("=" * 50)
    
    try:
        while True:
            current_wifi = get_network_ssid()
            
            # --- Wi-Fi Network Changed ---
            if current_wifi != previous_wifi:
                print(f"\n[Network Change] Connected to: '{current_wifi}'")
                last_auth_fail = 0  # Reset cooldown on network change
                
                if current_wifi in CAMPUS_NETWORKS:
                    print("-> Campus network detected. Enabling proxy...")
                    set_proxy(enable=True, proxy_server=PROXY_ADDRESS)
                    
                    # Test if internet works through proxy
                    if is_internet_active(proxy=PROXY_ADDRESS):
                        print("-> Session is active! Internet is working.")
                    else:
                        print("-> Session expired or not signed in. Authenticating...")
                        if authenticate_ruckus(USERNAME, PASSWORD, PORTAL_URL):
                            print("-> Waiting 10s for network to stabilize...")
                            time.sleep(10)
                        else:
                            print("-> Authentication failed. Will retry in 60 seconds.")
                            last_auth_fail = time.time()
                        
                elif current_wifi:
                    print("-> External network detected. Disabling proxy...")
                    set_proxy(enable=False)
                else:
                    print("-> No Wi-Fi connection. Disabling proxy...")
                    set_proxy(enable=False)
                
                previous_wifi = current_wifi
            
            # --- Background Check (Every loop while connected to campus Wi-Fi) ---
            elif current_wifi in CAMPUS_NETWORKS:
                # Skip if we recently failed (cooldown period)
                if last_auth_fail and (time.time() - last_auth_fail) < RETRY_COOLDOWN:
                    pass  # Still in cooldown, do nothing
                elif not is_internet_active(proxy=PROXY_ADDRESS):
                    print(f"\n[Session Expired] Lost internet connection. Re-authenticating...")
                    set_proxy(enable=True, proxy_server=PROXY_ADDRESS)
                    if authenticate_ruckus(USERNAME, PASSWORD, PORTAL_URL):
                        print("-> Session restored. Waiting 10s to stabilize...")
                        last_auth_fail = 0  # Reset cooldown on success
                        time.sleep(10)
                    else:
                        print(f"-> Authentication failed. Will retry in {RETRY_COOLDOWN} seconds.")
                        last_auth_fail = time.time()

            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n[Exit] Monitor stopped by user. Cleaning up...")
        set_proxy(enable=False)

if __name__ == "__main__":
    main()