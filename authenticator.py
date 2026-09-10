import requests
from bs4 import BeautifulSoup

def authenticate_ruccus(username, password):
    # This is the base URL the Ruckus controller redirects you to
    portal_url = "https://ironport2.iiita.ac.in" # Or your specific Ruckus login page URL
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # Step 1: Perform a GET request to the portal to grab the fresh HTML and tokens
        print("Fetching captive portal tokens...")
        response = requests.get(portal_url, headers=headers, timeout=5, verify=False)
        
        if response.status_code != 200:
            print(f"Failed to reach portal. Status code: {response.status_code}")
            return False

        # Step 2: Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Step 3: Extract the dynamic hidden input tokens from the form
        # We search for HTML <input> tags by their 'name' attribute and grab their 'value'
        login_form_token = soup.find('input', {'name': 'LoginFromForm'})['value']
        uip_token = soup.find('input', {'name': 'uip'})['value']
        client_mac_token = soup.find('input', {'name': 'client_mac'})['value']
        zone_token = soup.find('input', {'name': 'zone'})['value']

        # Step 4: Construct the final payload using both static config and dynamic scraped tokens
        payload = {
            "RequestType": "Login",
            "uip": uip_token,
            "client_mac": client_mac_token,
            "wlan": "13",
            "zone": zone_token,
            "proxy": "1",
            "url": "https://ironport2.iiita.ac.in",
            "AppResponseCode": "100",
            "LoginFromForm": login_form_token,
            "UE-Username": username,
            "UE-Password": password
        }

        # Step 5: Fire the POST request to log in
        print("Sending authentication payload...")
        post_res = requests.post(portal_url, data=payload, headers=headers, timeout=5, verify=False)

        if post_res.status_code == 200 or post_res.status_code == 302:
            print("Authentication successful! Session active.")
            return True
        else:
            print("Authentication rejected by server.")
            return False

    except Exception as e:
        print(f"An error occurred during authentication: {e}")
        return False