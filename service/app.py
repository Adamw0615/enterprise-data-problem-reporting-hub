"""Synthetic data-quality issue intake API. Local development only (no authentication)."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

DB_PATH = Path(os.environ.get("DQ_DB_PATH", "issues.db"))
app = FastAPI(title="Enterprise Data Quality API", version="0.1.0")


@contextmanager
def database():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with database() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                domain TEXT NOT NULL,
                severity TEXT NOT NULL,
                owner TEXT NOT NULL,
                target_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TEXT NOT NULL
            )
        """)


class IssueCreate(BaseModel):
    title: str = Field(min_length=5, max_length=160)
    description: str = Field(min_length=10, max_length=3000)
    domain: str = Field(min_length=2, max_length=80)
    severity: Literal["Low", "Medium", "High", "Critical"]
    owner: str = Field(min_length=2, max_length=120)
    target_date: date


class Issue(BaseModel):
    id: int
    title: str
    description: str
    domain: str
    severity: str
    owner: str
    target_date: date
    status: str
    created_at: datetime


@app.on_event("startup")
def start_database():
    initialize_database()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/issues", response_model=Issue, status_code=201)
def create_issue(payload: IssueCreate):
    with database() as connection:
        cursor = connection.execute(
            """INSERT INTO issues
                (title, description, domain, severity, owner, target_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'Open', ?)""",
            (
                payload.title, payload.description, payload.domain,
                payload.severity, payload.owner, payload.target_date.isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        record = connection.execute(
            "SELECT * FROM issues WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return dict(record)


@app.get("/issues", response_model=list[Issue])
def list_issues(
    status: Literal["Open", "Investigating", "Remediating", "Closed"] | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    sql = "SELECT * FROM issues"
    parameters: list[str | int] = []
    if status:
        sql += " WHERE status = ?"
        parameters.append(status)
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    parameters.extend([limit, offset])
    with database() as connection:
        records = connection.execute(sql, parameters).fetchall()
    return [dict(row) for row in records]


@app.get("/issues/{issue_id}", response_model=Issue)
def get_issue(issue_id: int):
    with database() as connection:
        record = connection.execute(
            "SELECT * FROM issues WHERE id = ?", (issue_id,)
        ).fetchone()
    if record is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return dict(record)
