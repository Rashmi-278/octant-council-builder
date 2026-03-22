"""
OptInPG Evaluator Service — FastAPI backend for Octant public goods evaluation.
Serves evaluation data from Turso/SQLite (primary) with filesystem fallback.
Accepts POST /api/publish for auto-publishing evaluations from the CLI.
"""
import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import publish_evaluation, list_evaluations, get_evaluation


SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


def validate_slug(slug: str) -> str:
    if not SLUG_PATTERN.match(slug):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid slug: '{slug}'. Use only lowercase letters, numbers, and hyphens.",
        )
    return slug


app = FastAPI(
    title="OptInPG Evaluator",
    description="Evaluation dashboard API for Octant public goods with Ostrom governance scoring",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

COUNCIL_OUT = Path(os.getenv("COUNCIL_OUT_DIR", "council-out"))


# ── Pydantic models ──────────────────────────────────────────


class PublishRequest(BaseModel):
    slug: str
    project: str
    ostrom_scores: dict | None = None
    quant_scores: dict | None = None
    qual_json: dict | None = None
    eas_json: dict | None = None
    report_md: str | None = None
    ostrom_report_md: str | None = None
    data: dict | None = None
    metadata: dict | None = None


class PublishResponse(BaseModel):
    slug: str
    project: str
    published_at: str
    url: str


class EvaluateRequest(BaseModel):
    slug: str


class EvaluateResponse(BaseModel):
    slug: str
    status: str
    report_path: str | None
    eas_attestation_path: str | None
    evaluated_at: str


# ── Filesystem helpers ────────────────────────────────────────


def safe_read_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {"_error": f"Failed to parse {path.name}"}


def collect_filesystem_data(slug: str) -> dict | None:
    """Read all evaluation data from council-out/{slug}/ filesystem."""
    slug_dir = COUNCIL_OUT / slug
    if not slug_dir.exists():
        return None

    dashboard: dict[str, Any] = {
        "slug": slug,
        "data": {},
        "evaluations": {},
        "synthesis": {},
        "has_report": False,
        "has_eas": False,
    }

    data_dir = slug_dir / "data"
    if data_dir.exists():
        for f in sorted(data_dir.iterdir()):
            if f.suffix == ".json":
                dashboard["data"][f.stem] = safe_read_json(f)

    eval_dir = slug_dir / "eval"
    if eval_dir.exists():
        for f in sorted(eval_dir.iterdir()):
            if f.suffix == ".json":
                dashboard["evaluations"][f.stem] = safe_read_json(f)

    synth_dir = slug_dir / "synth"
    if synth_dir.exists():
        for f in sorted(synth_dir.iterdir()):
            if f.suffix == ".json":
                dashboard["synthesis"][f.stem] = safe_read_json(f)
            elif f.suffix == ".md":
                dashboard["synthesis"][f.stem] = f.read_text()

    report_path = synth_dir / "ostrom-report.md" if synth_dir.exists() else None
    eas_path = synth_dir / "eas-attestations.json" if synth_dir.exists() else None
    dashboard["has_report"] = report_path is not None and report_path.exists()
    dashboard["has_eas"] = eas_path is not None and eas_path.exists()

    return dashboard


def format_db_to_dashboard(row: dict) -> dict:
    """Convert a DB row into dashboard format matching the frontend expectations."""
    return {
        "slug": row["slug"],
        "project": row.get("project", row["slug"]),
        "data": row.get("data_json") or {},
        "evaluations": {
            k: v
            for k, v in [
                ("ostrom-scores", row.get("ostrom_scores")),
                ("quant", row.get("quant_scores")),
                ("qual", row.get("qual_json")),
            ]
            if v is not None
        },
        "synthesis": {
            k: v
            for k, v in [
                ("eas-attestations", row.get("eas_json")),
                ("ostrom-report", row.get("ostrom_report_md")),
            ]
            if v is not None
        },
        "has_report": row.get("report_md") is not None or row.get("ostrom_report_md") is not None,
        "has_eas": row.get("eas_json") is not None,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "source": "database",
    }


# ── Endpoints ─────────────────────────────────────────────────


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "evaluator",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/publish", response_model=PublishResponse, status_code=201)
def publish(req: PublishRequest):
    """Publish an evaluation to the persistent database.

    Called automatically after /council:evaluate when PUBLISH_OSTROM=true.
    """
    validate_slug(req.slug)

    result = publish_evaluation(req.model_dump())

    base_url = os.getenv("PUBLIC_URL", "")
    return PublishResponse(
        slug=result["slug"],
        project=result["project"],
        published_at=result["published_at"],
        url=f"{base_url}/project?slug={result['slug']}",
    )


@app.get("/projects")
def list_projects():
    """List all evaluated projects. Merges DB and filesystem sources."""
    seen_slugs = set()
    projects = []

    # 1. Database projects (primary)
    try:
        db_projects = list_evaluations()
        for p in db_projects:
            seen_slugs.add(p["slug"])
            projects.append({
                "slug": p["slug"],
                "project": p["project"],
                "ostrom_overall": p.get("ostrom_overall"),
                "governance_maturity": p.get("governance_maturity"),
                "quant_composite": p.get("quant_composite"),
                "created_at": p.get("created_at"),
                "updated_at": p.get("updated_at"),
                "source": "database",
            })
    except Exception:
        pass  # DB unavailable, fall through to filesystem

    # 2. Filesystem projects (fallback for local dev / unpublished)
    if COUNCIL_OUT.exists():
        for d in sorted(COUNCIL_OUT.iterdir()):
            if d.is_dir() and d.name not in seen_slugs:
                data_files = []
                for sub in ["data", "eval", "synth"]:
                    sub_dir = d / sub
                    if sub_dir.exists():
                        data_files.extend(
                            f.name for f in sub_dir.iterdir() if f.suffix in (".json", ".md")
                        )
                if data_files:
                    projects.append({
                        "slug": d.name,
                        "data_files": sorted(data_files),
                        "source": "filesystem",
                    })

    return {"projects": projects}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest):
    """Check evaluation status for a slug (DB or filesystem)."""
    validate_slug(req.slug)

    # Check DB first
    row = get_evaluation(req.slug)
    if row:
        return EvaluateResponse(
            slug=req.slug,
            status="evaluated",
            report_path=None,
            eas_attestation_path=None,
            evaluated_at=row.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )

    # Filesystem fallback
    synth_dir = COUNCIL_OUT / req.slug / "synth"
    if not synth_dir.exists():
        raise HTTPException(status_code=404, detail=f"No data for slug '{req.slug}'")

    report_path = synth_dir / "ostrom-report.md"
    eas_path = synth_dir / "eas-attestations.json"

    return EvaluateResponse(
        slug=req.slug,
        status="evaluated",
        report_path=str(report_path) if report_path.exists() else None,
        eas_attestation_path=str(eas_path) if eas_path.exists() else None,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/evaluate/{slug}/report")
def get_report(slug: str):
    """Get the evaluation report (DB-first, filesystem-fallback)."""
    validate_slug(slug)

    # DB first
    row = get_evaluation(slug)
    if row:
        report = row.get("ostrom_report_md") or row.get("report_md")
        if report:
            return {"slug": slug, "report": report, "format": "markdown", "source": "database"}

    # Filesystem fallback
    report_path = COUNCIL_OUT / slug / "synth" / "ostrom-report.md"
    if not report_path.exists():
        report_path = COUNCIL_OUT / slug / "REPORT.md"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail=f"No report for slug '{slug}'")

    return {"slug": slug, "report": report_path.read_text(), "format": "markdown", "source": "filesystem"}


