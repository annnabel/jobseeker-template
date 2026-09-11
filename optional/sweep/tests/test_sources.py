"""Adapter tests: each ATS adapter against the payload shape it documents.

The adapters are the one part of the sweep that talks to the outside world,
and each one's docstring describes the response shape it reads. These tests
pin that reading with a representative payload per adapter, with the HTTP
helper replaced, so a refactor that mis-reads a field fails here instead of
producing an empty morning. They cannot notice a live API changing shape;
that still shows up as a board reporting zero postings in the morning report.

Also covered: fetch.py's per-target loop, where one dead adapter must log and
continue, and the location, role and freshness filters are applied to what
the adapters return.
"""
import os
import sys
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # optional/sweep
BIN = os.path.join(ROOT, "bin")
sys.path.insert(0, os.path.join(BIN, "lib"))
sys.path.insert(0, BIN)

from sources import (  # noqa: E402
    ashby,
    greenhouse,
    lever,
    oracle,
    pageup,
    recruitee,
    smartrecruiters,
    teamtailor,
    workable,
    workday,
)


class FakeHttp:
    """Stand-in for sources._http.get_json / post_json.

    `routes` maps a substring of the URL to the JSON to return (or an
    exception to raise). Every call is recorded so a test can assert how many
    requests a board cost and what was sent.
    """

    def __init__(self, routes):
        self.routes = routes
        self.calls: list[dict] = []

    def _dispatch(self, url):
        for key, value in self.routes.items():
            if key in url:
                if isinstance(value, Exception):
                    raise value
                return value
        raise AssertionError(f"unexpected request: {url}")

    def get_json(self, url, params=None, headers=None):
        self.calls.append({"method": "GET", "url": url, "params": params, "headers": headers})
        return self._dispatch(url)

    def post_json(self, url, json_body):
        self.calls.append({"method": "POST", "url": url, "body": json_body})
        return self._dispatch(url)


@pytest.fixture(autouse=True)
def no_pacing(monkeypatch):
    # Adapters that page or fetch detail self-pace with time.sleep; not in tests.
    monkeypatch.setattr(time, "sleep", lambda *_: None)


def wire(monkeypatch, module, http):
    """Point one adapter's imported HTTP helpers at the fake."""
    monkeypatch.setattr(module, "get_json", http.get_json)
    if hasattr(module, "post_json"):
        monkeypatch.setattr(module, "post_json", http.post_json)


# ── single-call boards ─────────────────────────────────────────────────────


def test_greenhouse_reads_location_from_offices_and_strips_html(monkeypatch):
    http = FakeHttp({
        "boards-api.greenhouse.io/v1/boards/acme/jobs": {
            "jobs": [
                {
                    "title": "Example Role",
                    "location": {"name": "Riverton, Eastland"},
                    "absolute_url": "https://boards.greenhouse.io/acme/jobs/1",
                    "departments": [{"name": "Operations"}],
                    "updated_at": "2026-07-01T00:00:00Z",
                    "content": "<p>Do the <b>work</b>.</p>",
                },
                {
                    # No `location`: the first office stands in.
                    "title": "Second Role",
                    "location": None,
                    "offices": [{"name": "Lakeside"}],
                    "absolute_url": "https://boards.greenhouse.io/acme/jobs/2",
                    "departments": [],
                    "updated_at": None,
                    "content": None,
                },
            ]
        }
    })
    wire(monkeypatch, greenhouse, http)
    out = greenhouse.fetch("acme")
    assert [p.title for p in out] == ["Example Role", "Second Role"]
    assert out[0].location == "Riverton, Eastland"
    assert out[0].department == "Operations"
    assert out[0].description == "Do the  work ."
    assert out[1].location == "Lakeside"
    assert out[1].updated_at == "" and out[1].description == ""
    assert http.calls[0]["params"] == {"content": "true"}


def test_lever_reads_categories_and_keeps_epoch_millis(monkeypatch):
    http = FakeHttp({
        "api.lever.co/v0/postings/acme": [
            {
                "text": "Example Role",
                "categories": {"location": "Riverton", "team": "Operations"},
                "hostedUrl": "https://jobs.lever.co/acme/1",
                "createdAt": 1782864000000,
                "descriptionPlain": "Do the work.",
            }
        ]
    })
    wire(monkeypatch, lever, http)
    (p,) = lever.fetch("acme")
    assert (p.title, p.location, p.department) == ("Example Role", "Riverton", "Operations")
    assert p.updated_at == "1782864000000"   # a string filters.parse_updated_at accepts
    assert p.url == "https://jobs.lever.co/acme/1"
    assert http.calls[0]["params"] == {"mode": "json"}


