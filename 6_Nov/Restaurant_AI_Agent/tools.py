import json
from pathlib import Path

from langchain.tools import tool

BASE_DIR = Path(__file__).parent
RESTAURANTS_FILE  = BASE_DIR/"restaurants.json"

def get_restaurants():
    return json.loads(RESTAURANTS_FILE.read_text(encoding="utf-8"))


@tool
def search_restaurants(query: str) -> str:

    """Search restaurants by name or cuisine type."""

    names = get_restaurants()
    matches = []
    for w in names:
        if query.lower() in w['name'].lower()  or  query.lower() in w['cuisine'].lower():
             result = {
                        "id": w['id'],
                                    "name": w['name'],
                        "cuisine": w['cuisine'],
                        "location": w["location"],
                        "price_per_person": w["price_per_person"],
                        "available_seats": w['available_seats']
                                }
             matches.append(result)
    if not matches:
        return json.dumps({"error":"No such restaurant exit"})


    return json.dumps(matches) 



@tool
def calculate_dining_cost(restaurant_id: str, guests: int) -> str:
    """Estimate the total dining cost for a restaurant ID and number of guests. 
    This is only an estimate and does not make a reservation or payment."""
    if guests <= 0:
        return json.dumps({"error": "guests should be greater that 0"})
    for workshop in get_restaurants():
        if workshop["id"].upper() == restaurant_id.upper():
            total = workshop["price_per_person"] * guests
            result = {
                "name": workshop['name'],
                "guests": guests,
                "fee_per_person": workshop["price_per_person"],
                "total_fee": total,
            }
            return json.dumps(result)
    return json.dumps({'error':f"Restaurant '{restaurant_id}' not found."})

if __name__ == "__main__":
    print(search_restaurants.invoke({"query": "indian"}))
    print(search_restaurants.invoke({"query": "garden"}))
    print(search_restaurants.invoke({"query": "thai"}))
    print(calculate_dining_cost.invoke({"restaurant_id": "R101", "guests": 4}))
    print(calculate_dining_cost.invoke({"restaurant_id": "r103", "guests": 2}))
    print(calculate_dining_cost.invoke({"restaurant_id": "R999", "guests": 2}))
    print(calculate_dining_cost.invoke({"restaurant_id": "R101", "guests": 0}))
    print(calculate_dining_cost.invoke({"restaurant_id": "R104", "guests": 2}))

