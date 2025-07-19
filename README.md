# Pokémon Pocket API

This is an Express.js-based API that serves Pokémon Pocket card data from JSON files. The card data contains all information on the cards, including description, height, weight, and species.

## Features
- Retrieve all Pokémon Pocket cards
- Filter cards by type (Pokémon or Trainer)
- Retrieve cards by set (A1, A1A, A2, A2a, A2b, A3, A3a, P-A)
- Retrieve a specific card by its number

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/buzzo123/pokemon-tcg-pocket-api.git
   cd pokemon-tcg-pocket-api/backend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the server:
   ```sh
   npm start
   ```

## API Endpoints

### Get all cards
```sh
GET /
```
Returns all available Pokémon cards.

### Get cards by type
```sh
GET /type/:type
```
Example:
```sh
GET type/Pokémon
```
Returns all Pokémon-type cards.

### Get cards by set
```sh
GET /set/:set
```
Example:
```sh
GET /set/A2
```
Returns all cards from the A2 set.

### Get cards by number
```sh
GET /set/:set/:number
```
Example:
```sh
GET /set/A2/100
```
Returns the card from A2 set with ID 100.

## Data Structure

Each card in the JSON files contains the following basic structure:

```json
{
  "image": "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/pocket/A1/A1_001_EN.webp",
  "type": "Pokémon",
  "name": "Bulbasaur",
  "energy": "Grass",
  "hp": "70",
  "category": "Basic",
  "evolvesfrom": "",
  "attacks": [
    {
      "energy_cost": ["Grass", "Colorless"],
      "name": "Vine Whip",
      "attack": "40",
      "effect": ""
    }
  ],
  "weakness": "Fire",
  "retreat": "1",
  "artist": "Narumi Sato",
  "set": {
    "name": "Genetic Apex",
    "code": "A1",
    "pack": "Mewtwo"
  },
  "id": "1",
  "rarity": {
    "symbol": "◊",
    "text": "Common"
  },
  "description": "There is a plant seed on its back right from the day this Pokémon is born. The seed slowly grows larger.",
  "info": {
    "national_pokedex": "0001",
    "species": "Seed Pokémon",
    "height": "0.7 m / 2'04\"",
    "weight": "6.9 kg / 15.2 lbs."
  }
}
```

### Field Descriptions:
- **image**: URL to the card image
- **type**: Card type (Pokémon or Trainer)
- **name**: Pokémon or Trainer card name
- **energy**: Energy type of the Pokémon
- **hp**: Hit Points of the Pokémon
- **category**: Evolution stage (Basic, Stage 1, Stage 2, etc.)
- **evolvesfrom**: Name of the Pokémon this evolves from (if applicable)
- **attacks**: Array of attack objects with energy cost, name, damage, and effects
- **weakness**: Type weakness of the Pokémon
- **retreat**: Retreat cost (number of energy required to retreat)
- **artist**: Card artist name
- **set**: Object containing set information (name, code, pack)
- **id**: Unique card identifier within the set
- **rarity**: Object containing rarity symbol and text
- **description**: Card description text
- **info**: Object containing Pokémon information (Pokedex number, species, height, weight)

All JSON data files are located in the `backend/data/` folder.

## Data Source

The card data and images were scraped from:
```
https://limitlesstcg.com/
https://www.pokemon-zone.com/
https://pokemon.fandom.com/
```

## Project Structure
```
/backend
│── data/
│   ├── A1_cards.json
│   ├── A1a_cards.json
│   ├── A2_cards.json
│   ├── P-A_cards.json
│── server.js
│── package.json
│── README.md
│── .gitignore
```



## TODOs
- [ ] Implement other endpoints
