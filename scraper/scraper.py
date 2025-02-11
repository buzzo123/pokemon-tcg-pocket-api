import requests
from bs4 import BeautifulSoup
import json
import time
import re

def scrape_card(set_code, card_number):
    url = f"https://pocket.limitlesstcg.com/cards/{set_code}/{card_number}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Card {card_number} not found, stopping...")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    card_data = {}
    
    # Card Image
    img_tag = soup.select_one(".card-image img")
    if img_tag:
        card_data["image"] = img_tag["src"]
    
    # Card Type (from .card-text-type)
    type_tag = soup.select_one(".card-text-type")
    
    # Determine if it is a Pokémon or Trainer card
    if "Pokémon" in type_tag.text:
        card_data["type"] = "Pokémon"
    elif "Trainer" in type_tag.text:
        card_data["type"] = "Trainer"
    else:
        card_data["type"] = None

    # Category & Evolves From (for Pokémon only)
    if card_data["type"] == "Pokémon":
            # Name, Type, HP (Card Type from .card-text-type)
        title_tag = soup.select_one(".card-text-title")
        if title_tag:
            parts = [p.strip() for p in title_tag.text.split(" - ")]
            card_data["name"] = parts[0]
            card_data["energy"] = parts[1]
            card_data["hp"] = parts[2].replace(" HP", "") if len(parts) > 2 else ""
        category_text = re.sub(r'\s+', ' ', type_tag.text.replace("\n", " ")).replace("Pokémon -", "").replace("Evolves from", "").strip()
        parts = [line.strip() for line in category_text.split("-")]
        card_data["category"] = parts[0] if parts else ""
        card_data["evolvesfrom"] = parts[1] if len(parts) > 1 else ""
        
        # Attacks
        attacks = []
        for attack in soup.select(".card-text-attack"):
            attack_info = attack.select_one(".card-text-attack-info")
            attack_effect = attack.select_one(".card-text-attack-effect")
            energy_symbols = attack_info.select_one(".ptcg-symbol")
            energy_cost = list(energy_symbols.text.strip()) if energy_symbols else []
            
            attack_name = ""
            attack_power = ""
            if attack_info:
                attack_text = attack_info.text.strip().replace(energy_symbols.text.strip(), "").strip()
                match = re.search(r"(.*?)(\d+[+x]*)$", attack_text)
                if match:
                    attack_name = match.group(1).strip()
                    attack_power = match.group(2).strip()
                else:
                    attack_name = attack_text
                    attack_power = ""
            
            attack_data = {
                "energy_cost": energy_cost,
                "name": attack_name,
                "attack": attack_power,
                "effect": attack_effect.text.strip() if attack_effect else ""
            }
            attacks.append(attack_data)
        card_data["attacks"] = attacks
        
        # Weakness & Retreat Cost
        wrr_tag = soup.select_one(".card-text-wrr")
        if wrr_tag:
            details = [line.strip() for line in wrr_tag.text.split("\n") if line.strip()]
            card_data["weakness"] = details[0].split(": ")[1] if len(details) > 0 else ""
            card_data["retreat"] = details[1].split(": ")[1] if len(details) > 1 else ""
    
    # For Trainer Cards (or other types)
    elif card_data["type"] == "Trainer":
        title_tag = soup.select_one(".card-text-title")
        if title_tag:
            parts = [p.strip() for p in title_tag.text.split(" - ")]
            card_data["name"] = parts[0]
        category_text = re.sub(r'\s+', ' ', type_tag.text.replace("\n", " ")).replace("Trainer -", "").strip()
        parts = [line.strip() for line in category_text.split("-")]
        card_data["category"] = parts[0] if parts else ""
        card_text_sections = soup.select(".card-text .card-text-section")
        # Check if there are at least two sections
        if len(card_text_sections) >= 2:
            second_section = card_text_sections[1]  
            card_data["effect"] = second_section.text.strip()
        else:
            print("Not enough card-text-sections found")

    # Artist
    artist_tag = soup.select_one(".card-text-artist a")
    if artist_tag:
        card_data["artist"] = artist_tag.text.strip()
    
    # Set Details
    set_info = soup.select_one(".card-prints-current .prints-current-details span.text-lg")
    if set_info:
        card_data["set"] = set_info.text.strip()
    
    # Card Number & Rarity
    card_num_tag = soup.select_one(".card-prints-current .prints-current-details span:nth-of-type(2)")
    if card_num_tag:
        num_parts = card_num_tag.text.strip().split(" · ")
        card_data["id"] = num_parts[0].replace("#", "").strip()
        card_data["rarity"] = num_parts[1].strip() if len(num_parts) > 1 else ""
    
    return card_data

def scrape_set(set_code, init_card = 1, max_cards=100):
    all_cards = []
    for card_number in range(init_card, max_cards + 1):
        card_data = scrape_card(set_code, card_number)
        if not card_data:
            break
        all_cards.append(card_data)
        time.sleep(1)  # To avoid getting blocked by the server
    
    with open(f"{set_code}_cards.json", "w", encoding="utf-8") as f:
        json.dump(all_cards, f, indent=4, ensure_ascii=False)
    
    print(f"Scraped {len(all_cards)} cards from set {set_code}.")

# Example usage
scrape_set("P-A", init_card = 1, max_cards=41)
