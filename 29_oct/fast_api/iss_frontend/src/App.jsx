
import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [page, setPage] = useState("Dashboard");

  // Candidate states
  const [candidates, setCandidates] = useState([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  // Interview states
  const [interviews, setInterviews] = useState([]);
  const [candidateId, setCandidateId] = useState("");
  const [interviewerName, setInterviewerName] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  // General states
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Load candidates
  async function loadCandidates() {
    try {
      const response = await fetch(`${API_URL}/api/v1/candidates`);

      if (!response.ok) {
        throw new Error("Could not load candidates.");
      }

      const data = await response.json();
      setCandidates(data);
    } catch {
      setMessage("Could not connect to the backend.");
    }
  }

  // Load interviews
  async function loadInterviews() {
    try {
      const response = await fetch(`${API_URL}/api/v1/interviews`);

      if (!response.ok) {
        throw new Error("Could not load interviews.");
      }

      const data = await response.json();
      setInterviews(data);
    } catch {
      setMessage("Could not load interviews. Check your backend.");
    }
  }

  // Load data when the app opens
  useEffect(() => {
    loadCandidates();
    loadInterviews();
  }, []);

  // Add candidate
  async function addCandidate(event) {
    event.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/v1/candidates`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Could not add candidate."
        );
      }

      setName("");
      setEmail("");
      setMessage("Candidate added successfully!");

      await loadCandidates();
    } catch (error) {
      setMessage(error.message || "Could not add candidate.");
    } finally {
      setLoading(false);
    }
  }

  // Schedule interview
  async function scheduleInterview(event) {
    event.preventDefault();
    setMessage("");

    const start = new Date(startTime);
    const end = new Date(endTime);

    if (start >= end) {
      setMessage("End time must be later than start time.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/v1/interviews`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          candidate_id: Number(candidateId),
          interviewer_name: interviewerName.trim(),
          start_time: start.toISOString(),
          end_time: end.toISOString(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Could not schedule interview."
        );
      }

      setCandidateId("");
      setInterviewerName("");
      setStartTime("");
      setEndTime("");
      setMessage("Interview scheduled successfully!");

      await loadInterviews();
    } catch (error) {
      setMessage(error.message || "Could not schedule interview.");
    } finally {
      setLoading(false);
    }
  }

  // Dashboard
  function renderDashboard() {
    return (
      <>
        <section className="welcome">
          <h2>Welcome to ISS!</h2>
          <p>
            Manage candidates and schedule interviews from one place.
          </p>
        </section>

        <section className="cards">
          <div className="card">
            <p>Total Candidates</p>
            <h2>{candidates.length}</h2>
            <button onClick={() => setPage("Candidates")}>
              View Candidates
            </button>
          </div>

          <div className="card">
            <p>Total Interviews</p>
            <h2>{interviews.length}</h2>
            <button onClick={() => setPage("Interviews")}>
              View Interviews
            </button>
          </div>

          <div className="card">
            <p>Backend API</p>
            <h2>FastAPI</h2>
            <a
              href={`${API_URL}/docs`}
              target="_blank"
              rel="noreferrer"
            >
              Open API Docs
            </a>
          </div>
        </section>
      </>
    );
  }

  // Candidates page
  function renderCandidates() {
    return (
      <>
        <section className="welcome">
          <h2>Add Candidate</h2>

          <form onSubmit={addCandidate} className="candidate-form">
            <label>
              Full Name
              <input
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Enter candidate name"
                minLength={2}
                maxLength={100}
                required
              />
            </label>

            <label>
              Email Address
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="Enter email address"
                required
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Please wait..." : "Add Candidate"}
            </button>
          </form>

          {message && <p className="message">{message}</p>}
        </section>

        <section className="welcome">
          <div className="section-heading">
            <h2>Candidate List</h2>
            <button onClick={loadCandidates}>Refresh</button>
          </div>

          {candidates.length === 0 ? (
            <p>No candidates found yet.</p>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                  </tr>
                </thead>

                <tbody>
                  {candidates.map((candidate) => (
                    <tr key={candidate.id}>
                      <td>{candidate.id}</td>
                      <td>{candidate.name}</td>
                      <td>{candidate.email}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </>
    );
  }

  // Interviews page
  function renderInterviews() {
    return (
      <>
        <section className="welcome">
          <h2>Schedule an Interview</h2>

          <form
            onSubmit={scheduleInterview}
            className="candidate-form"
          >
            <label>
              Candidate
              <select
                value={candidateId}
                onChange={(event) => setCandidateId(event.target.value)}
                required
              >
                <option value="">Select a candidate</option>

                {candidates.map((candidate) => (
                  <option key={candidate.id} value={candidate.id}>
                    {candidate.name} (ID: {candidate.id})
                  </option>
                ))}
              </select>
            </label>

            <label>
              Interviewer Name
              <input
                type="text"
                value={interviewerName}
                onChange={(event) =>
                  setInterviewerName(event.target.value)
                }
                placeholder="Enter interviewer name"
                minLength={2}
                maxLength={100}
                required
              />
            </label>

            <label>
              Start Time
              <input
                type="datetime-local"
                value={startTime}
                onChange={(event) => setStartTime(event.target.value)}
                required
              />
            </label>

            <label>
              End Time
              <input
                type="datetime-local"
                value={endTime}
                onChange={(event) => setEndTime(event.target.value)}
                required
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Please wait..." : "Schedule Interview"}
            </button>
          </form>

          {message && <p className="message">{message}</p>}
        </section>

        <section className="welcome">
          <div className="section-heading">
            <h2>Interview List</h2>
            <button onClick={loadInterviews}>Refresh</button>
          </div>

          {interviews.length === 0 ? (
            <p>No interviews scheduled yet.</p>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Candidate ID</th>
                    <th>Interviewer</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {interviews.map((interview) => (
                    <tr key={interview.id}>
                      <td>{interview.id}</td>
                      <td>{interview.candidate_id}</td>
                      <td>{interview.interviewer_name}</td>
                      <td>
                        {new Date(interview.start_time).toLocaleString()}
                      </td>
                      <td>
                        {new Date(interview.end_time).toLocaleString()}
                      </td>
                      <td>{interview.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>ISS</h2>
        <p className="subtitle">Interview Scheduling</p>

        <nav>
          {["Dashboard", "Candidates", "Interviews"].map((item) => (
            <button
              key={item}
              className={
                page === item ? "nav-button active" : "nav-button"
              }
              onClick={() => {
                setPage(item);
                setMessage("");
              }}
            >
              {item}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>{page}</h1>
            <p>Interview Scheduling System</p>
          </div>

          <span className="status">ISS Project</span>
        </header>

        {page === "Dashboard" && renderDashboard()}
        {page === "Candidates" && renderCandidates()}
        {page === "Interviews" && renderInterviews()}
      </main>
    </div>
  );
}

export default App;