def test_ashby_reads_flat_job_fields(monkeypatch):
    http = FakeHttp({
        "api.ashbyhq.com/posting-api/job-board/acme": {
            "jobs": [
                {
                    "title": "Example Role",
                    "location": "Riverton",
                    "jobUrl": "https://jobs.ashbyhq.com/acme/1",
                    "department": "Operations",
                    "publishedAt": "2026-07-01T00:00:00Z",
                    "descriptionPlain": "Do the work.",
                }
            ]
        }
    })
    wire(monkeypatch, ashby, http)
    (p,) = ashby.fetch("acme")
    assert (p.title, p.location, p.url) == (
        "Example Role", "Riverton", "https://jobs.ashbyhq.com/acme/1"
    )
    assert p.company == "acme" and p.updated_at == "2026-07-01T00:00:00Z"


def test_workable_location_shapes(monkeypatch):
    http = FakeHttp({
        "apply.workable.com/api/v1/widget/accounts/acme": {
            "name": "Acme",
            "jobs": [
                {"title": "Flat", "city": "Riverton", "state": "Northshire", "country": "Eastland",
                 "url": "https://apply.workable.com/acme/j/1", "published_on": "2026-07-01"},
                {"title": "Nested", "location": {"city": "Lakeside", "region": "", "country": "Eastland"}},
                {"title": "Multi", "locations": [{"city": "Bayview", "country": "Eastland"}]},
                {"title": "Remote", "telecommuting": True},
                {"title": "Unknown"},
            ],
        }
    })
    wire(monkeypatch, workable, http)
    out = {p.title: p for p in workable.fetch("acme")}
    assert all(p.company == "Acme" for p in out.values())
    assert out["Flat"].location == "Riverton, Northshire, Eastland"
    assert out["Nested"].location == "Lakeside, Eastland"
    assert out["Multi"].location == "Bayview, Eastland"
    assert out["Remote"].location == "Remote"
    assert out["Unknown"].location == ""      # unknown goes to triage, not the bin
    assert http.calls[0]["params"] == {"details": "true"}


def test_recruitee_skips_unpublished_and_normalises_dates(monkeypatch):
    http = FakeHttp({
        "acme.recruitee.com/api/offers/": {
            "offers": [
                {
                    "status": "published",
                    "title": "Example Role",
                    "location": "Riverton, Eastland",
                    "description": "<p>Do the work.</p>",
                    "requirements": "<ul><li>A licence</li></ul>",
                    "careers_url": "https://acme.recruitee.com/o/example-role",
                    "company_name": "Acme",
                    "published_at": "2026-07-01 10:00:00 UTC",
                },
                {"status": "draft", "title": "Not Live"},
                {
                    # No `location` string: built from the structured parts.
                    "status": "published", "title": "Structured",
                    "city": "Lakeside", "state_name": "", "country": "Eastland",
                    "created_at": "someday",
                },
            ]
        }
    })
    wire(monkeypatch, recruitee, http)
    out = {p.title: p for p in recruitee.fetch("acme")}
    assert set(out) == {"Example Role", "Structured"}
    assert out["Example Role"].company == "Acme"
    assert out["Example Role"].description == "Do the work.\n\nA licence"
    assert out["Example Role"].updated_at == "2026-07-01T10:00:00+00:00"
    assert out["Structured"].location == "Lakeside, Eastland"
    assert out["Structured"].updated_at == "someday"   # unparseable stays as-is: fails open


def test_teamtailor_joins_locations_and_applies_the_filter_early(monkeypatch):
    def item(title, *places):
        return {
            "title": title,
            "url": f"https://careers.acme.example/jobs/{title.lower()}",
            "date_published": "2026-07-01T00:00:00Z",
            "_jobposting": {
                "hiringOrganization": {"name": "Acme"},
                "description": "<p>Do the work.</p>",
                "jobLocation": [
                    {"address": {"addressLocality": city, "addressCountry": country}}
                    for city, country in places
                ],
            },
        }

    http = FakeHttp({
        "careers.acme.example/jobs.json": {
            "items": [
                item("Near", ("Riverton", "Eastland"), ("Lakeside", "Eastland")),
                item("Far", ("Elsewhere", "Otherland")),
                {"title": "Bare", "url": "", "_jobposting": {"jobLocation": {"address": {}}}},
            ]
        }
    })
    wire(monkeypatch, teamtailor, http)
    out = {p.title: p for p in teamtailor.fetch("careers.acme.example", ["riverton"])}
    assert set(out) == {"Near", "Bare"}          # Far is filtered; Bare has no location
    assert out["Near"].location == "Riverton, Eastland; Lakeside, Eastland"
    assert out["Near"].company == "Acme" and out["Near"].description == "Do the work."
    assert out["Bare"].company == "careers"      # falls back to the host's first label


# ── paged boards and detail calls ──────────────────────────────────────────


