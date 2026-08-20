import winreg
import ctypes

def set_proxy(enable=True, proxy_server=""):
    # The registry path where Windows stores global proxy settings
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    
    try:
        # Answer 1: We use KEY_SET_VALUE to get permission to write to the registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
        
        # Answer 2: We use REG_DWORD to save the 1 (ON) or 0 (OFF) integer
        is_enabled = 1 if enable else 0
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, is_enabled)
        
        # If enabling, we also update the proxy server address (REG_SZ for string)
        if enable and proxy_server:
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
            
        # Always close the registry key to prevent memory leaks
        winreg.CloseKey(key)
        
        # Answer 3: We use ctypes to broadcast to the OS that settings have changed
        internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
        internet_set_option(0, 37, 0, 0) # 37 = INTERNET_OPTION_SETTINGS_CHANGED
        internet_set_option(0, 39, 0, 0) # 39 = INTERNET_OPTION_REFRESH
        
        state = 'ON' if enable else 'OFF'
        print(f"Proxy successfully set to: {state}")

    except PermissionError:
        print("Permission Denied: Run your terminal as Administrator.")
    except Exception as e:
        print(f"Error modifying registry: {e}")

if __name__ == "__main__":
    # Test turning the proxy OFF
    # set_proxy(enable=False)
    
    # When you want to test turning it ON, uncomment the line below 
    # and replace the IP with your actual proxy server and port:
    set_proxy(enable=True, proxy_server="172.31.2.3:8080")