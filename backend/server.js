const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());

// Load JSON data from files
const loadJSON = (filename) => {
    const filePath = path.join(__dirname, 'data', filename);
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
};

const A1 = loadJSON('A1_cards.json');
const A1a = loadJSON('A1a_cards.json');
const A2 = loadJSON('A2_cards.json');
const A2a = loadJSON('A2a_cards.json');
const A2b = loadJSON('A2b_cards.json');
const P_A = loadJSON('P-A_cards.json');


// Combine all data
const allCards = [...A1, ...A1a, ...A2, ...A2a, ...A2b, ...P_A];

// Routes
app.get('/', (req, res) => {
    res.json(allCards);
});

app.get('/type/:type', (req, res) => {
    const { type } = req.params;
    const filteredCards = allCards.filter(card => card.type.toLowerCase() === type.toLowerCase());
    res.json(filteredCards);
});


app.get('/set/:set', (req, res) => {
    const { set } = req.params;
    const selectedSet = _getSet(set);

    if(set) {
        res.json(selectedSet);

    } else {
        return res.status(404).json({ error: 'Set not found' });
    }
});

app.get('/set/:set/:number', (req, res) => {
    const { set, number} = req.params;
    const selectedSet = _getSet(set);

    if(set) {
        const filteredCards = selectedSet.filter(card => card.id === number);
        res.json(filteredCards);

    } else {
        return res.status(404).json({ error: 'Card not found' });
    }
});

// Create server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});


const _getSet = (set) => {
    switch (set.toUpperCase()) {
        case 'A1':
            return A1;
        case 'A1A':
            return A1a;
        case 'A2':
            return A2;
        case 'A2A':
            return A2a;
        case 'A2B':
            return A2b;
        case 'P-A':
            return P_A;
            
        default:
            return undefined
}
}