import requests

def is_internet_active():
    url = "http://clients3.google.com/generate_204"
    try:
        # We tell Python NOT to follow the Ruckus redirect. 
        # We just want to saee if we get intercepted.
        response = requests.get(url, timeout=5, allow_redirects=False)
        
        # If active, Google gives us 204.
        if response.status_code == 204:
            return True
            
        # If expired, Ruckus intercepts and throws a 302 Redirect.
        elif response.status_code == 302:
            print("Ruckus SCG interception detected! Session expired.")
            return False
            
        else:
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False

if __name__ == "__main__":
    if is_internet_active():
        print("Session active! No login needed.")
    else:
        print("Session expired or no internet. Login required!")