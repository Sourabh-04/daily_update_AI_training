# E-commerce Multi-Agent System

A product recommendation assistant for an electronics store, built with **Microsoft Agent Framework**.
Three specialist agents run in sequence using `SequentialBuilder`. Each one uses its own tools and passes the conversation to the next.

## Workflow

```
Customer Request
      │
      ▼
Inventory Agent        → search_products()
      │
      ▼
Pricing Agent          → calculate_order_total()
      │
      ▼
Recommendation Agent   → (no tools, reasons over verified results)
      │
      ▼
Final Recommendation
```

## Project Structure

```
Ecommerce_Multi_Agent/
├── .env              # OpenRouter API key and model (not committed)
├── requirements.txt  # Python dependencies
├── products.json     # Product catalogue (32 products, P101–P132)
├── tools.py          # search_products, calculate_order_total
├── agents.py         # Creates the three agents
├── sequential.py     # Builds and runs the sequential workflow
└── test_tools.py     # Tests the tools directly, without any LLM
```

## Agents

| Agent | Tool | Responsibility |
|---|---|---|
| **InventoryAgent** | `search_products` | Understands the request, finds matching products, and reports ID, price, stock and rating. Marks out-of-stock items. |
| **PricingAgent** | `calculate_order_total` | Calculates verified totals for in-stock products, checks quantity against stock, and labels each product within or over budget. |
| **RecommendationAgent** | — | Recommends the highest-rated product that fits the budget and quantity. Breaks ties by lower cost. Never recommends unavailable products. |

All agents are told to use only tool-verified data and never to invent products, prices or stock.

## Tools

### `search_products(query)`
- Searches by product **name** or **category** (case-insensitive).
- Returns ID, name, category, price, stock and rating for each match.
- Returns `No products found matching '...'` when nothing matches.

### `calculate_order_total(product_id, quantity)`
- Looks up the product price from `products.json` and calculates the total.
- Rejects quantities that are zero, negative or not whole numbers.
- Reports out-of-stock and insufficient-stock cases.
- Returns `Product '...' does not exist.` for unknown IDs.

## Product Catalogue

`products.json` holds 32 products in 8 categories: Laptop, Smartphone, Tablet, Monitor, Headphones, Printer, Keyboard and Mouse.
Each product has `id`, `name`, `category`, `price_inr`, `stock` and `rating`.

## Setup

1. Install dependencies (inside your virtual environment):
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file:
   ```
   OPENROUTER_API_KEY=your_openrouter_key
   OPENROUTER_MODEL=openai/gpt-4o-mini
   ```
   Use a model that supports **tool calling** (filter by "Tools" on openrouter.ai/models).

The model client uses `OpenAIChatCompletionClient` pointed at `https://openrouter.ai/api/v1`, because OpenRouter fully supports the Chat Completions API.

## Running

Test the tools first (no API calls):
```
python test_tools.py
```

Run the multi-agent workflow:
```
python sequential.py
```

The output shows each agent's intermediate result, followed by the **FINAL RECOMMENDATION**.

## Example Requests

| Request | Expected behaviour |
|---|---|
| `I need 2 laptops under 130000 rupees` | Recommends **Atlas Work 14** (P104, rating 4.7, total ₹118,000) |
| `I want 5 Orion Pro 15 laptops` | Rejected: only 3 in stock |
| `Suggest headphones under 1000 rupees` | No product fits the budget, and the system says so |

## Key Concepts

- **Sequential orchestration:** `SequentialBuilder` runs agents in a fixed order with shared conversation context. Agents are not called one by one with separate `run()` statements.
- **Tool grounding:** prices and stock come only from tools, so agents can't make up data.
- **Separation of responsibilities:** each agent has one job and only the tools it needs.
