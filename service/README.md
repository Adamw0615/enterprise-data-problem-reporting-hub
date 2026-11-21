# Data Quality Issue Intake API — Milestone 1

This is an **unauthenticated, local-only prototype** using fictional data.
It adds a basic operational issue registry to the existing Power BI reporting portfolio.

## Setup

Requires Python 3.11+.

```bash
cd service
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1
```

Visit http://127.0.0.1:8000/docs for interactive API documentation.

## Run tests

```bash
cd service
python -m pytest -q
```

## Sample issue

```json
{
  "title": "Duplicate source records",
  "description": "Synthetic source extract contains repeated account keys.",
  "domain": "Operations",
  "severity": "High",
  "owner": "Demo Analyst",
  "target_date": "2027-01-15"
}
```

Use POST /issues and GET /issues in the interactive docs.

## Current capabilities

- SQLite-backed issue creation and retrieval
- Pydantic request validation
- Status filtering and pagination
- Health endpoint
- Initial automated API tests

## NOT implemented

- Authentication, authorization, audit history, SLA processing, state transitions
- Power BI integration, Power Automate integration, deployment
- Database migrations, production security controls

Do not expose this service publicly. The application uses no real bank data.
The default SQLite file is generated locally and must not be committed.
