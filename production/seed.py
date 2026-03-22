#!/usr/bin/env python3
"""
Seed the evaluator database with evaluation data.
Reads real data from council-out/ and generates realistic data for demo projects.

Usage:
  python3 seed.py                          # seed local SQLite
  python3 seed.py https://your-api.railway.app  # seed remote API
"""
import json
import sys
import os
from pathlib import Path

# If a URL is passed, POST to it. Otherwise, use the DB directly.
API_URL = sys.argv[1] if len(sys.argv) > 1 else None

COUNCIL_OUT = Path(os.getenv("COUNCIL_OUT_DIR", "council-out"))


def safe_read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def safe_read_text(path: Path):
    try:
        return path.read_text()
    except FileNotFoundError:
        return None


def load_real_project(slug: str, project_name: str) -> dict | None:
    """Load a real evaluation from council-out/."""
    slug_dir = COUNCIL_OUT / slug
    if not slug_dir.exists():
        return None

    return {
        "slug": slug,
        "project": project_name,
        "ostrom_scores": safe_read_json(slug_dir / "eval" / "ostrom-scores.json"),
        "quant_scores": safe_read_json(slug_dir / "eval" / "quant.json"),
        "qual_json": safe_read_json(slug_dir / "eval" / "qual.json"),
        "eas_json": safe_read_json(slug_dir / "synth" / "eas-attestations.json"),
        "report_md": safe_read_text(slug_dir / "REPORT.md"),
        "ostrom_report_md": safe_read_text(slug_dir / "synth" / "ostrom-report.md"),
        "data": {
            "octant": safe_read_json(slug_dir / "data" / "octant.json"),
            "karma": safe_read_json(slug_dir / "data" / "karma.json"),
            "social": safe_read_json(slug_dir / "data" / "social.json"),
            "global": safe_read_json(slug_dir / "data" / "global.json"),
        },
        "metadata": {
            "evaluated_at": "2026-03-22T00:00:00Z",
            "agent_count": 19,
            "wave_count": 3,
        },
    }


def make_demo_project(slug: str, project_name: str, overall: float, maturity: str,
                      scores: list[int], composite: int, summary: str,
                      recommendation: str, composite_10: int) -> dict:
    """Generate a realistic demo evaluation."""
    principle_names = [
        "Clearly Defined Boundaries",
        "Congruence with Local Conditions",
        "Collective-Choice Arrangements",
        "Monitoring",
        "Graduated Sanctions",
        "Conflict-Resolution Mechanisms",
        "Minimal Recognition of Rights to Organize",
        "Nested Enterprises",
    ]
    weights = [1.25, 1.0, 1.25, 1.25, 0.75, 1.0, 1.0, 1.0]

    principles = []
    for i, (name, score, weight) in enumerate(zip(principle_names, scores, weights)):
        principles.append({
            "id": i + 1,
            "name": name,
            "score": score,
            "weight": weight,
            "evidence": [f"Evidence for {name} assessment of {project_name}"],
            "gaps": [],
        })

    return {
        "slug": slug,
        "project": project_name,
        "ostrom_scores": {
            "project": project_name,
            "overall_score": overall,
            "governance_maturity": maturity,
            "principles": principles,
        },
        "quant_scores": {
            "project": project_name,
            "composite_score": composite,
            "scores": {
                "activity": {"score": composite - 5},
                "funding_efficiency": {"score": composite - 10},
                "ecosystem_impact": {"score": composite + 5},
                "growth_trajectory": {"score": composite - 3},
                "transparency": {"score": composite + 2},
            },
        },
        "qual_json": {
            "project": project_name,
            "summary": summary,
            "strengths": [f"{project_name} demonstrates strong community engagement"],
            "concerns": ["Funding diversification could improve"],
        },
        "eas_json": {
            "attestations": [{
                "schema": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "data": {
                    "recipient": "0x0000000000000000000000000000000000000000",
                    "data": {
                        "projectSlug": slug,
                        "ostromOverallScore": int(overall),
                        "quantCompositeScore": composite,
                        "governanceMaturity": maturity,
                    },
                },
            }],
        },
        "report_md": f"# Council Report: {project_name}\n\n**Recommendation: {recommendation}**\n**Composite Score: {composite_10}/10**\n\n## Executive Summary\n\n{summary}",
        "ostrom_report_md": f"# {project_name} — Ostrom Commons Evaluation Report\n\n**Overall Ostrom Score: {overall} / 100**\n**Governance Maturity: {maturity.title()}**\n\n{summary}",
        "metadata": {
            "evaluated_at": "2026-03-22T00:00:00Z",
            "agent_count": 19,
            "wave_count": 3,
            "demo": True,
        },
    }


