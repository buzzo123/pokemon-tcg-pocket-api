import requests
from bs4 import BeautifulSoup
import json
import re
import unicodedata


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
        return None
    
    description = card_desc.text.strip()
    
    return {"ultra_beast": ultra_beast_found, "description": description}


#set_code = "P-A"
#set_name= "Promo-A"

set_code = "A3b"
set_name = "A3b"

with open(f"../backend/data/{set_code}_cards.json", "r", encoding="utf-8") as file:
    card_list = json.load(file)

# Iterate through the JSON array and update with descriptions
for card in card_list:
    details = scrape_pokemon_details(set_name, card["id"], card["name"])
    if details:
        if isinstance(details, dict):
            # Ultra Beast found - add both ultra_beast status and description
            if details["ultra_beast"]:
                card["ultra_beast"] = True

            card["description"] = details["description"]
        else:
            # Regular description only
            card["description"] = details

with open(f"../{set_code}_cards.json", "w", encoding="utf-8") as f:
    json.dump(card_list, f, indent=4, ensure_ascii=False)