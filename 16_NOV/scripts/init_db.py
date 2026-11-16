"""Create the trips table and insert sample trips.
Run from the project root:  python -m scripts.init_db
"""
from datetime import date, timedelta

from app import db


def d(days_from_today: int) -> str:
    return (date.today() + timedelta(days=days_from_today)).isoformat()


# Dates are relative to today, so the samples always fall inside
# Open-Meteo's ~16-day forecast window (except the deliberate failure case).
SAMPLE_TRIPS = [
    ("EMP104", "Jaipur",    d(3),  d(5),  "Client meeting"),
    ("EMP104", "Mumbai",    d(8),  d(10), "Quarterly review"),
    ("EMP221", "Bengaluru", d(2),  d(4),  "Team workshop"),
    ("EMP221", "London",    d(40), d(44), "Conference"),   # beyond forecast horizon -> failure demo
]


def main() -> None:
    db.init_db()
    with db.get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM trips").fetchone()[0]

    if count > 0:
        print(f"Database already has {count} trips - skipping seed.")
    else:
        for emp, dest, start, end, purpose in SAMPLE_TRIPS:
            trip = db.create_trip(emp, dest, start, end, purpose)
            print("Created:", trip["trip_id"], trip["employee_id"], trip["destination"],
                  trip["start_date"], "->", trip["end_date"])

    print("EMP104 trips:", [t["destination"] for t in db.list_trips("EMP104")])


if __name__ == "__main__":
    main()
