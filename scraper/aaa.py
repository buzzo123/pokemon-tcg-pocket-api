import json
import pytesseract
import re
from PIL import Image
from rapidfuzz import process, fuzz

# Set Tesseract path (Only needed for Windows users)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load JSON Data
with open("Master.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Flatten JSON dictionary (Key-Value pairs)
text_database = {key: value for key, value in data.items() if isinstance(value, str)}

# Define special words to replace
ignored_words = {"Asleep", "Burned", "Paralyzed", "Poisoned", "Confused", "Frozen"}

def clean_text(text):
    """
    Cleans text by:
    - Replacing ignored words with [Text:SpecialCondition id="0"].
    - Replacing ' with ’ for consistency.
    - Removing trailing periods.
    - Removing special characters like @, ç, ©, etc.
    """
    # Replace ignored words with the special condition pattern
    for word in ignored_words:
        text = re.sub(r'\b' + re.escape(word) + r'\b', '[Text:SpecialCondition id="0"]', text, flags=re.IGNORECASE)
    
    # Replace ' with ’ for consistency
    text = text.replace("'", "’")
    
    # Remove special characters (anything that is not a letter, number, or space)
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)

    # Remove trailing period if it exists
    text = re.sub(r'\.$', '', text)

    # Remove extra spaces created after word replacement
    return ' '.join(text.split())

def extract_text_from_image(image_path):
    """ Extract text from an image using Tesseract OCR and split it into phrases """
    image = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(image, lang="eng")

    # Split into separate lines (phrases), remove empty lines
    phrases = [line.strip() for line in extracted_text.split("\n") if line.strip()]
    
    # Clean each phrase
    cleaned_phrases = [clean_text(phrase) for phrase in phrases]

    return cleaned_phrases

def find_best_match(query_text, threshold=85):
    """
    Finds the best match for a given phrase in the JSON dictionary.
    Returns matches above the given similarity threshold.
    """
    matches = process.extract(query_text, text_database, scorer=fuzz.ratio, limit=3)
    return [match for match in matches if match[1] >= threshold]  # Filter by threshold

def main(image_path):
    # Extract and clean phrases from image
    extracted_phrases = extract_text_from_image(image_path)

    # Print extracted text
    print("\n📝 Extracted & Cleaned Phrases from Image:")
    print("-" * 40)
    for phrase in extracted_phrases:
        print(f"🔹 {phrase}")
    print("-" * 40)

    # Match each cleaned phrase separately
    for phrase in extracted_phrases:
        if phrase:  # Skip empty phrases after cleaning
            best_matches = find_best_match(phrase)

            if best_matches:
                print(f"\n🔍 Matches for: \"{phrase}\"")
                for match, score, key in best_matches:
                    print(f"🔹 Key: {key}\n🔸 Match Score: {score}%\n🔹 Value: {match}\n")
            else:
                print(f"❌ No close matches found for: \"{phrase}\"")

if __name__ == "__main__":
    image_path = "image.png"  # Replace with your image file
    main(image_path)