# ── Project Data ──────────────────────────────────────────────

DEMO_PROJECTS = [
    make_demo_project(
        slug="l2beat",
        project_name="L2BEAT",
        overall=71.0,
        maturity="established",
        scores=[85, 78, 72, 88, 35, 52, 75, 68],
        composite=81,
        summary="L2BEAT is the definitive Layer 2 analytics and research platform for the Ethereum ecosystem. It provides TVL tracking, risk assessments, and detailed technical comparisons across all major rollups. With a dedicated team, active community, and deep integration into Ethereum governance discussions, L2BEAT serves as critical infrastructure for L2 accountability and informed decision-making.",
        recommendation="FUND",
        composite_10=8,
    ),
    make_demo_project(
        slug="growthepie",
        project_name="growthepie",
        overall=58.5,
        maturity="developing",
        scores=[70, 65, 55, 72, 30, 45, 62, 55],
        composite=68,
        summary="growthepie provides open-source L2 analytics with a focus on user-friendly data visualization and comparative metrics across Ethereum rollups. The project differentiates from L2BEAT through its emphasis on growth metrics, user activity, and fee analysis. Still in active development with a growing contributor base and increasing visibility in the ecosystem.",
        recommendation="FUND WITH CONDITIONS",
        composite_10=7,
    ),
    make_demo_project(
        slug="revoke-cash",
        project_name="Revoke.cash",
        overall=64.0,
        maturity="established",
        scores=[82, 70, 58, 75, 42, 50, 72, 60],
        composite=74,
        summary="Revoke.cash is a critical security tool that allows users to revoke token approvals across 80+ EVM chains. It addresses a fundamental security gap in the Ethereum ecosystem — unlimited token approvals that persist indefinitely. The project has prevented millions in potential losses and serves as essential defensive infrastructure.",
        recommendation="FUND",
        composite_10=7,
    ),
    make_demo_project(
        slug="tor-project",
        project_name="Tor Project",
        overall=79.5,
        maturity="established",
        scores=[92, 85, 80, 82, 70, 65, 88, 75],
        composite=83,
        summary="The Tor Project provides the world's most widely used privacy infrastructure, protecting millions of users from surveillance and censorship. Its mature governance, transparent operations, and deep institutional support make it one of the most well-governed public goods in existence. The Ethereum ecosystem benefits directly from Tor's privacy infrastructure for node operators, developers, and users.",
        recommendation="FUND",
        composite_10=8,
    ),
]


def publish_to_api(project: dict):
    """POST project data to the evaluator API."""
    import urllib.request
    import urllib.error

    url = f"{API_URL}/api/publish"
    data = json.dumps(project).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"  Published {project['slug']}: {result.get('url', 'ok')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"  FAILED {project['slug']}: {e.code} {body[:200]}")
    except Exception as e:
        print(f"  FAILED {project['slug']}: {e}")


def publish_to_db(project: dict):
    """Write directly to local SQLite DB."""
    sys.path.insert(0, str(Path(__file__).parent / "backend" / "evaluator"))
    from db import publish_evaluation
    result = publish_evaluation(project)
    print(f"  Stored {project['slug']}: {result.get('published_at', 'ok')}")


def main():
    print("Seeding evaluation data...\n")
    publish = publish_to_api if API_URL else publish_to_db

    # 1. Real project from council-out/
    real = load_real_project("protocol-guild", "Protocol Guild")
    if real:
        print("Protocol Guild (real evaluation data):")
        publish(real)
    else:
        print("Protocol Guild: no council-out/ data found, using demo data")
        publish(make_demo_project(
            slug="protocol-guild",
            project_name="Protocol Guild",
            overall=74.5,
            maturity="established",
            scores=[88, 82, 76, 90, 38, 55, 78, 72],
            composite=86,
            summary="Protocol Guild is the only mechanism purpose-built to systematically fund Ethereum's layer 1 core protocol maintainers across all major client teams. With $100M+ in cumulative donations and 187-190 members, it represents best-in-class public goods infrastructure.",
            recommendation="FUND",
            composite_10=8,
        ))

    # 2. Demo projects
    for project in DEMO_PROJECTS:
        print(f"\n{project['project']} (demo data):")
        publish(project)

    print(f"\nDone! Seeded {1 + len(DEMO_PROJECTS)} projects.")
    if not API_URL:
        print(f"Database: {os.getenv('DATABASE_PATH', 'evaluations.db')}")
    else:
        print(f"API: {API_URL}")


if __name__ == "__main__":
    main()
