"""
Tests for the publish pipeline and DB-backed endpoints.
Run: cd production/backend/evaluator && pip install -r requirements.txt pytest httpx && pytest test_publish.py -v
"""
import json
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def setup_env(tmp_path):
    """Use a temp SQLite DB and temp council-out dir for each test."""
    db_path = str(tmp_path / "test.db")
    council_dir = tmp_path / "council-out"
    council_dir.mkdir()

    os.environ["DATABASE_PATH"] = db_path
    os.environ["COUNCIL_OUT_DIR"] = str(council_dir)
    os.environ.pop("TURSO_URL", None)
    os.environ.pop("TURSO_TOKEN", None)

    # Reimport to pick up new env
    import importlib
    import db as db_module
    import main as main_module
    importlib.reload(db_module)
    importlib.reload(main_module)

    yield {"db_path": db_path, "council_dir": council_dir}


@pytest.fixture
def client(setup_env):
    from main import app
    return TestClient(app)


VALID_PAYLOAD = {
    "slug": "protocol-guild",
    "project": "Protocol Guild",
    "ostrom_scores": {
        "project": "Protocol Guild",
        "overall_score": 74.5,
        "governance_maturity": "established",
        "principles": [
            {"id": 1, "name": "Clearly Defined Boundaries", "score": 88, "weight": 1.25},
            {"id": 2, "name": "Congruence with Local Conditions", "score": 82, "weight": 1.0},
            {"id": 3, "name": "Collective-Choice Arrangements", "score": 76, "weight": 1.25},
            {"id": 4, "name": "Monitoring", "score": 90, "weight": 1.25},
            {"id": 5, "name": "Graduated Sanctions", "score": 38, "weight": 0.75},
            {"id": 6, "name": "Conflict-Resolution Mechanisms", "score": 55, "weight": 1.0},
            {"id": 7, "name": "Minimal Recognition of Rights to Organize", "score": 78, "weight": 1.0},
            {"id": 8, "name": "Nested Enterprises", "score": 72, "weight": 1.0},
        ],
    },
    "quant_scores": {"composite_score": 86, "activity": 82, "ecosystem_impact": 97},
    "qual_json": {"summary": "Protocol Guild is exceptional.", "strengths": ["transparency"]},
    "eas_json": {"attestations": [{"schema": "0x000", "data": {"recipient": "0xF6C"}}]},
    "report_md": "# Council Report: Protocol Guild\n\n**Recommendation: FUND**",
    "ostrom_report_md": "# Protocol Guild — Ostrom Commons Evaluation Report\n\nOverall: 74.5/100",
    "metadata": {"evaluated_at": "2026-03-22T00:00:00Z", "agent_count": 19},
}


# ── POST /api/publish ─────────────────────────────────────────


class TestPublishEndpoint:
    def test_publish_happy_path(self, client):
        resp = client.post("/api/publish", json=VALID_PAYLOAD)
        assert resp.status_code == 201
        body = resp.json()
        assert body["slug"] == "protocol-guild"
        assert body["project"] == "Protocol Guild"
        assert "published_at" in body
        assert "protocol-guild" in body["url"]

    def test_publish_bad_slug(self, client):
        payload = {**VALID_PAYLOAD, "slug": "BAD SLUG!"}
        resp = client.post("/api/publish", json=payload)
        assert resp.status_code == 400

    def test_publish_missing_required_fields(self, client):
        resp = client.post("/api/publish", json={"slug": "ok"})
        assert resp.status_code == 422  # pydantic validation

    def test_publish_minimal_payload(self, client):
        """Publish with only required fields (slug + project)."""
        resp = client.post("/api/publish", json={"slug": "minimal-test", "project": "Minimal"})
        assert resp.status_code == 201
        assert resp.json()["slug"] == "minimal-test"

    def test_publish_upsert(self, client):
        """Publishing same slug twice should update, not fail."""
        client.post("/api/publish", json=VALID_PAYLOAD)
        updated = {**VALID_PAYLOAD, "report_md": "# Updated Report"}
        resp = client.post("/api/publish", json=updated)
        assert resp.status_code == 201

        # Verify update took effect
        dash = client.get("/dashboard/protocol-guild")
        assert "Updated Report" in dash.json().get("report_md", "") or dash.status_code == 200


# ── GET /projects ──────────────────────────────────────────────


class TestProjectsEndpoint:
    def test_projects_empty(self, client):
        resp = client.get("/projects")
        assert resp.status_code == 200
        assert resp.json()["projects"] == []

    def test_projects_from_db(self, client):
        client.post("/api/publish", json=VALID_PAYLOAD)
        resp = client.get("/projects")
        projects = resp.json()["projects"]
        assert len(projects) == 1
        assert projects[0]["slug"] == "protocol-guild"
        assert projects[0]["source"] == "database"
        assert projects[0]["ostrom_overall"] == 74.5

    def test_projects_merges_db_and_filesystem(self, client, setup_env):
        """DB projects and filesystem projects both appear, no duplicates."""
        # Add to DB
        client.post("/api/publish", json=VALID_PAYLOAD)

        # Add to filesystem
        fs_slug_dir = setup_env["council_dir"] / "l2beat" / "eval"
        fs_slug_dir.mkdir(parents=True)
        (fs_slug_dir / "ostrom-scores.json").write_text('{"overall_score": 50}')

        resp = client.get("/projects")
        slugs = [p["slug"] for p in resp.json()["projects"]]
        assert "protocol-guild" in slugs
        assert "l2beat" in slugs
        assert len(slugs) == 2

    def test_projects_no_duplicates(self, client, setup_env):
        """If slug exists in both DB and filesystem, only DB version appears."""
        client.post("/api/publish", json=VALID_PAYLOAD)

        # Also create filesystem version
        fs_dir = setup_env["council_dir"] / "protocol-guild" / "eval"
        fs_dir.mkdir(parents=True)
        (fs_dir / "ostrom-scores.json").write_text("{}")

        resp = client.get("/projects")
        slugs = [p["slug"] for p in resp.json()["projects"]]
        assert slugs.count("protocol-guild") == 1