def test_smartrecruiters_pages_and_skips_detail_outside_the_filter(monkeypatch):
    def job(i, city):
        return {"id": f"j{i}", "name": f"Role {i}", "releasedDate": "2026-07-01T00:00:00Z",
                "location": {"city": city, "country": "Eastland", "remote": i == 2},
                "company": {"name": "Acme"}, "department": {"label": "Operations"}}

    http = FakeHttp({
        "postings/j1": {"jobAd": {"sections": {"jobDescription": {"text": "<p>One</p>"},
                                              "qualifications": {"text": "A licence"}}},
                        "postingUrl": "https://jobs.smartrecruiters.com/acme/j1"},
        "postings/j2": {"jobAd": {"sections": {}}},
        "postings/j3": AssertionError("detail must not be fetched for a filtered posting"),
        "postings": None,  # list endpoint; replaced below to page by offset
    })
    pages = {0: {"content": [job(1, "Riverton"), job(2, "Lakeside")], "totalFound": 3},
             2: {"content": [job(3, "Elsewhere")], "totalFound": 3}}

    real_get = http.get_json

    def get_json(url, params=None, headers=None):
        if url.endswith("/postings"):
            http.calls.append({"method": "GET", "url": url, "params": params})
            return pages[params["offset"]]
        return real_get(url, params, headers)

    monkeypatch.setattr(smartrecruiters, "get_json", get_json)
    out = smartrecruiters.fetch("acme", ["riverton", "lakeside"])
    assert [p.title for p in out] == ["Role 1", "Role 2"]
    assert out[0].description == "One A licence"
    assert out[0].url == "https://jobs.smartrecruiters.com/acme/j1"
    assert out[1].location == "Lakeside, Eastland (Remote)"
    assert out[1].url == "https://jobs.smartrecruiters.com/acme/j2"   # detail had no URL
    list_calls = [c for c in http.calls if c["url"].endswith("/postings")]
    assert [c["params"]["offset"] for c in list_calls] == [0, 2]
    assert not any(c["url"].endswith("/j3") for c in http.calls)


def test_oracle_parses_slug_pages_and_filters_by_primary_location(monkeypatch):
    with pytest.raises(ValueError):
        oracle.fetch("not-a-host-and-site")

    def req(i, location):
        return {"Id": str(i), "Title": f"Role {i}", "PrimaryLocation": location,
                "ShortDescriptionStr": "<p>Short</p>", "ExternalQualificationsStr": "A licence",
                "JobFamily": "Operations", "PostedDate": "2026-07-01"}

    pages = [
        {"items": [{"TotalJobsCount": 3, "requisitionList": [req(1, "Riverton"), req(2, "Elsewhere")]}]},
        {"items": [{"TotalJobsCount": 3, "requisitionList": [req(3, "Lakeside")]}]},
    ]
    http = FakeHttp({})

    def get_json(url, params=None, headers=None):
        http.calls.append({"url": url})
        return pages[len(http.calls) - 1]

    monkeypatch.setattr(oracle, "get_json", get_json)
    out = oracle.fetch("pod.example.oraclecloud.com/CX", ["riverton", "lakeside"])
    assert [p.title for p in out] == ["Role 1", "Role 3"]
    assert out[0].company == "pod"
    assert out[0].description == "Short  A licence"   # tag-stripper leaves a space per tag
    assert out[0].url.endswith("/sites/CX/job/1")
    assert len(http.calls) == 2
    assert "offset=0" in http.calls[0]["url"] and "offset=2" in http.calls[1]["url"]


def test_pageup_sends_the_ajax_header_and_pages_until_count(monkeypatch):
    def fragment(*ids):
        return "".join(
            f'<li><a class="job-link" href="/410/fb/en/job/{i}/role-{i}">Role &amp; {i}</a></li>'
            for i in ids
        )

    pages = {1: {"results": fragment(1, 2), "count": 3}, 2: {"results": fragment(3), "count": 3}}
    http = FakeHttp({})

    def get_json(url, params=None, headers=None):
        http.calls.append({"url": url, "params": params, "headers": headers})
        return pages[params["page"]]

    monkeypatch.setattr(pageup, "get_json", get_json)
    out = pageup.fetch("410/fb/en")
    assert [p.title for p in out] == ["Role & 1", "Role & 2", "Role & 3"]
    assert out[0].url == "https://careers.pageuppeople.com/410/fb/en/job/1/role-1"
    assert out[0].company == "410" and out[0].location == ""
    assert len(http.calls) == 2
    assert all(c["headers"] == {"X-Requested-With": "XMLHttpRequest"} for c in http.calls)
    assert all(c["params"]["data"] == "json" for c in http.calls)


