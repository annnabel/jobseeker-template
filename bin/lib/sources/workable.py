"""Workable widget adapter. PRD §4.1.

    https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true
"""
from __future__ import annotations

from schema import Posting
from sources._http import get_json

BASE = "https://apply.workable.com/api/v1/widget/accounts/{slug}"


def fetch(slug: str, location_filter: list[str] | None = None) -> list[Posting]:
    data = get_json(BASE.format(slug=slug), params={"details": "true"})
    jobs = data.get("jobs", []) if isinstance(data, dict) else []
    company = data.get("name", slug) if isinstance(data, dict) else slug
    out: list[Posting] = []
    for job in jobs:
        loc = job.get("location") or {}
        city = loc.get("city", "")
        country = loc.get("country", "")
        location = ", ".join(x for x in (city, country) if x)
        out.append(
            Posting(
                source="workable",
                slug=slug,
                company=company,
                title=job.get("title", ""),
                location=location or ("Remote" if loc.get("workplace") == "remote" else ""),
                url=job.get("url", "") or job.get("application_url", ""),
                department=job.get("department", ""),
                updated_at=job.get("published_on", ""),
                description=job.get("description", ""),
            )
        )
    return out
