import requests

def is_internet_active(proxy=None):
    """
    Checks if internet is active.
    If proxy is provided (e.g. on campus), checks through the proxy.
    Returns True if internet is reachable, False otherwise.
    """
    url = "http://clients3.google.com/generate_204"
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None

    try:
        response = requests.get(
            url,
            timeout=5,
            allow_redirects=False,
            proxies=proxies
        )
        # 204 means open internet is active
        return response.status_code == 204
    except requests.RequestException:
        return False

if __name__ == "__main__":
    if is_internet_active():
        print("Internet is active!")
    else:
        print("Internet is down or login required.")