# Backend (FastAPI)

This directory contains the web API backend for the Intelligent Music Agent.

## Run

From the repository root:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Endpoints

- `GET /health` - service health check
- `GET /api/status` - backend + playback status
- `POST /api/command` - run a natural language music command

Request example:

```json
{
  "command": "what's playing"
}
```

