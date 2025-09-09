import argparse
import os
import sys
import json

# Ensure local imports resolve when invoked directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def run_pipeline(set_code, set_name, init_card, max_cards):
    # Paths
    backend_data_dir = os.path.join(REPO_ROOT, "backend", "data")
    os.makedirs(backend_data_dir, exist_ok=True)

    step1_output = os.path.join(backend_data_dir, f"{set_code}_cards.json")
    step2_output = os.path.join(backend_data_dir, f"{set_code}_cards_desc.json")
    final_output = os.path.join(backend_data_dir, f"{set_code}_cards_full.json")

    # Step 1: scrape list
    from scraper.scrap_init import scrape_set  # type: ignore
    scrape_set(set_code, init_card=init_card, max_cards=max_cards, output_path=step1_output)

    # Step 2: enrich descriptions/rarity
    from scraper.scrap_desc import enrich_descriptions  # type: ignore
    enrich_descriptions(step1_output, step2_output, set_code, set_name)

    # Step 3: fandom infos
    from scraper.scrap_info import enrich_infos  # type: ignore
    enrich_infos(step2_output, final_output)

    # Optionally also copy final to the canonical name used by backend
    canonical_output = os.path.join(backend_data_dir, f"{set_code}_cards.json")
    try:
        with open(final_output, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(canonical_output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

    return final_output

#set_code = "P-A"
#set_name= "Promo-A"
def main():
    parser = argparse.ArgumentParser(description="Run full scraping pipeline for a set")
    parser.add_argument("set_code", help="Set code, e.g., A4a")
    parser.add_argument("set_name", help="Set slug used on pokemon-zone, e.g., a4a")
    parser.add_argument("--init", dest="init_card", type=int, default=1, help="Starting card number")
    parser.add_argument("--max", dest="max_cards", type=int, default=100, help="Max card number to attempt")

    args = parser.parse_args()

    output = run_pipeline(args.set_code, args.set_name, args.init_card, args.max_cards)
    print(f"Pipeline completed. Output: {output}")


if __name__ == "__main__":
    main()


