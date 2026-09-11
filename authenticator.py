import requests
from bs4 import BeautifulSoup
import urllib3

# Suppress insecure SSL warnings for campus routers
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def authenticate_ruckus(username, password, portal_url="https://172.31.1.90"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    try:
        # Step 1: Detect the captive portal by triggering a redirect
        # When Ruckus intercepts your traffic, any HTTP request gets redirected
        # to the actual login page URL. We capture that URL.
        print("Detecting captive portal redirect...")
        detect_response = requests.get(
            "http://clients3.google.com/generate_204",
            headers=headers,
            timeout=10,
            allow_redirects=False,
            proxies={"http": None, "https": None}
        )

        if detect_response.status_code == 302:
            # Ruckus intercepted! The Location header has the real login page URL
            login_url = detect_response.headers.get("Location", portal_url)
            print(f"Captive portal found: {login_url[:80]}...")
        elif detect_response.status_code == 204:
            # No redirect = already logged in, internet is working
            print("No captive portal detected — already logged in!")
            return True
        else:
            # Fallback: try the portal URL directly
            print(f"Unexpected status {detect_response.status_code}, trying portal directly...")
            login_url = portal_url

        # Step 2: GET the login page to fetch hidden form tokens
        print("Fetching login page tokens...")
        response = requests.get(
            login_url,
            headers=headers,
            timeout=10,
            verify=False,
            proxies={"http": None, "https": None}
        )

        if response.status_code != 200:
            print(f"Failed to reach login page. Status code: {response.status_code}")
            print(f"Response preview: {response.text[:500]}")
            return False

        # Step 3: Parse HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Helper to safely extract input values without crashing if missing
        def get_input_val(name):
            tag = soup.find('input', {'name': name})
            return tag['value'] if tag and 'value' in tag.attrs else ''

        # Step 4: Extract hidden form tokens
        login_form_token = get_input_val('LoginFromForm')
        uip_token = get_input_val('uip')
        client_mac_token = get_input_val('client_mac')
        zone_token = get_input_val('zone')

        # Step 5: Construct payload mapping tokens and credentials
        payload = {
            "RequestType": "Login",
            "uip": uip_token,
            "client_mac": client_mac_token,
            "wlan": "13",
            "zone": zone_token,
            "proxy": "1",
            "url": portal_url,
            "AppResponseCode": "100",
            "LoginFromForm": login_form_token,
            "UE-Username": username,
            "UE-Password": password
        }

        # Step 6: POST credentials to the login page (not the original portal URL)
        print("Sending authentication payload...")
        post_response = requests.post(
            login_url,
            data=payload,
            headers=headers,
            timeout=10,
            verify=False,
            proxies={"http": None, "https": None}
        )

        if post_response.status_code in [200, 302]:
            print("Authentication request sent successfully!")
            return True
        else:
            print(f"Authentication rejected by server (Status: {post_response.status_code}).")
            return False

    except Exception as e:
        print(f"Authentication error: {e}")
        return False