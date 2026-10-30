
from fastapi import FastAPI, HTTPException, status
from psycopg import Error, IntegrityError

from data_base import get_connection
from schema import CandidateCreate, CandidateResponse
from fastapi.middleware.cors import CORSMiddleware


from interview_schema import *
from interview_update_schema import *

app = FastAPI(
    title="Interview Scheduling System API",
    description="Backend API for managing candidates and interviews",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Interview Scheduling System API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}



@app.get("/db-test")
def test_database():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        current_database() AS database_name,
                        current_schema() AS schema_name,
                        current_user AS username,
                        current_setting('search_path') AS search_path
                """)
                connection_info = cur.fetchone()

                cur.execute("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_name = 'candidates'
                """)
                tables = cur.fetchall()

        return {
            "status": "connected",
            "connection": connection_info,
            "matching_tables": tables
        }

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {e}"
        )



@app.post(
    "/api/v1/candidates",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_candidate(candidate: CandidateCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO candidates (name, email)
                    VALUES (%s, %s)
                    RETURNING id, name, email
                    """,
                    (candidate.name.strip(), str(candidate.email)),
                )
                new_candidate = cur.fetchone()

        return new_candidate

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A candidate with this email already exists.",
        )
    except Error:
        raise HTTPException(
            status_code=500,
            detail="Could not save the candidate.",
        )


@app.get("/api/v1/candidates", response_model=list[CandidateResponse])
def list_candidates():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, email
                    FROM candidates
                    ORDER BY id
                    """
                )
                candidates = cur.fetchall()

        return candidates

    except Error:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve candidates.",
        )

@app.post(
    "/api/v1/interviews",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview(interview: InterviewCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                # Serialize scheduling requests to prevent
                # simultaneous requests from double booking.
                cur.execute("SELECT pg_advisory_xact_lock(123456)")

                # Check candidate exists.
                cur.execute(
                    "SELECT id FROM candidates WHERE id = %s",
                    (interview.candidate_id,),
                )

                if cur.fetchone() is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Candidate not found.",
                    )

                # Check for overlapping interviews.
                cur.execute(
                    """
                    SELECT id
                    FROM interviews
                    WHERE status = 'Scheduled'
                      AND (
                          candidate_id = %s
                          OR LOWER(interviewer_name) = LOWER(%s)
                      )
                      AND start_time < %s
                      AND end_time > %s
                    LIMIT 1
                    """,
                    (
                        interview.candidate_id,
                        interview.interviewer_name.strip(),
                        interview.end_time,
                        interview.start_time,
                    ),
                )

                if cur.fetchone():
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "Scheduling conflict: the candidate or "
                            "interviewer already has an interview "
                            "during this time."
                        ),
                    )

                cur.execute(
                    """
                    INSERT INTO interviews (
                        candidate_id,
                        interviewer_name,
                        start_time,
                        end_time,
                        status
                    )
                    VALUES (%s, %s, %s, %s, 'Scheduled')
                    RETURNING id, candidate_id, interviewer_name,
                              start_time, end_time, status
                    """,
                    (
                        interview.candidate_id,
                        interview.interviewer_name.strip(),
                        interview.start_time,
                        interview.end_time,
                    ),
                )

                new_interview = cur.fetchone()

                cur.execute(
                    """
                    INSERT INTO audit_events (
                        interview_id, action, details
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        new_interview["id"],
                        "Created",
                        "Interview scheduled",
                    ),
                )

        return new_interview

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not schedule the interview.",
        )


@app.get(
    "/api/v1/interviews",
    response_model=list[InterviewResponse],
)
def list_interviews():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, candidate_id, interviewer_name,
                           start_time, end_time, status
                    FROM interviews
                    ORDER BY start_time
                    """
                )
                return cur.fetchall()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve interviews.",
        )


@app.patch("/api/v1/interviews/{interview_id}")
def reschedule_interview(
    interview_id: int,
    update: InterviewUpdate
):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute("SELECT pg_advisory_xact_lock(123456)")

                cur.execute(
                    """
                    SELECT candidate_id, interviewer_name, status
                    FROM interviews
                    WHERE id = %s
                    """,
                    (interview_id,)
                )
                interview = cur.fetchone()

                if interview is None:
                    raise HTTPException(404, "Interview not found.")

                if interview["status"] != "Scheduled":
                    raise HTTPException(
                        400, "Only scheduled interviews can be rescheduled."
                    )

                cur.execute(
                    """
                    SELECT id
                    FROM interviews
                    WHERE id <> %s
                      AND status = 'Scheduled'
                      AND (
                          candidate_id = %s
                          OR LOWER(interviewer_name) = LOWER(%s)
                      )
                      AND start_time < %s
                      AND end_time > %s
                    LIMIT 1
                    """,
                    (
                        interview_id,
                        interview["candidate_id"],
                        interview["interviewer_name"],
                        update.end_time,
                        update.start_time,
                    )
                )

                if cur.fetchone():
                    raise HTTPException(
                        409, "Candidate or interviewer is already booked."
                    )

                cur.execute(
                    """
                    UPDATE interviews
                    SET start_time = %s,
                        end_time = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, candidate_id, interviewer_name,
                              start_time, end_time, status
                    """,
                    (update.start_time, update.end_time, interview_id)
                )

                result = cur.fetchone()

                cur.execute(
                    """
                    INSERT INTO audit_events (interview_id, action, details)
                    VALUES (%s, %s, %s)
                    """,
                    (interview_id, "Rescheduled", "Interview time updated")
                )

        return result

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, "Could not reschedule interview.")


@app.post("/api/v1/interviews/{interview_id}/cancel")
def cancel_interview(
    interview_id: int,
    cancellation: InterviewCancel
):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute("SELECT pg_advisory_xact_lock(123456)")

                cur.execute(
                    """
                    SELECT status
                    FROM interviews
                    WHERE id = %s
                    """,
                    (interview_id,)
                )
                interview = cur.fetchone()

                if interview is None:
                    raise HTTPException(404, "Interview not found.")

                if interview["status"] != "Scheduled":
                    raise HTTPException(
                        400, "Only scheduled interviews can be cancelled."
                    )

                cur.execute(
                    """
                    UPDATE interviews
                    SET status = 'Cancelled',
                        cancellation_reason = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (cancellation.reason.strip(), interview_id)
                )

                cur.execute(
                    """
                    INSERT INTO audit_events (interview_id, action, details)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        interview_id,
                        "Cancelled",
                        cancellation.reason.strip()
                    )
                )

        return {
            "message": "Interview cancelled successfully.",
            "interview_id": interview_id
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, "Could not cancel interview.")
