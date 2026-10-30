
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class InterviewCreate(BaseModel):
    candidate_id: int = Field(gt=0)
    interviewer_name: str = Field(min_length=2, max_length=100)
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time.")

        if self.start_time.utcoffset() != self.end_time.utcoffset():
            raise ValueError(
                "Start and end times must use the same timezone offset."
            )

        if self.start_time.tzinfo is None:
            raise ValueError("Start time must include a timezone.")

        if self.end_time.tzinfo is None:
            raise ValueError("End time must include a timezone.")

        return self


class InterviewResponse(BaseModel):
    id: int
    candidate_id: int
    interviewer_name: str
    start_time: datetime
    end_time: datetime
    status: str
