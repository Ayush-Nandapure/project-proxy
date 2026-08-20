import time
from wifi_detector import get_network_ssid
from proxy_toggle import set_proxy

def auto_switch():
    TARGET_SSID = "BH3"
    PROXY_ADDRESS = "172.31.2.3:8080" 
    
    # This variable remembers the last network we saw so we can detect changes
    previous_wifi = None
    
    print("Starting continuous network monitor... (Press Ctrl+C to stop)")
    
    try:
        # The infinite loop keeps the program alive forever
        while True:
            current_wifi = get_network_ssid()
            
            # We only execute the logic IF the network has changed since the last check
            if current_wifi != previous_wifi:
                print(f"\n[Network Change Detected] Switched to: '{current_wifi}'")
                
                if current_wifi == TARGET_SSID:
                    print("Target network detected. Enabling proxy...")
                    set_proxy(enable=True, proxy_server=PROXY_ADDRESS)
                elif current_wifi:
                    print("Different network detected. Disabling proxy...")
                    set_proxy(enable=False)
                else:
                    print("No Wi-Fi connection detected. Disabling proxy...")
                    set_proxy(enable=False)
                
                # Update our memory so we don't trigger this again until the next change
                previous_wifi = current_wifi
            
            # Pause the script for 5 seconds to prevent high CPU usage
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nMonitor stopped by user. Exiting cleanly...")

if __name__ == "__main__":
    auto_switch()