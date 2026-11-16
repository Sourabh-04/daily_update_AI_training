from fastapi import FastAPI, HTTPException

from app import db, memory
from app.assistant import ask
from app.schemas import ChatRequest, TripCreate


app = FastAPI(title="Travel & Weather Advisory Assistant")
db.init_db()   # make sure the table exists when the server starts


@app.post("/trips", status_code=201)
def create_trip(trip: TripCreate):
    # FastAPI has already validated `trip` using TripCreate
    return db.create_trip(
        trip.employee_id,
        trip.destination,
        trip.start_date.isoformat(),
        trip.end_date.isoformat(),
        trip.purpose,
    )


@app.get("/trips")
def list_all_trips():
    return db.list_all_trips()


@app.get("/trips/{trip_id}")
def get_trip(trip_id: str):
    trip = db.get_trip(trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail=f"Trip {trip_id} not found")
    return trip


@app.post("/chat")
def chat(req: ChatRequest):
    history = memory.get_history(req.session_id)
    try:
        answer, tools_used = ask(req.question, history, req.employee_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Assistant unavailable: {e}")
    memory.add_turn(req.session_id, req.question, answer)
    return {"session_id": req.session_id, "answer": answer, "tools_used": tools_used}
