"""Library tools used by the agent: search_books() and reserve_book()."""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOOKS_FILE = ROOT / "books.json"
RESERVATIONS_FILE = ROOT / "reservations.json"


# Helper: read a JSON file and return its data
def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


# Helper: write data back to a JSON file
def save_json(path: Path, data: list[dict]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# TOOL 1: Search books by title or keyword
def search_books(query: str) -> list[dict]:
    """Return books whose title, author or category contains the keyword."""
    keyword = query.strip().lower()
    if not keyword:
        return []

    books = load_json(BOOKS_FILE)
    matches = []
    for book in books:
        searchable = f"{book['title']} {book['author']} {book['category']}".lower()
        if keyword in searchable:
            matches.append({
                "id": book["id"],
                "title": book["title"],
                "author": book["author"],
                "category": book["category"],
                "available_copies": book["available_copies"],
                "status": "Available" if book["available_copies"] > 0 else "Not available",
            })
    return matches


# TOOL 2: Reserve a book for a customer
def reserve_book(book_id: int, customer_name: str, confirm: bool = False) -> dict:
    """Check availability; create the reservation only when confirm=True."""
    customer_name = customer_name.strip()
    if not customer_name:
        return {"success": False, "message": "Customer name is required."}

    try:
        book_id = int(book_id)
    except (TypeError, ValueError):
        return {"success": False, "message": f"Invalid book ID: {book_id!r}."}

    # STEP 1: Find the book
    books = load_json(BOOKS_FILE)
    book = next((b for b in books if b["id"] == book_id), None)
    if book is None:
        return {"success": False, "message": f"No book found with ID {book_id}."}

    # STEP 2: Never reserve when no copies are left
    if book["available_copies"] <= 0:
        return {"success": False,
                "message": f"'{book['title']}' has no available copies. Reservation not created."}

    # STEP 3: Ask for confirmation before changing any data
    if not confirm:
        return {"success": False,
                "needs_confirmation": True,
                "message": (f"Reserve '{book['title']}' (ID {book_id}) for {customer_name}? "
                            f"{book['available_copies']} copies available. Please confirm.")}

    # STEP 4: Save the reservation and reduce the copy count
    reservations = load_json(RESERVATIONS_FILE)
    reservation = {
        "reservation_id": max((r["reservation_id"] for r in reservations), default=0) + 1,
        "book_id": book_id,
        "title": book["title"],
        "customer_name": customer_name,
        "reserved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    reservations.append(reservation)
    book["available_copies"] -= 1

    save_json(RESERVATIONS_FILE, reservations)
    save_json(BOOKS_FILE, books)

    return {"success": True,
            "message": "Reservation created.",
            "reservation": reservation,
            "copies_left": book["available_copies"]}


# Quick manual test: python tools.py (does not change any data)
if __name__ == "__main__":
    for word in ["python", "history", "mockingbird", "cooking"]:
        print(f"\nSearch: {word!r}")
        results = search_books(word)
        if not results:
            print("  No matching books found.")
        for book in results:
            print(f"  [{book['id']}] {book['title']} by {book['author']} "
                  f"- {book['status']} ({book['available_copies']} copies)")

    print("\nReserve checks (confirm=False, nothing is saved):")
    for book_id in [101, 105, 999]:
        print(f"  ID {book_id}:", reserve_book(book_id, "Test User")["message"])
