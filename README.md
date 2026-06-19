# Warden

Autonomous service degradation detection and remediation agent for Internal Developer Platforms.

## Requirements

- Docker & Docker Compose
- Python 3.12+
- Groq API Key ([console.groq.com](https://console.groq.com))

## Setup

1. Clone the repository
2. Copy the environment file and fill in your values:
   ```bash
   cp .env.example .env
3. Start the services:
    ```bash
    docker compose up --build
    
4. Running locally (without Docker)
    ```bash
    python3.12 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python -m src.main

5. Running tests
    ```bash
    pytest tests/

6. API

| Method | Route | Description |
|---|---|---|
| GET | /health | Service health check |
| GET | /events | List received events |
| GET | /events/:id | Event detail with decision |
| GET | /approvals | Pending approval requests |
| POST | /approvals/:id/approve | Approve and execute action |
| POST | /approvals/:id/reject | Reject pending action |

