"""
Database layer for persistent evaluation storage.
Uses libsql (Turso) when TURSO_URL is set, falls back to local SQLite.
"""
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Try libsql for Turso, fall back to sqlite3
try:
    import libsql_experimental as libsql
    HAS_LIBSQL = True
except ImportError:
    HAS_LIBSQL = False


SCHEMA = """
CREATE TABLE IF NOT EXISTS evaluations (
    slug TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    ostrom_scores TEXT,
    quant_scores TEXT,
    qual_json TEXT,
    eas_json TEXT,
    report_md TEXT,
    ostrom_report_md TEXT,
    data_json TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def get_connection():
    """Get a database connection — Turso if configured, else local SQLite."""
    turso_url = os.getenv("TURSO_URL")
    turso_token = os.getenv("TURSO_TOKEN")

    if turso_url and HAS_LIBSQL:
        conn = libsql.connect(
            turso_url,
            auth_token=turso_token,
        )
    else:
        db_path = os.getenv("DATABASE_PATH", "evaluations.db")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

    conn.execute(SCHEMA)
    conn.commit()
    return conn


def _safe_json(data) -> str | None:
    """Serialize to JSON string, return None if data is None."""
    if data is None:
        return None
    if isinstance(data, str):
        return data
    return json.dumps(data)


def _parse_json(text: str | None):
    """Parse JSON string, return None if empty."""
    if not text:
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def publish_evaluation(payload: dict) -> dict:
    """Store a complete evaluation in the database."""
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    slug = payload["slug"]
    project = payload.get("project", slug)

    conn.execute(
        """
        INSERT INTO evaluations (slug, project, ostrom_scores, quant_scores, qual_json,
                                 eas_json, report_md, ostrom_report_md, data_json, metadata,
                                 created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            project=excluded.project,
            ostrom_scores=excluded.ostrom_scores,
            quant_scores=excluded.quant_scores,
            qual_json=excluded.qual_json,
            eas_json=excluded.eas_json,
            report_md=excluded.report_md,
            ostrom_report_md=excluded.ostrom_report_md,
            data_json=excluded.data_json,
            metadata=excluded.metadata,
            updated_at=excluded.updated_at
        """,
        (
            slug,
            project,
            _safe_json(payload.get("ostrom_scores")),
            _safe_json(payload.get("quant_scores")),
            _safe_json(payload.get("qual_json")),
            _safe_json(payload.get("eas_json")),
            payload.get("report_md"),
            payload.get("ostrom_report_md"),
            _safe_json(payload.get("data")),
            _safe_json(payload.get("metadata")),
            now,
            now,
        ),
    )
    conn.commit()
    conn.close()

    return {"slug": slug, "project": project, "published_at": now}


def list_evaluations() -> list[dict]:
    """List all evaluations from the database."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT slug, project, ostrom_scores, quant_scores, created_at, updated_at "
        "FROM evaluations ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()

    results = []
    for row in rows:
        ostrom = _parse_json(row["ostrom_scores"] if isinstance(row, sqlite3.Row) else row[2])
        quant = _parse_json(row["quant_scores"] if isinstance(row, sqlite3.Row) else row[3])

        overall_score = None
        governance_maturity = None
        if ostrom:
            overall_score = ostrom.get("overall_score")
            governance_maturity = ostrom.get("governance_maturity")

        composite = None
        if quant:
            composite = quant.get("composite", {}).get("score") if isinstance(quant.get("composite"), dict) else quant.get("composite_score")

        results.append({
            "slug": row["slug"] if isinstance(row, sqlite3.Row) else row[0],
            "project": row["project"] if isinstance(row, sqlite3.Row) else row[1],
            "ostrom_overall": overall_score,
            "governance_maturity": governance_maturity,
            "quant_composite": composite,
            "created_at": row["created_at"] if isinstance(row, sqlite3.Row) else row[4],
            "updated_at": row["updated_at"] if isinstance(row, sqlite3.Row) else row[5],
        })
    return results


def get_evaluation(slug: str) -> dict | None:
    """Get a single evaluation by slug."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM evaluations WHERE slug = ?", (slug,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    if isinstance(row, sqlite3.Row):
        d = dict(row)
    else:
        cols = ["slug", "project", "ostrom_scores", "quant_scores", "qual_json",
                "eas_json", "report_md", "ostrom_report_md", "data_json", "metadata",
                "created_at", "updated_at"]
        d = dict(zip(cols, row))

    # Parse JSON fields
    for field in ["ostrom_scores", "quant_scores", "qual_json", "eas_json", "data_json", "metadata"]:
        d[field] = _parse_json(d.get(field))

    return d