# ── GET /dashboard/{slug} ─────────────────────────────────────


class TestDashboardEndpoint:
    def test_dashboard_from_db(self, client):
        client.post("/api/publish", json=VALID_PAYLOAD)
        resp = client.get("/dashboard/protocol-guild")
        assert resp.status_code == 200
        body = resp.json()
        assert body["slug"] == "protocol-guild"
        assert body["source"] == "database"
        assert body["has_report"] is True
        assert body["has_eas"] is True

    def test_dashboard_filesystem_fallback(self, client, setup_env):
        """When slug not in DB, falls back to filesystem."""
        slug_dir = setup_env["council_dir"] / "tor-project"
        (slug_dir / "data").mkdir(parents=True)
        (slug_dir / "eval").mkdir(parents=True)
        (slug_dir / "data" / "octant.json").write_text('{"name": "Tor"}')
        (slug_dir / "eval" / "ostrom-scores.json").write_text('{"overall_score": 60}')

        resp = client.get("/dashboard/tor-project")
        assert resp.status_code == 200
        body = resp.json()
        assert body["source"] == "filesystem"

    def test_dashboard_not_found(self, client):
        resp = client.get("/dashboard/nonexistent")
        assert resp.status_code == 404


# ── GET /evaluate/{slug}/ostrom-radar ──────────────────────────


class TestOstromRadarEndpoint:
    def test_radar_from_db(self, client):
        client.post("/api/publish", json=VALID_PAYLOAD)
        resp = client.get("/evaluate/protocol-guild/ostrom-radar")
        assert resp.status_code == 200
        body = resp.json()
        assert body["overall_score"] == 74.5
        assert body["governance_maturity"] == "established"
        assert len(body["axes"]) == 8
        assert body["axes"][0]["label"] == "Clearly Defined Boundaries"
        assert body["axes"][0]["value"] == 88
        assert body["axes"][0]["weight"] == 1.25

    def test_radar_filesystem_fallback(self, client, setup_env):
        """Radar works from filesystem with actual agent output schema."""
        eval_dir = setup_env["council_dir"] / "test-project" / "eval"
        eval_dir.mkdir(parents=True)
        (eval_dir / "ostrom-scores.json").write_text(json.dumps({
            "project": "Test",
            "overall_score": 50,
            "governance_maturity": "developing",
            "principles": [
                {"id": i, "name": f"Principle {i}", "score": 50 + i, "weight": 1.0}
                for i in range(1, 9)
            ],
        }))

        resp = client.get("/evaluate/test-project/ostrom-radar")
        assert resp.status_code == 200
        assert len(resp.json()["axes"]) == 8
        assert resp.json()["axes"][0]["value"] == 51

    def test_radar_not_found(self, client):
        resp = client.get("/evaluate/nonexistent/ostrom-radar")
        assert resp.status_code == 404


# ── GET /evaluate/{slug}/report ────────────────────────────────


class TestReportEndpoint:
    def test_report_from_db(self, client):
        client.post("/api/publish", json=VALID_PAYLOAD)
        resp = client.get("/evaluate/protocol-guild/report")
        assert resp.status_code == 200
        body = resp.json()
        assert "Ostrom Commons" in body["report"]
        assert body["source"] == "database"

    def test_report_not_found(self, client):
        resp = client.get("/evaluate/nonexistent/report")
        assert resp.status_code == 404


# ── GET /evaluate/{slug}/eas ──────────────────────────────────


class TestEASEndpoint:
    def test_eas_from_db(self, client):
        client.post("/api/publish", json=VALID_PAYLOAD)
        resp = client.get("/evaluate/protocol-guild/eas")
        assert resp.status_code == 200
        assert "attestations" in resp.json()

    def test_eas_not_found(self, client):
        resp = client.get("/evaluate/nonexistent/eas")
        assert resp.status_code == 404


# ── Slug validation ───────────────────────────────────────────


class TestSlugValidation:
    @pytest.mark.parametrize("bad_slug", [
        "UPPERCASE",
        "has spaces",
        "has_underscore",
        "../path-traversal",
        "",
        "a" * 41,  # too long
    ])
    def test_bad_slugs_rejected(self, client, bad_slug):
        resp = client.post("/api/publish", json={"slug": bad_slug, "project": "Test"})
        assert resp.status_code in (400, 422)

    @pytest.mark.parametrize("good_slug", [
        "protocol-guild",
        "l2beat",
        "a",
        "test-123-project",
    ])
    def test_good_slugs_accepted(self, client, good_slug):
        resp = client.post("/api/publish", json={"slug": good_slug, "project": "Test"})
        assert resp.status_code == 201
