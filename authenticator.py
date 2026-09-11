import requests
from bs4 import BeautifulSoup
import urllib3
import urllib.parse
import re

# Suppress insecure SSL warnings for campus routers
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def find_captive_portal(session, portal_url, headers):
    """
    Detects the captive portal redirect URL.
    Uses direct IP probes so detection works even when external DNS is blocked
    prior to authentication.
    """
    # IP targets — NO DNS resolution needed.
    # Local portal IP first (fastest, most reliable on campus).
    probe_targets = [
        "http://172.31.1.90",
        "http://1.1.1.1",
        "http://1.0.0.1",
    ]

    for url in probe_targets:
        try:
            resp = session.get(
                url,
                headers=headers,
                timeout=3,
                allow_redirects=False,
                verify=False
            )

            # Check for HTTP redirect (301, 302, 303, 307, 308)
            if resp.status_code in [301, 302, 303, 307, 308] and "Location" in resp.headers:
                loc = resp.headers["Location"]
                # Skip normal Cloudflare redirect (http://1.1.1.1 -> https://1.1.1.1/)
                if ("1.1.1.1" in url and loc in ["https://1.1.1.1/", "https://one.one.one.one/"]) or \
                   ("1.0.0.1" in url and loc in ["https://1.0.0.1/"]):
                    continue

                print(f"Captive portal intercepted via {url}")
                return loc

            # If 204 returned, internet is already active
            if resp.status_code == 204:
                print("Already authenticated (got 204).")
                return "ALREADY_AUTHENTICATED"

            # Check for HTML meta refresh redirect in body
            if resp.status_code == 200 and "url=" in resp.text.lower():
                match = re.search(r'content=["\']?\d+;\s*url=([^"\'>]+)', resp.text, re.IGNORECASE)
                if match:
                    loc = match.group(1).strip()
                    print(f"Captive portal HTML redirect via {url}")
                    return loc

        except requests.exceptions.RequestException:
            # Probe failed (timeout, connection refused, etc.) — try next
            continue

    return None


def authenticate_ruckus(username, password, portal_url="https://172.31.1.90"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    session = requests.Session()
    # CRITICAL: trust_env=False prevents requests from using the Windows
    # system proxy. Without this, after set_proxy(enable=True) is called,
    # every request in this session would route through the campus proxy —
    # which is unreachable before authentication.
    session.trust_env = False

    try:
        # Step 1: Detect captive portal URL via redirect
        print("Detecting captive portal...")
        detected_url = find_captive_portal(session, portal_url, headers)

        if detected_url == "ALREADY_AUTHENTICATED":
            return True

        login_url = detected_url if detected_url else portal_url
        print(f"Target login page: {login_url}")

        # Step 2: Fetch the login page
        print("Fetching login page tokens...")
        try:
            response = session.get(
                login_url,
                headers=headers,
                timeout=10,
                verify=False
            )
        except requests.exceptions.RequestException as e:
            # If HTTPS fails, try HTTP fallback if using portal_url
            if login_url.startswith("https://"):
                fallback_url = "http://" + login_url[8:]
                print(f"HTTPS failed, trying HTTP fallback...")
                response = session.get(
                    fallback_url,
                    headers=headers,
                    timeout=10,
                    verify=False
                )
                login_url = fallback_url
            else:
                raise e

        # If HTTPS returned 400 (e.g. client cert required), try HTTP
        if response.status_code == 400 and login_url.startswith("https://"):
            fallback_url = "http://" + login_url[8:]
            print(f"Server returned 400 on HTTPS, trying HTTP...")
            fallback_resp = session.get(
                fallback_url,
                headers=headers,
                timeout=10,
                verify=False
            )
            if fallback_resp.status_code == 200:
                response = fallback_resp
                login_url = fallback_url

        if response.status_code != 200:
            print(f"Failed to reach login page. Status code: {response.status_code}")
            return False

        # Step 3: Parse HTML form and tokens
        soup = BeautifulSoup(response.text, 'html.parser')

        # Collect all form fields
        payload = {}
        for inp in soup.find_all('input'):
            name = inp.get('name')
            if name:
                payload[name] = inp.get('value', '')

        # Helper to extract specific input values
        def get_val(name):
            return payload.get(name) or ''

        login_form_token = get_val('LoginFromForm')
        uip_token = get_val('uip')
        client_mac_token = get_val('client_mac')
        zone_token = get_val('zone')

        # Construct final Ruckus payload
        payload.update({
            "RequestType": "Login",
            "uip": uip_token,
            "client_mac": client_mac_token,
            "wlan": payload.get("wlan", "13"),
            "zone": zone_token,
            "proxy": "1",
            "url": portal_url,
            "AppResponseCode": "100",
            "LoginFromForm": login_form_token,
            "UE-Username": username,
            "UE-Password": password
        })

        # Step 4: Determine POST target URL (from <form action="..."> if present)
        form = soup.find('form')
        if form and form.get('action'):
            post_url = urllib.parse.urljoin(login_url, form.get('action'))
        else:
            post_url = login_url

        # Step 5: Submit credentials
        print(f"Submitting credentials...")
        post_response = session.post(
            post_url,
            data=payload,
            headers=headers,
            timeout=10,
            verify=False
        )

        if post_response.status_code in [200, 302]:
            text_lower = post_response.text.lower()
            if "invalid" in text_lower or "incorrect" in text_lower or "failed" in text_lower:
                print("Authentication rejected: Invalid username or password.")
                return False
            print("Authentication successful!")
            return True
        else:
            print(f"Authentication rejected (Status: {post_response.status_code}).")
            return False

    except Exception as e:
        print(f"Authentication error: {e}")
        return False