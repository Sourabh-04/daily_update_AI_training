
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class InterviewUpdate(BaseModel):
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time.tzinfo is None or self.end_time.tzinfo is None:
            raise ValueError("Both times must include a timezone.")

        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time.")

        return self


class InterviewCancel(BaseModel):
    reason: str = Field(min_length=3, max_length=500)
