"""
OptInPG Evaluator Service — FastAPI + LangGraph skeleton
Reads analysis data and triggers Wave 3 synthesis agents.
Serves final reports and EAS attestation data.
"""
import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException


SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


def validate_slug(slug: str) -> str:
    if not SLUG_PATTERN.match(slug):
        raise HTTPException(status_code=400, detail=f"Invalid slug: '{slug}'. Use only lowercase letters, numbers, and hyphens.")
    return slug
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="OptInPG Evaluator",
    description="Synthesis and reporting service for Octant public goods evaluation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

COUNCIL_OUT = Path(os.getenv("COUNCIL_OUT_DIR", "council-out"))


class EvaluateRequest(BaseModel):
    slug: str


class EvaluateResponse(BaseModel):
    slug: str
    status: str
    report_path: str | None
    eas_attestation_path: str | None
    evaluated_at: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "evaluator", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/projects")
def list_projects():
    """List all evaluated projects with their available data."""
    if not COUNCIL_OUT.exists():
        return {"projects": []}

    projects = []
    for d in sorted(COUNCIL_OUT.iterdir()):
        if d.is_dir():
            data_files = []
            for sub in ["data", "eval", "synth"]:
                sub_dir = d / sub
                if sub_dir.exists():
                    data_files.extend(
                        f.name for f in sub_dir.iterdir() if f.suffix in (".json", ".md")
                    )
            if data_files:
                projects.append({"slug": d.name, "data_files": sorted(data_files)})

    return {"projects": projects}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest):
    synth_dir = COUNCIL_OUT / req.slug / "synth"
    report_path = synth_dir / "ostrom-report.md"
    eas_path = synth_dir / "eas-attestations.json"

    if not synth_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No synthesis data for slug '{req.slug}'. Run Wave 3 first.",
        )

    return EvaluateResponse(
        slug=req.slug,
        status="evaluated",
        report_path=str(report_path) if report_path.exists() else None,
        eas_attestation_path=str(eas_path) if eas_path.exists() else None,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/evaluate/{slug}/report")
def get_report(slug: str):
    validate_slug(slug)
    report_path = COUNCIL_OUT / slug / "synth" / "ostrom-report.md"
    if not report_path.exists():
        # Fall back to REPORT.md at slug root
        report_path = COUNCIL_OUT / slug / "REPORT.md"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail=f"No report for slug '{slug}'")

    return {"slug": slug, "report": report_path.read_text(), "format": "markdown"}


@app.get("/evaluate/{slug}/eas")
def get_eas_attestation(slug: str):
    validate_slug(slug)
    eas_path = COUNCIL_OUT / slug / "synth" / "eas-attestations.json"
    if not eas_path.exists():
        raise HTTPException(status_code=404, detail=f"No EAS attestation for slug '{slug}'")

    try:
        return json.loads(eas_path.read_text())
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail=f"Malformed EAS attestation JSON for slug '{slug}'")


@app.get("/evaluate/{slug}/ostrom-radar")
def get_ostrom_radar_data(slug: str):
    """Return Ostrom scores formatted for radar chart rendering."""
    validate_slug(slug)
    ostrom_path = COUNCIL_OUT / slug / "eval" / "ostrom-scores.json"
    if not ostrom_path.exists():
        raise HTTPException(status_code=404, detail=f"No Ostrom scores for slug '{slug}'")

    try:
        data = json.loads(ostrom_path.read_text())
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail=f"Malformed Ostrom scores JSON for slug '{slug}'")
    rules = data.get("rules", [])

    radar_data = {
        "project": data.get("project", slug),
        "overall_score": data.get("overall_ostrom_score", 0),
        "governance_maturity": data.get("governance_maturity", "unknown"),
        "axes": [
            {
                "label": rule.get("rule_name", f"Principle {rule.get('rule_number', i+1)}"),
                "full_text": rule.get("rule_text", ""),
                "value": rule.get("score", 0),
                "confidence": rule.get("confidence", "unknown"),
            }
            for i, rule in enumerate(rules)
        ],
    }

    return radar_data


@app.get("/dashboard/{slug}")
def get_dashboard_data(slug: str):
    """Aggregate all data for the dashboard view of a single project."""
    validate_slug(slug)
    slug_dir = COUNCIL_OUT / slug

    if not slug_dir.exists():
        raise HTTPException(status_code=404, detail=f"No data for slug '{slug}'")

    dashboard = {
        "slug": slug,
        "data": {},
        "evaluations": {},
        "synthesis": {},
        "has_report": False,
        "has_eas": False,
    }

    def safe_read_json(path: Path) -> dict | list | None:
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return {"_error": f"Failed to parse {path.name}"}

    # Collect data files
    data_dir = slug_dir / "data"
    if data_dir.exists():
        for f in sorted(data_dir.iterdir()):
            if f.suffix == ".json":
                dashboard["data"][f.stem] = safe_read_json(f)

    # Collect evaluation files
    eval_dir = slug_dir / "eval"
    if eval_dir.exists():
        for f in sorted(eval_dir.iterdir()):
            if f.suffix == ".json":
                dashboard["evaluations"][f.stem] = safe_read_json(f)

    # Collect synthesis files
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
