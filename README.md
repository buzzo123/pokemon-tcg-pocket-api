# Pokémon Pocket API

This is an Express.js-based API that serves Pokémon Pocket card data from JSON files. The card data contains all information on the cards, including description, height, weight, and species.

## Features
- Retrieve all Pokémon Pocket cards
- Filter cards by type (Pokémon or Trainer)
- Retrieve cards by set (A1, A1A, A2, A2a, A2b, A3, P-A)
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
