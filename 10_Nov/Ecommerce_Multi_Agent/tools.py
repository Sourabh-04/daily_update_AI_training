import json
from pathlib import Path

from agent_framework import tool


DATA_FILE = Path(__file__).parent / "products.json"

def load_products():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


# Tool 1: Search products
@tool(approval_mode="never_require")
def search_products(query: str) -> str:
    """Find products whose name or category matches the query (e.g. 'Laptop', 'Orion')."""

    print(f"[TOOL CALLED] search_products: {query}")

    q = query.lower().strip()

    matches = [
        {
            "id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "price_inr": p["price_inr"],
            "stock": p["stock"],
            "rating": p["rating"],
        }
        for p in load_products()
        if q in p["name"].lower() or q in p["category"].lower()
    ]

    if not matches:
        return f"No products found matching '{query}'."

    return json.dumps(matches)


# Tool 2: Calculate order total
@tool(approval_mode="never_require")
def calculate_order_total(product_id: str, quantity: int) -> str:
    """Calculate the total cost for a product ID and quantity, checking stock availability."""

    print(f"[TOOL CALLED] calculate_order_total: {product_id}, {quantity}")

    # Reject invalid quantities (non-integers, zero, negatives)
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        return "Invalid quantity. Quantity must be a whole number of 1 or more."

    # Find the product
    product = next(
        (p for p in load_products() if p["id"].upper() == product_id.strip().upper()),
        None,
    )

    if product is None:
        return f"Product '{product_id}' does not exist."

    # Verify stock
    if product["stock"] == 0:
        return f"{product['name']} ({product['id']}) is out of stock."

    if quantity > product["stock"]:
        return (
            f"Insufficient stock for {product['name']} ({product['id']}). "
            f"Requested {quantity}, only {product['stock']} available."
        )

    # Calculate total
    return json.dumps({
        "id": product["id"],
        "name": product["name"],
        "quantity": quantity,
        "unit_price_inr": product["price_inr"],
        "total_inr": product["price_inr"] * quantity,
        "stock_available": product["stock"],
    })
