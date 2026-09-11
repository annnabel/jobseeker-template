"""Sweep-only tests: fetch, filters, schema, HTTP retry scope.

These moved out of tests/test_acceptance.py when the sweep became an optional,
quarantined add-on. They exercise optional/sweep/bin and nothing in bin/.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # optional/sweep
BIN = os.path.join(ROOT, "bin")


def run(script, *args):
    return subprocess.run(
        [sys.executable, os.path.join(BIN, script), *args],
        capture_output=True,
        text=True,
    )


# ── fetch.py dry-run ───────────────────────────────────────────────────────


def test_fetch_dry_run_no_targets(tmp_path):
    # With no targets.yaml the dry run must still exit 0 (nothing to do).
    r = run("fetch.py", "--dry-run", "--root", str(tmp_path))
    assert r.returncode == 0, r.stderr


def test_fetch_survives_a_profile_yaml_that_is_not_a_mapping(tmp_path):
    # A hand-edited profile file that parses to a list must degrade to "no
    # targets, no role filter" with a warning, never an AttributeError.
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "targets.yaml").write_text("- example-co\n- another-co\n", encoding="utf-8")
    (profile / "goals.yaml").write_text("- a track\n", encoding="utf-8")
    r = run("fetch.py", "--dry-run", "--root", str(tmp_path))
    assert r.returncode == 0, r.stderr
    assert "not a mapping" in r.stderr
    assert "Traceback" not in r.stderr


def test_location_filter_matching():
    sys.path.insert(0, os.path.join(BIN, "lib"))
    from filters import location_matches

    # Placeholder place names: the filter is regex-only and knows no geography,
    # so the test exercises the shapes boards actually print, not a real region.
    patterns = [
        "riverton", "eastland", r"\bel\b", r"\bels\b", r"\bnorthshire\b",
        "lakeside", "bayview", "hillcrest", "pinegrove", "westport",
    ]
    for loc in (
        "Riverton, Northshire, Eastland",
        "EL - Riverton",
        "EL: Riverton (45 Market St)",
        "Lakeside, el",
        "Lakeside",  # some boards report a bare city, no country token
        "Remote - ELS",
        "",  # unknown location goes to triage, not the bin
    ):
        assert location_matches(loc, patterns), loc
    # Near misses the word boundaries must reject: "Elsewhere" contains "els",
    # "Riverside" is not "Riverton", and an unlisted country is out.
    for loc in ("Elsewhere, Texas", "London, UK", "US Remote", "Riverside, NZ"):
        assert not location_matches(loc, patterns), loc
    # No filter configured -> keep everything.
    assert location_matches("London, UK", [])


def test_freshness_filter():
    sys.path.insert(0, os.path.join(BIN, "lib"))
    from datetime import datetime, timezone

    from filters import is_fresh, parse_updated_at

    now = datetime(2026, 7, 17, tzinfo=timezone.utc)
    # Fresh, across the formats the adapters actually emit.
    for value in (
        "2026-07-01T00:00:00Z",          # greenhouse/ashby/smartrecruiters ISO
        "2026-07-01T00:00:00+02:00",     # ISO with offset
        "2026-07-01",                    # workable bare date
        "1782864000000",                 # lever epoch millis (2026-07-01)
        "1782864000",                    # epoch seconds
        "",                              # unknown age goes to triage, not the bin
        "not-a-date",                    # unparseable likewise
    ):
        assert is_fresh(value, 30, now=now), value
    # Stale: last touched more than 30 days before `now`.
    for value in (
        "2026-06-01T00:00:00Z",
        "2026-01-15",
        "1743465600000",                 # 2025-04-01 in epoch millis
    ):
        assert not is_fresh(value, 30, now=now), value
    # 0 disables the filter entirely.
    assert is_fresh("2020-01-01", 0, now=now)
    # Unparseable values must read as unknown, never as a date.
    assert parse_updated_at("someday") is None
    assert parse_updated_at("") is None


# ── schema.py null-coalescing (adapter robustness) ─────────────────────────


def test_posting_coerces_null_fields():
    # An ATS payload with an explicit null for a read field must not sink the
    # whole board: Posting coerces None -> "" so one bad field costs nothing.
    sys.path.insert(0, os.path.join(BIN, "lib"))
    from schema import Posting

    p = Posting(
        source="greenhouse", slug="acme", company="acme",
        title=None, location=None, url=None, department=None,
        updated_at=None, description=None,
    )
    assert p.title == "" and p.location == "" and p.description == ""
    # A fingerprint is still derivable (no crash on the None-turned-empty).
    assert len(p.fingerprint()) == 64


# ── _http.py retry scope (fail fast on non-retryable 4xx) ──────────────────


def test_http_fails_fast_on_404(monkeypatch):
    sys.path.insert(0, os.path.join(BIN, "lib"))
    import time as _time

    import httpx

    from sources import _http

    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        req = httpx.Request(method, url)
        return httpx.Response(404, request=req, json={"error": "not found"})

    slept = {"n": 0}
    monkeypatch.setattr(httpx, "request", fake_request)
    monkeypatch.setattr(_time, "sleep", lambda *_: slept.__setitem__("n", slept["n"] + 1))

    try:
        _http.get_json("https://boards-api.greenhouse.io/v1/boards/nope/jobs")
    except httpx.HTTPStatusError:
        pass
    else:
        raise AssertionError("expected a 404 to raise")
    # One attempt, no retries, no backoff sleeps for a genuine 404.
    assert calls["n"] == 1, calls
    assert slept["n"] == 0, slept


def test_http_retries_on_500(monkeypatch):
    sys.path.insert(0, os.path.join(BIN, "lib"))
    import time as _time

    import httpx

    from sources import _http

    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        req = httpx.Request(method, url)
        return httpx.Response(503, request=req, json={})

    monkeypatch.setattr(httpx, "request", fake_request)
    monkeypatch.setattr(_time, "sleep", lambda *_: None)

    try:
        _http.get_json("https://boards-api.greenhouse.io/v1/boards/x/jobs")
    except httpx.HTTPStatusError:
        pass
    # A 5xx is transient: it exhausts MAX_RETRIES attempts.
    assert calls["n"] == _http.MAX_RETRIES, calls


# ── fetch.py location_filter validation ────────────────────────────────────


def test_fetch_rejects_bad_location_regex(tmp_path):
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "targets.yaml").write_text(
        "companies:\n  - slug: acme\n    ats: greenhouse\n"
        "location_filter:\n  - '['\n",  # unbalanced bracket -> re.error
        encoding="utf-8",
    )
    r = run("fetch.py", "--dry-run", "--root", str(tmp_path))
    assert r.returncode == 2, r.stderr
    assert "invalid location_filter regex" in r.stderr


# ── goals: role filter ─────────────────────────────────────────────────────


def test_role_filter_matching():
    sys.path.insert(0, os.path.join(BIN, "lib"))
    from filters import title_matches

    patterns = ["data analyst", "business analyst", "analytics", r"\binsights\b"]
    for title in (
        "Data Analyst",
        "Senior Business Analyst",
        "Analytics Engineer",
        "Insights Manager",
        "",  # unknown title goes to triage, not the bin
    ):
        assert title_matches(title, patterns), title
    for title in ("Registered Nurse", "Warehouse Associate", "Account Executive"):
        assert not title_matches(title, patterns), title
    # No filter configured -> keep everything (the default: off).
    assert title_matches("Registered Nurse", [])


def test_load_goals_missing_file(tmp_path):
    sys.path.insert(0, os.path.join(BIN, "lib"))
    from filters import load_goals, role_filter

    # An absent goals.yaml is a valid state (it arrives during /setup).
    assert load_goals(str(tmp_path)) == {}
    assert role_filter(load_goals(str(tmp_path))) == []
