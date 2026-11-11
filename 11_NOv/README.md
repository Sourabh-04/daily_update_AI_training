# Employee Support Agent API

A small FastAPI service that puts an existing **Azure AI Foundry** agent (`EmployeeSupportAgent`) behind a REST API. Redis keeps each user's session, so the agent remembers the conversation across requests.

## How it works

```
Client ──POST /chat──▶ FastAPI (main.py) ──▶ Azure AI Foundry agent
                          │
                          └──▶ Redis
                               • retail:{session_id}:conversation  → Foundry conversation ID
                               • retail:{session_id}:history       → list of user/assistant messages
```

1. The client sends a message, plus a `session_id` if it's continuing a conversation.
2. If the session is new, the API creates a Foundry conversation and saves its ID in Redis.
3. The message goes to the Foundry agent inside that conversation, so the agent has the earlier context.
4. The question and the answer are added to the session history in Redis.
5. Session keys expire after **1 hour** without activity (`SESSION_TTL = 3600`).

## Prerequisites

- Python 3.10 or later
- Docker Desktop, running, for Redis (or any other Redis 6+ server)
- An Azure AI Foundry project that already has an agent deployed
- The Azure CLI, signed in with `az login`, using an account that can access the Foundry project

## Setup

### 1. Create a virtual environment and install dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Start Redis

Docker Desktop must be running first, or you will get a `dockerDesktopLinuxEngine` pipe error.

```powershell
docker run -d --name retail-redis -p 127.0.0.1:6379:6379 -v retail_redis_data:/data redis:7-alpine redis-server --appendonly yes
```

If the container already exists, start it again with `docker start retail-redis`.

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
FOUNDRY_PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>
FOUNDRY_AGENT_NAME=EmployeeSupportAgent
REDIS_URL=redis://localhost:6379/0
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | Yes | – | Endpoint of your Azure AI Foundry project |
| `FOUNDRY_AGENT_NAME` | No | `EmployeeSupportAgent` | Name of the deployed Foundry agent |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection string |

> Don't commit `.env`. Add it to `.gitignore`.

### 4. Sign in to Azure

`DefaultAzureCredential` picks up your Azure CLI login:

```powershell
az login
```

### 5. Run the API

```powershell
uvicorn main:app --reload
```

The API runs at http://127.0.0.1:8000. Interactive docs are at http://127.0.0.1:8000/docs.

## API reference

### `POST /chat`

Sends a message to the employee support agent.

**Request body**

| Field | Type | Required | Notes |
|---|---|---|---|
| `message` | string | Yes | 1–2000 characters |
| `session_id` | UUID | No | Leave it out to start a new session |

**Example: start a new session**

```powershell
curl.exe -X POST http://127.0.0.1:8000/chat `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"How many leave days do I get per year?\"}'
```

```json
{
  "session_id": "3f2b8c1e-6a4d-4e7f-9b21-0c5d8e7a1f42",
  "reply": "Full-time employees receive ..."
}
```

**Example: continue the session**

Send the `session_id` you got back:

```json
{
  "message": "Can I carry unused days forward?",
  "session_id": "3f2b8c1e-6a4d-4e7f-9b21-0c5d8e7a1f42"
}
```

### `GET /history/{session_id}`

Returns the stored chat history for a session.

```powershell
curl.exe http://127.0.0.1:8000/history/3f2b8c1e-6a4d-4e7f-9b21-0c5d8e7a1f42
```

```json
{
  "session_id": "3f2b8c1e-6a4d-4e7f-9b21-0c5d8e7a1f42",
  "messages": [
    { "role": "user", "message": "How many leave days do I get per year?" },
    { "role": "assistant", "message": "Full-time employees receive ..." }
  ]
}
```

An expired or unknown session returns an empty `messages` list.

## Project structure

```
.
├── main.py            # FastAPI app: Redis + Foundry agent integration
├── requirements.txt   # Python dependencies
├── .env               # Local configuration (not committed)
└── README.md
```

## Troubleshooting

| Problem | Cause / fix |
|---|---|
| `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | Docker Desktop isn't running. Start it and wait for "Engine running". |
| `redis.exceptions.ConnectionError` | Redis isn't reachable. Check `docker ps` and `REDIS_URL`. |
| `KeyError: 'FOUNDRY_PROJECT_ENDPOINT'` | `.env` is missing or doesn't set this variable. |
| `DefaultAzureCredential failed to retrieve a token` | Run `az login`, and check that your account has access to the Foundry project. |
| Agent not found | Check that `FOUNDRY_AGENT_NAME` matches the agent name in the Foundry portal. |
