"""Test both tools directly, without any agent or LLM."""

from tools import search_products, calculate_order_total


def show(label, result):
    print(f"\n=== {label} ===")
    print(result)


# ---- Tool 1: search_products ----
show("Search by category: Laptop", search_products("Laptop"))
show("Search by name: Orion", search_products("Orion"))
show("Search case-insensitive: monitor", search_products("monitor"))
show("Search no match: Camera Drone", search_products("Camera Drone"))

# ---- Tool 2: calculate_order_total ----
show("Valid order: P101 x 2", calculate_order_total("P101", 2))
show("Lowercase ID: p121 x 3", calculate_order_total("p121", 3))
show("Exact stock: P102 x 3", calculate_order_total("P102", 3))
show("Insufficient stock: P102 x 5", calculate_order_total("P102", 5))
show("Out of stock: P103 x 1", calculate_order_total("P103", 1))
show("Zero quantity: P101 x 0", calculate_order_total("P101", 0))
show("Negative quantity: P101 x -2", calculate_order_total("P101", -2))
show("Unknown product: P999 x 1", calculate_order_total("P999", 1))
