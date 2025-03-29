import requests
from bs4 import BeautifulSoup
import json
import unicodedata
import re

def normalize_name(name):
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')  # Remove accents
    name = name.replace(" ", "_")  # Replace spaces with underscores
    # name = re.sub(r"[^a-zA-Z0-9_]", "", name)  # Remove special characters except underscores
    return name

def scrape_pokemon_fandom(name):
    formatted_name = normalize_name(name)
    url = f"https://pokemon.fandom.com/wiki/{formatted_name}"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url} - Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    national_pokedex = soup.select_one('div[data-source="Row 11 info"] div')
    species = soup.select_one('div[data-source="Row 4 info"] div')
    htwt = soup.select('div[data-source="Row 5 info"] div dl dd')
    
    if not national_pokedex or not species or not htwt:
        print(f"infos not found on the page. url: {url}")
        return None

    return {
        "national_pokedex": national_pokedex.text.strip(),
        "species": species.text.strip(),
        "height": htwt[0].text.strip(),
        "weight": htwt[1].text.strip()
    }

set_code = "A2b"

with open(f"../backend/data/{set_code}_cards.json", "r", encoding="utf-8") as file:
    card_list = json.load(file)

# Iterate through the JSON array and update with scraped data
for card in card_list:
    infos = scrape_pokemon_fandom(card["name"])
    if infos:
        card["info"] = infos

# Save updated JSON back to file
with open(f"{set_code}_cards.json", "w", encoding="utf-8") as f:
    json.dump(card_list, f, indent=4, ensure_ascii=False)
