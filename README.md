# Pokémon API

This is an Express.js-based API that serves Pokémon Pocket card data from JSON files.

## Features
- Retrieve all Pokémon Pocket cards
- Filter cards by type (Pokémon or Trainer)
- Retrieve cards by set (A1, A1A, A2, P-A)
- Retrieve a specific card by its number

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/pokemon-api.git
   cd pokemon-api
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
Returns the card from A2 set with ID 223.

## Data Source

The card data and images were scraped from:
```
https://limitlesstcg.com/
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
- [ ] Add pokémon card missing info: descriptions and infos