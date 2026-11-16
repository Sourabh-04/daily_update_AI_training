

from datetime import date

from pydantic import BaseModel, Field, model_validator


class TripCreate(BaseModel):
    employee_id: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=2)
    start_date: date            # Pydantic rejects invalid dates like 2026-13-45
    end_date: date
    purpose: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date < date.today():
            raise ValueError("start_date cannot be in the past")
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    employee_id: str | None = None   # optional: helps the assistant find the trip
