import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

import app as module


def test_issue_create_list_and_lookup():
    with tempfile.TemporaryDirectory() as directory:
        module.DB_PATH = Path(directory) / "test.db"
        module.initialize_database()
        with TestClient(module.app) as client:
            payload = {
                "title": "Missing transaction date",
                "description": "Synthetic reporting feed has blank dates.",
                "domain": "Finance",
                "severity": "High",
                "owner": "Demo Analyst",
                "target_date": "2027-01-15",
            }
            response = client.post("/issues", json=payload)
            assert response.status_code == 201
            issue_id = response.json()["id"]
            assert response.json()["status"] == "Open"
            assert client.get("/issues").json()[0]["id"] == issue_id
            assert client.get(f"/issues/{issue_id}").status_code == 200
            assert client.get("/issues/9999").status_code == 404


def test_invalid_issue_rejected():
    with tempfile.TemporaryDirectory() as directory:
        module.DB_PATH = Path(directory) / "test.db"
        module.initialize_database()
        with TestClient(module.app) as client:
            response = client.post("/issues", json={"title": "x"})
            assert response.status_code == 422
            assert client.get("/issues?limit=1000").status_code == 422
