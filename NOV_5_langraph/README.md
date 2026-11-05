# Workshop AI Agent

**Date:** 5 November 2026

A command-line AI assistant, built with LangChain, that answers questions about training workshops, calculates fees and applies coupon discounts.

## Features

- **List all workshops:** shows every available workshop.
- **Find the cheapest workshop:** returns the workshop with the lowest fee.
- **Search workshops:** finds workshops by keyword in the title.
- **Calculate fees:** works out the total fee for a given number of participants.
- **Coupon discounts:** a valid coupon code takes 10% off the total.
- **Guardrails:** blocks input that contains emails or phone numbers and redacts them from the agent's replies.
- **Conversation memory:** the agent remembers earlier messages in a chat. Type `/new` to start a fresh conversation.

## Project structure

| File | Purpose |
|---|---|
| `agent.py` | Main app: the agent setup and chat loop |
| `tool.py` | Agent tools (list, cheapest, search, fee and coupon) |
| `guardrails.py` | PII detection and output cleaning |
| `workshops.json` | Workshop data |
| `coupons.json` | Valid coupon codes |
| `requirements.txt` | Python dependencies |

## Tools

| Tool | Description |
|---|---|
| `list_all_workshops()` | Returns all workshops |
| `find_cheapest_workshop()` | Returns the workshop with the lowest fee |
| `search_workshops(keyword)` | Searches workshops by title |
| `calculate_workshop_fee(workshop_id, participants, coupon_code="")` | Calculates the total fee and applies a coupon if one is given |

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
3. Create a `.env` file in the project folder:
   ```
   OPENAI_API_KEY=your-api-key-here
   OPENAI_MODEL=gpt-4o-mini
   ```
4. Run the agent:
   ```powershell
   python agent.py
   ```

## Example prompts

- `Show all workshops`
- `Which is the cheapest workshop?`
- `Fee for 4 people for Python Fundamentals with coupon SAVE10`

Example result: 4 × ₹3,000 = ₹12,000. The 10% discount (₹1,200) brings the **final fee to ₹10,800**.

## Coupon codes

The valid codes are listed in `coupons.json`: `SAVE10`, `WELCOME10` and `STUDENT10`. Each gives 10% off. Codes are not case-sensitive. If a code is invalid, the agent says so and shows the full fee.

## Commands

| Command | Action |
|---|---|
| `/new` | Start a new conversation |
| `exit` | Quit |