@app.get("/evaluate/{slug}/eas")
def get_eas_attestation(slug: str):
    """Get EAS attestation data (DB-first, filesystem-fallback)."""
    validate_slug(slug)

    # DB first
    row = get_evaluation(slug)
    if row and row.get("eas_json"):
        return row["eas_json"]

    # Filesystem fallback
    eas_path = COUNCIL_OUT / slug / "synth" / "eas-attestations.json"
    if not eas_path.exists():
        raise HTTPException(status_code=404, detail=f"No EAS attestation for slug '{slug}'")

    try:
        return json.loads(eas_path.read_text())
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail=f"Malformed EAS attestation JSON for slug '{slug}'")


@app.get("/evaluate/{slug}/ostrom-radar")
def get_ostrom_radar_data(slug: str):
    """Return Ostrom scores formatted for radar chart rendering.

    DB-first, filesystem-fallback. Fixed to match actual eval-ostrom agent output schema.
    """
    validate_slug(slug)

    ostrom_data = None

    # DB first
    row = get_evaluation(slug)
    if row and row.get("ostrom_scores"):
        ostrom_data = row["ostrom_scores"]

    # Filesystem fallback
    if not ostrom_data:
        ostrom_path = COUNCIL_OUT / slug / "eval" / "ostrom-scores.json"
        if not ostrom_path.exists():
            raise HTTPException(status_code=404, detail=f"No Ostrom scores for slug '{slug}'")

        try:
            ostrom_data = json.loads(ostrom_path.read_text())
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail=f"Malformed Ostrom scores JSON for slug '{slug}'")

    # Handle both schema shapes: agent uses "principles[]", legacy uses "rules[]"
    principles = ostrom_data.get("principles", ostrom_data.get("rules", []))

    radar_data = {
        "project": ostrom_data.get("project", slug),
        "overall_score": ostrom_data.get("overall_score", ostrom_data.get("overall_ostrom_score", 0)),
        "governance_maturity": ostrom_data.get("governance_maturity", "unknown"),
        "axes": [
            {
                "label": p.get("name", p.get("rule_name", f"Principle {p.get('id', p.get('rule_number', i + 1))}")),
                "full_text": p.get("rule_text", ""),
                "value": p.get("score", 0),
                "weight": p.get("weight", 1.0),
                "confidence": p.get("confidence", "unknown"),
            }
            for i, p in enumerate(principles)
        ],
    }

    return radar_data


@app.get("/dashboard/{slug}")
def get_dashboard_data(slug: str):
    """Aggregate all data for the dashboard view. DB-first, filesystem-fallback."""
    validate_slug(slug)

    # DB first
    row = get_evaluation(slug)
    if row:
        return format_db_to_dashboard(row)

    # Filesystem fallback
    fs_data = collect_filesystem_data(slug)
    if fs_data:
        fs_data["source"] = "filesystem"
        return fs_data

    raise HTTPException(status_code=404, detail=f"No data for slug '{slug}'")
