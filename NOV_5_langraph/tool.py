import json
from pathlib import Path

from langchain.tools import tool

BASE_DIR = Path(__file__).parent
WORKSHOPS_FILE = BASE_DIR / "workshops.json"
COUPONS_FILE = BASE_DIR / "coupons.json"


def get_workshops():
    return json.loads(WORKSHOPS_FILE.read_text(encoding="utf-8"))


def get_coupons():
    return json.loads(COUPONS_FILE.read_text(encoding="utf-8"))


def find_coupon(code: str):
    """Return the coupon dict if the code is valid (case-insensitive), else None."""
    code = code.strip().upper()
    for coupon in get_coupons():
        if coupon["code"].upper() == code:
            return coupon
    return None


@tool
def list_all_workshops() -> str:
    """List all available workshops with their id, title, duration and fee."""
    return json.dumps(get_workshops())


@tool
def find_cheapest_workshop() -> str:
    """Find the workshop with the lowest fee."""
    workshops = get_workshops()
    if not workshops:
        return "No workshops available."
    cheapest = min(workshops, key=lambda w: w["fee"])
    return json.dumps(cheapest)


@tool
def search_workshops(keyword: str) -> str:
    """Search available workshops by title."""
    matches = [
        w for w in get_workshops()
        if keyword.lower() in w["title"].lower()
    ]
    return json.dumps(matches)


@tool
def calculate_workshop_fee(
    workshop_id: str,
    participants: int,
    coupon_code: str = ""
) -> str:
    """Calculate the total fee for a workshop and participant count.
    Optionally pass a coupon_code to apply a discount."""
    for workshop in get_workshops():
        if workshop["id"].upper() == workshop_id.upper():
            total = workshop["fee"] * participants
            result = {
                "workshop": workshop["title"],
                "participants": participants,
                "fee_per_person": workshop["fee"],
                "total_fee": total,
            }

            if coupon_code:
                coupon = find_coupon(coupon_code)
                if coupon:
                    discount = total * coupon["discount_percent"] / 100
                    result["coupon_code"] = coupon["code"]
                    result["discount_percent"] = coupon["discount_percent"]
                    result["discount_amount"] = discount
                    result["final_fee"] = total - discount
                else:
                    result["coupon_error"] = f"Coupon '{coupon_code}' is invalid."
                    result["final_fee"] = total
            else:
                result["final_fee"] = total

            return json.dumps(result)

    return "Workshop not found."


if __name__ == "__main__":
    print(list_all_workshops.invoke({}))
    print(find_cheapest_workshop.invoke({}))
    print(search_workshops.invoke({"keyword": "Python"}))
    print(calculate_workshop_fee.invoke({"workshop_id": "W101", "participants": 4}))
    print(calculate_workshop_fee.invoke({"workshop_id": "W101", "participants": 4, "coupon_code": "SAVE10"}))
    print(calculate_workshop_fee.invoke({"workshop_id": "W101", "participants": 4, "coupon_code": "FAKE"}))
