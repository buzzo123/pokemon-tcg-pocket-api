import requests
from bs4 import BeautifulSoup
import json
import re
import unicodedata


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

def scrape_pokemon_details(set, pokemon_id, name):
    formatted_name = normalize_name(name)
    url = f"https://www.pokemon-zone.com/cards/{set}/{pokemon_id}/{formatted_name}/"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url} - Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
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

set_code = "A1"
set_name = "a1"

with open(f"../backend/data/{set_code}_cards.json", "r", encoding="utf-8") as file:
    card_list = json.load(file)

# Iterate through the JSON array and update with descriptions
for card in card_list:
    details = scrape_pokemon_details(set_name, card["id"], card["name"])
    if details:
        if isinstance(details, dict):
            # Ultra Beast found - add both ultra_beast status and description
            if details.get("ultra_beast"):
                card["ultra_beast"] = True
            if details.get("rarity"):
                card["rarity"] = details["rarity"]
            if details.get("description"):
                card["description"] = details["description"]


with open(f"../{set_code}_cards.json", "w", encoding="utf-8") as f:
    json.dump(card_list, f, indent=4, ensure_ascii=False)