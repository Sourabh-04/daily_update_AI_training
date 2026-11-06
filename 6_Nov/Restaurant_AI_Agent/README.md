# Restaurant AI Agent

**Date:** 6 November 2026

A command-line AI assistant, built with LangChain, that helps users find restaurants and estimate dining costs. It runs on a free model through OpenRouter.

The agent does **not** make reservations or take payments. It only searches and estimates.

## Features

- **Search restaurants:** finds restaurants by cuisine or name, with price per person and available seats.
- **Estimate dining cost:** works out the total cost for a restaurant ID and number of guests.
- **Seat warnings:** tells the user when a restaurant doesn't have enough free seats.
- **Stays on topic:** declines booking/payment requests and unrelated questions.
- **Conversation memory:** remembers the selected restaurant during a chat. Type `/new` to start a fresh conversation.

## Project structure

| File | Purpose |
|---|---|
| `agent.py` | Main app: the agent setup and chat loop |
| `tools.py` | Agent tools (search and cost estimate) |
| `restaurants.json` | Restaurant data (six fictional restaurants) |
| `requirements.txt` | Python dependencies |

## Tools

| Tool | Description |
|---|---|
| `search_restaurants(query)` | Searches restaurants by cuisine or name (case-insensitive) |
| `calculate_dining_cost(restaurant_id, guests)` | Returns `price_per_person × guests`, or an error if the ID doesn't exist or guests is 0 or less |

## Setup

1. Create and activate a virtual environment (Windows PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install the dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project folder. Get a free key at https://openrouter.ai/keys.
   ```
   OPENROUTER_API_KEY=your-api-key-here
   OPENROUTER_MODEL=google/gemma-4-31b-it:free
   ```
   Any OpenRouter `:free` model that supports tool calling will work.
4. Run the agent:
   ```powershell
   python agent.py
   ```

## Example conversation

`[TOOL]` lines show which tool the agent called and what it returned.

```
You: Show me Indian restaurants
[TOOL]: search_restaurants
Arguments: {'query': 'Indian'}
[TOOL RESULT]: [{"id": "R101", "name": "Spice Garden", "cuisine": "Indian", "location": "Hyderabad", "price_per_person": 800, "available_seats": 20}]

Agent: Here are the Indian restaurants I found:

**Spice Garden** (ID: R101)
- **Cuisine:** Indian
- **Location:** Hyderabad
- **Price per person:** ₹800
- **Available seats:** 20

This is the only Indian restaurant currently available in the search results. Would you like more details about Spice Garden or help with something else?

You: How much for 4 people there?
[TOOL]: calculate_dining_cost
Arguments: {'restaurant_id': 'R101', 'guests': 4}
[TOOL RESULT]: {"name": "Spice Garden", "guests": 4, "fee_per_person": 800, "total_fee": 3200}

Agent: For 4 people at **Spice Garden** (ID: R101), the estimated total cost is **₹3,200** (₹800 per person).

You: What about 3 people at Coastal Catch?
[TOOL]: search_restaurants
Arguments: {'query': 'Coastal Catch'}
[TOOL RESULT]: [{"id": "R104", "name": "Coastal Catch", "cuisine": "Seafood", "location": "Chennai", "price_per_person": 950, "available_seats": 0}]
[TOOL]: calculate_dining_cost
Arguments: {'restaurant_id': 'R104', 'guests': 3}
[TOOL RESULT]: {"name": "Coastal Catch", "guests": 3, "fee_per_person": 950, "total_fee": 2850}

Agent: For **3 people at Coastal Catch** (ID: R104):

- **Total cost:** ₹2,850 (₹950 per person)
- **However**, this restaurant currently has **0 available seats**, so it cannot accommodate a party of 3.

You: Book a table for me

Agent: I can't make bookings or reservations directly. However, I can help you with the following:

- **Spice Garden** (ID: R101) - Indian, Hyderabad, ₹800 per person, **20 seats available**
- **Coastal Catch** (ID: R104) - Seafood, Chennai, ₹950 per person, **0 seats available**

You: What's the weather today?

Agent: I don't have access to weather information. My capabilities are limited to helping with restaurant searches, cuisines, locations, prices, and dining cost estimates.
```

The second turn shows the agent remembering the restaurant ("there" → R101).

## Commands

| Command | Action |
|---|---|
| `/new` | Start a new conversation |
| `exit` | Quit |

## Notes

- Free OpenRouter models are rate-limited. If you see `Error code: 429`, wait a few seconds and try again, or switch `OPENROUTER_MODEL` to another free model.
- Guardrails (`guardrails.py`) are planned for a later update.
