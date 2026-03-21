"""
OptInPG Collector Service — FastAPI + LangGraph skeleton
Reads council-out/ data and triggers Wave 1 data agents.
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
        raise HTTPException(status_code=400, detail=f"Invalid slug: '{slug}'")
    return slug
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="OptInPG Collector",
    description="Data collection service for Octant public goods evaluation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

COUNCIL_OUT = Path(os.getenv("COUNCIL_OUT_DIR", "council-out"))


class CollectRequest(BaseModel):
    project: str
    slug: str | None = None


class CollectResponse(BaseModel):
    slug: str
    status: str
    data_files: list[str]
    collected_at: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "collector", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/collect", response_model=CollectResponse)
def collect(req: CollectRequest):
    slug = req.slug or req.project.lower().replace(" ", "-").replace("/", "-")[:40]
    data_dir = COUNCIL_OUT / slug / "data"

    if not data_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No data found for slug '{slug}'. Run /council:evaluate first.",
        )

    data_files = []
    for f in sorted(data_dir.iterdir()):
        if f.suffix in (".json", ".md"):
            data_files.append(f.name)

    return CollectResponse(
        slug=slug,
        status="collected",
        data_files=data_files,
        collected_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/collect/{slug}")
def get_collected_data(slug: str):
    validate_slug(slug)
    data_dir = COUNCIL_OUT / slug / "data"
    if not data_dir.exists():
        raise HTTPException(status_code=404, detail=f"No data for slug '{slug}'")

    result = {}
    for f in sorted(data_dir.iterdir()):
        if f.suffix == ".json":
            try:
                result[f.stem] = json.loads(f.read_text())
            except json.JSONDecodeError:
                result[f.stem] = {"_error": f"Failed to parse {f.name}"}
        elif f.suffix == ".md":
            result[f.stem] = f.read_text()

    return {"slug": slug, "data": result}


@app.get("/projects")
def list_projects():
    if not COUNCIL_OUT.exists():
        return {"projects": []}

    projects = []
    for d in sorted(COUNCIL_OUT.iterdir()):
        if d.is_dir() and (d / "data").exists():
            data_files = [f.name for f in (d / "data").iterdir() if f.suffix in (".json", ".md")]
            projects.append({"slug": d.name, "data_files": data_files})

    return {"projects": projects}
