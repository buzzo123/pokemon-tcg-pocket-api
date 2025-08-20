import requests
from bs4 import BeautifulSoup
import json
import re
import unicodedata
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
try:
    import cloudscraper  # Optional, helps bypass some anti-bot protections
except ImportError:
    cloudscraper = None
try:
    from curl_cffi import requests as curl_requests  # Strong Cloudflare/anti-bot bypass
except ImportError:
    curl_requests = None


RARITY_MAP = {
    "Common": "◊",
    "Uncommon": "◊◊",
    "Rare": "◊◊◊",
    "Double Rare": "◊◊◊◊",
    "Art Rare": "☆",
    "Super Rare": "☆☆",
    "Special Art Rare": "☆☆",
    "Immersive Rare": "☆☆☆",
    "Crown Rare": "♔",
    "Shiny Super Rare": "✸✸",
    "Shiny": "✸",
}

def normalize_name(name):
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')  # Remove accents
    name = name.lower().replace(" ", "-")
    name = re.sub(r"[^a-zA-Z0-9-]", "", name)
    return name

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) "
        "Gecko/20100101 Firefox/127.0"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
]

def _sec_ch_ua_from_user_agent(user_agent):
    if "Chrome" in user_agent or "Chrom" in user_agent:
        return '"Chromium";v="126", "Not;A=Brand";v="99", "Google Chrome";v="126"'
    if "Firefox" in user_agent:
        # Firefox typically does not send sec-ch-ua headers; return empty to skip
        return None
    return '"Chromium";v="126", "Not;A=Brand";v="99", "Google Chrome";v="126"'

def _build_headers(set_name, user_agent):
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Referer": f"https://www.pokemon-zone.com/cards/{set_name}/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }
    sec_ch = _sec_ch_ua_from_user_agent(user_agent)
    if sec_ch:
        headers.update({
            "sec-ch-ua": sec_ch,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        })
    return headers

def _choose_user_agent():
    return random.choice(USER_AGENTS)

def _create_session():
    # Prefer cloudscraper if available
    if cloudscraper is not None:
        session = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
    else:
        session = requests.Session()
    try:
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
    except TypeError:
        # Older urllib3 versions use method_whitelist
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def _warm_up_session(session, set_name):
    # Hit homepage and the set page to collect cookies/session
    warm_urls = [
        "https://www.pokemon-zone.com/",
        f"https://www.pokemon-zone.com/cards/{set_name}/",
    ]
    for url in warm_urls:
        try:
            ua = _choose_user_agent()
            headers = _build_headers(set_name, ua)
            session.get(url, headers=headers, timeout=20)
            time.sleep(random.uniform(0.6, 1.2))
        except requests.RequestException:
            pass

def _fetch_with_curl_cffi(url, set_name):
    if curl_requests is None:
        return None
    # Try multiple impersonations
    personas = [
        "chrome120",
        "chrome116",
        "chrome110",
        "chrome104",
        "edge101",
        "safari17_0",
        "safari15_5",
    ]
    for idx, persona in enumerate(personas, start=1):
        try:
            resp = curl_requests.get(
                url,
                impersonate=persona,
                headers=_build_headers(set_name, _choose_user_agent()),
                timeout=25,
            )
            if resp.status_code == 200 and resp.text:
                return resp.text
            if resp.status_code in (403, 429):
                time.sleep(1.0 + 0.3 * idx)
                continue
            if 500 <= resp.status_code < 600:
                time.sleep(0.8)
                continue
        except Exception:
            continue
    return None

