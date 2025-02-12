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

    if not card_desc:
        print("Card details not found.", url)
        return None
    
    return card_desc.text.strip()



set_code = "A1a"

with open(f"../backend/data/{set_code}_cards.json", "r", encoding="utf-8") as file:
    card_list = json.load(file)

# Iterate through the JSON array and update with descriptions
for card in card_list:
    details = scrape_pokemon_details(set_code, card["id"], card["name"])
    if details:
        # print(f"{pokemon['name'].title()} details: {details}\n")
        card["description"] = details

with open(f"../{set_code}_cards.json", "w", encoding="utf-8") as f:
    json.dump(card_list, f, indent=4, ensure_ascii=False)