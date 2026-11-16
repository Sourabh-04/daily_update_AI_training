from langchain_core.tools import tool

from app import db
from app.weather import get_forecast


@tool
def get_trip(trip_id: str):
    """Look up a saved business trip by its trip ID (for example TRIP-3F9A1C2B)."""
    return db.get_trip(trip_id) or {"error": f"Trip {trip_id} not found."}


@tool
def list_trips(employee_id: str):
    """List all saved trips for an employee ID (for example EMP104).
    Use this to find the employee's destination and travel dates."""
    return db.list_trips(employee_id) or {"error": f"No trips found for employee {employee_id}."}


@tool
def get_weather(city: str, start_date: str, end_date: str):
    """Get the daily weather forecast (temperature, precipitation, rain chance)
    for a city between start_date and end_date, in YYYY-MM-DD format.
    Always use the destination and dates from the saved trip."""
    return get_forecast(city, start_date, end_date)


TOOLS = [get_trip, list_trips, get_weather]