def test_workday_scopes_by_facet_then_pages_and_fetches_detail(monkeypatch):
    listing = {
        "jobPostings": [
            {"title": "Near", "locationsText": "Riverton, Eastland", "externalPath": "/job/near"},
            {"title": "Aggregate", "locationsText": "3 Locations", "externalPath": "/job/agg"},
            {"title": "No path", "locationsText": "Riverton, Eastland"},
        ],
        "total": 3,
        "facets": [
            {"facetParameter": "locations", "values": [
                {"facetParameter": "locationCountry", "values": [
                    {"descriptor": "Eastland", "id": "country-1", "count": 3},
                    {"descriptor": "Otherland", "id": "country-2", "count": 9},
                ]},
                {"facetParameter": "locationCity", "values": [
                    {"descriptor": "Riverton", "id": "city-1", "count": 1},
                ]},
            ]},
        ],
    }
    http = FakeHttp({
        "/jobs": listing,
        "/job/near": {"jobPostingInfo": {
            "title": "Near (detail)", "location": "Riverton, Eastland",
            "externalUrl": "https://acme.wd3.myworkdayjobs.com/site/job/near",
            "startDate": "2026-07-01", "jobDescription": "<p>Do the work.</p>",
        }},
    })
    wire(monkeypatch, workday, http)
    out = workday.fetch("acme/wd3/Careers", ["riverton", "eastland"])

    (p,) = out
    assert p.title == "Near (detail)" and p.company == "acme"
    assert p.description == "Do the work." and p.updated_at == "2026-07-01"
    assert p.url == "https://acme.wd3.myworkdayjobs.com/site/job/near"

    posts = [c for c in http.calls if c["method"] == "POST"]
    # Discovery (limit 1, no facets), then one page scoped to the country
    # facet: broader than the matching city facet, and only one parameter.
    assert posts[0]["body"]["limit"] == 1 and posts[0]["body"]["appliedFacets"] == {}
    assert posts[1]["body"]["appliedFacets"] == {"locationCountry": ["country-1"]}
    gets = [c for c in http.calls if c["method"] == "GET"]
    assert [c["url"].rsplit("/", 1)[-1] for c in gets] == ["near"]   # aggregate + pathless skipped


def test_workday_falls_back_to_a_plain_scan_without_matching_facets(monkeypatch):
    http = FakeHttp({
        "/jobs": {"jobPostings": [], "total": 0, "facets": []},
    })
    wire(monkeypatch, workday, http)
    assert workday.fetch("acme/wd3/Careers", ["riverton"]) == []
    posts = [c for c in http.calls if c["method"] == "POST"]
    assert posts[1]["body"]["appliedFacets"] == {}
    with pytest.raises(ValueError):
        workday.fetch("acme/Careers")


# ── fetch.py: the per-target loop ──────────────────────────────────────────


def test_fetch_all_survives_one_dead_adapter_and_applies_every_filter(monkeypatch, capsys):
    from datetime import datetime, timezone

    import fetch
    from schema import Posting

    recent = datetime.now(tz=timezone.utc).isoformat()

    def posting(title, location, updated_at=None):
        return Posting(source="fake", slug="acme", company="acme", title=title,
                       location=location, updated_at=updated_at or recent)

    class Good:
        @staticmethod
        def fetch(slug, location_filter=None):
            return [
                posting("Example Role", "Riverton"),
                posting("Example Role", "Elsewhere"),          # outside location filter
                posting("Unrelated Role", "Riverton"),        # outside role filter
                posting("Old Role", "Riverton", "2020-01-01"),  # stale
                posting("Undated Role", ""),                  # unknown location and age: kept
            ]

    class Dead:
        @staticmethod
        def fetch(slug, location_filter=None):
            raise RuntimeError("board offline")

    monkeypatch.setattr(fetch, "get_adapter", lambda ats: {"good": Good, "dead": Dead}[ats])
    targets = [
        {"ats": "good", "slug": "acme"},
        {"ats": "dead", "slug": "other"},
        {"slug": "malformed-no-ats"},
    ]
    postings, failures, attempted, role_dropped = fetch.fetch_all(
        targets, "all", ["riverton"], max_age_days=30,
        role_patterns=["example", "old", "undated"],
    )
    assert sorted(p.title for p in postings) == ["Example Role", "Undated Role"]
    assert (failures, attempted, role_dropped) == (1, 2, 1)
    err = capsys.readouterr().err
    assert "adapter dead/other failed: board offline" in err
    assert "skipping malformed target" in err
    assert "1 outside location filter, 1 outside role filter, 1 stale" in err

    # --source narrows to one adapter without counting the others as failures.
    postings, failures, attempted, _ = fetch.fetch_all(targets, "dead", ["riverton"])
    assert (postings, failures, attempted) == ([], 1, 1)