def scrape_pokemon_details(set, pokemon_id, name, session=None):
    formatted_name = normalize_name(name)
    url = f"https://www.pokemon-zone.com/cards/{set}/{pokemon_id}/{formatted_name}/"
    
    if session is None:
        session = _create_session()
    
    # First try with curl_cffi to bypass Cloudflare if available
    html_text = _fetch_with_curl_cffi(url, set)
    if html_text is None:
        # Attempt with rotating headers and exponential backoff if 403/429
        attempts = 5
        response = None
        for attempt in range(1, attempts + 1):
            headers = _build_headers(set, _choose_user_agent())
            try:
                response = session.get(url, headers=headers, timeout=25)
            except requests.RequestException as exc:
                if attempt == attempts:
                    print(f"Request failed for {url}: {exc}")
                    return None
            else:
                if response.status_code == 200:
                    break
                if response.status_code in (403, 429):
                    wait_s = min(14, 1.8 * (2 ** (attempt - 1))) + random.uniform(0, 0.9)
                    print(f"{response.status_code} for {url}. Retrying in {wait_s:.1f}s (attempt {attempt}/{attempts})...")
                    time.sleep(wait_s)
                    continue
                if 500 <= response.status_code < 600:
                    wait_s = 1.2 + random.uniform(0, 0.7)
                    print(f"Server error {response.status_code} for {url}. Retry in {wait_s:.1f}s (attempt {attempt}/{attempts})...")
                    time.sleep(wait_s)
                    continue
                # Other non-OK status codes: no point retrying
                print(f"Failed to fetch {url} - Status code: {response.status_code}")
                return None

        if not response or response.status_code != 200:
            print(f"Failed to fetch {url} - Status code: {response.status_code if response else 'N/A'}")
            return None
        html_text = response.text
    
    soup = BeautifulSoup(html_text, "html.parser")
    
    card_desc = soup.select_one(".card-detail__content .fst-italic")

    stats = soup.select_one(".card-detail__header .fw-bold")

    rarity = soup.select_one(".card-detail__aside .card-collection-summary__meta")
    
    # Extract rarity from the meta div
    rarity_text = None
    if rarity:
        # Get all span elements with class card-collection-summary__meta-item
        rarity_items = rarity.select(".card-collection-summary__meta-item")
        if len(rarity_items) >= 2:
            # The second element should be the rarity
            rarity_text = rarity_items[1].text.strip()
    
    # Map rarity text to rarity code if it exists in RARITY_MAP
    rarity_code = None
    if rarity_text and rarity_text in RARITY_MAP:
        rarity_code = {"symbol": RARITY_MAP[rarity_text], "text": rarity_text}

    ultra_beast_found = False
    if stats:
        stats_text = stats.text.strip()
        if "|" in stats_text:
            # Split by pipe and trim each part
            stats_parts = [part.strip() for part in stats_text.split("|")]
            # Check if "Ultra Beast" is in the array
            if "Ultra Beast" in stats_parts:
                ultra_beast_found = True
        else:
            # Check if the single stat contains "Ultra Beast"
            if "Ultra Beast" in stats_text:
                ultra_beast_found = True
    else:
        print("Stats not found")

    if not card_desc:
        print("Card details not found.", url)
    
    result = {"ultra_beast": ultra_beast_found}

    if card_desc:
        result["description"] = card_desc.text.strip()
    if rarity_code:
        result["rarity"] = rarity_code
    
    return result


#set_code = "P-A"
#set_name= "Promo-A"

set_code = "A4"
set_name = "a4"

with open(f"../backend/data/{set_code}_cards.json", "r", encoding="utf-8") as file:
    card_list = json.load(file)

session = _create_session()
_warm_up_session(session, set_name)

# Iterate through the JSON array and update with descriptions
for card in card_list:
    details = scrape_pokemon_details(set_name, card["id"], card["name"], session=session)
    if details:
        if isinstance(details, dict):
            # Ultra Beast found - add both ultra_beast status and description
            if details.get("ultra_beast"):
                card["ultra_beast"] = True
            if details.get("rarity"):
                card["rarity"] = details["rarity"]
            if details.get("description"):
                card["description"] = details["description"]

    # Polite delay with slight jitter to reduce risk of being blocked
    time.sleep(random.uniform(1.5, 3.0))


with open(f"../{set_code}_cards.json", "w", encoding="utf-8") as f:
    json.dump(card_list, f, indent=4, ensure_ascii=False)