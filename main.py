import time
from wifi_detector import get_network_ssid
from proxy_toggle import set_proxy

def auto_switch():
    # 1. Configuration variables
    TARGET_SSID = "BH3"
    PROXY_ADDRESS = "172.31.2.3:8080" 
    
    print("Checking current network connection...")
    
    # 2. Call the function from Milestone 1
    current_wifi = get_network_ssid()
    
    # 3. Decision logic
    if current_wifi:
        print(f"Currently connected to: '{current_wifi}'")
        
        if current_wifi == TARGET_SSID:
            print("Target network detected. Enabling proxy...")
            # Call the function from Milestone 2 (Enable)
            set_proxy(enable=True, proxy_server=PROXY_ADDRESS)
        else:
            print("Different network detected. Disabling proxy...")
            # Call the function from Milestone 2 (Disable)
            set_proxy(enable=False)
            
    else:
        print("No Wi-Fi connection detected. Disabling proxy just in case...")
        set_proxy(enable=False)

if __name__ == "__main__":
    auto_switch()