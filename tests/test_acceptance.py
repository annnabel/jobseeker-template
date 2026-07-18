"""Phase 0 acceptance tests (PRD §11) plus the v3.1 amendments (PRD §14).

  * validate.py passes a good fixture and fails one with a missing ev
  * validate.py --cover fails a letter containing a number absent from its variant
  * the style gate fails em dashes and stock AI phrasing (resume and cover)
  * render.py emits a markdown resume and still enforces the ev floor
  * fetch.py --dry-run runs clean
  * tracker.py regeneration is byte-identical (Phase 7 invariant, checked early)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "bin")
FIX = os.path.join(ROOT, "tests", "fixtures")


def run(script, *args):
    return subprocess.run(
        [sys.executable, os.path.join(BIN, script), *args],
        capture_output=True,
        text=True,
    )


# ── validate.py resume mode ────────────────────────────────────────────────


def test_good_variant_passes():
    r = run(
        "validate.py",
        os.path.join(FIX, "variant_good.yaml"),
        "--bank", os.path.join(FIX, "evidence-bank.md"),
        "--resume", os.path.join(FIX, "resume.yaml"),
    )
    assert r.returncode == 0, r.stderr


def test_missing_ev_fails():
    r = run(
        "validate.py",
        os.path.join(FIX, "variant_missing_ev.yaml"),
        "--bank", os.path.join(FIX, "evidence-bank.md"),
        "--resume", os.path.join(FIX, "resume.yaml"),
    )
    assert r.returncode == 1, r.stderr
    assert "no evidence ID" in r.stderr


# ── validate.py cover mode ─────────────────────────────────────────────────


def test_good_cover_passes():
    r = run(
        "validate.py",
        "--cover", os.path.join(FIX, "cover_good.md"),
        "--variant", os.path.join(FIX, "variant_good.yaml"),
        "--bank", os.path.join(FIX, "evidence-bank.md"),
    )
    assert r.returncode == 0, r.stderr


def test_cover_bad_numeral_fails():
    r = run(
        "validate.py",
        "--cover", os.path.join(FIX, "cover_bad_numeral.md"),
        "--variant", os.path.join(FIX, "variant_good.yaml"),
        "--bank", os.path.join(FIX, "evidence-bank.md"),
    )
    assert r.returncode == 1, r.stderr
    assert "40" in r.stderr


# ── validate.py style gate (PRD §14) ───────────────────────────────────────

# A config path that doesn't exist forces validate.py's built-in banned list,
# keeping these tests independent of the user's profile/config.yaml.
NO_CONFIG = os.path.join(FIX, "no-such-config.yaml")


def test_cover_bad_style_fails():
    r = run(
        "validate.py",
        "--cover", os.path.join(FIX, "cover_bad_style.md"),
        "--variant", os.path.join(FIX, "variant_good.yaml"),
        "--bank", os.path.join(FIX, "evidence-bank.md"),
        "--config", NO_CONFIG,
    )
    assert r.returncode == 1, r.stderr
    assert "banned style pattern" in r.stderr
    assert "—" in r.stderr
    assert "excited to apply" in r.stderr
    # the "It's not X, it's Y" structure is caught by regex, not substring
    assert "banned style regex" in r.stderr


def test_good_cover_passes_style_gate():
    r = run(
        "validate.py",
        "--cover", os.path.join(FIX, "cover_good.md"),
        "--variant", os.path.join(FIX, "variant_good.yaml"),
        "--bank", os.path.join(FIX, "evidence-bank.md"),
        "--config", NO_CONFIG,
    )
    assert r.returncode == 0, r.stderr


def test_resume_em_dash_fails(tmp_path):
    src = open(os.path.join(FIX, "variant_good.yaml"), encoding="utf-8").read()
    bad = src.replace(
        "Platform engineer who makes the paved road other teams ship on.",
        "Platform engineer — the paved road other teams ship on.",
    )
    assert bad != src
    variant = tmp_path / "variant_bad_style.yaml"
    variant.write_text(bad, encoding="utf-8")
    r = run(
        "validate.py", str(variant),
        "--bank", os.path.join(FIX, "evidence-bank.md"),
        "--resume", os.path.join(FIX, "resume.yaml"),
        "--config", NO_CONFIG,
    )
    assert r.returncode == 1, r.stderr
    assert "banned style pattern" in r.stderr


# ── render.py markdown mode (PRD §14) ──────────────────────────────────────


def test_render_markdown(tmp_path):
    out = tmp_path / "resume.md"
    r = run("render.py", os.path.join(FIX, "variant_good.yaml"), "-o", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Pat Doe")
    assert "## Experience" in text
    assert "**Staff Engineer**, Example Co" in text
    assert "ev:" not in text  # evidence IDs are internal, never printed


def test_render_markdown_missing_ev_fails(tmp_path):
    out = tmp_path / "resume.md"
    r = run("render.py", os.path.join(FIX, "variant_missing_ev.yaml"), "-o", str(out))
    assert r.returncode != 0
    assert not out.exists()


# ── fetch.py dry-run ───────────────────────────────────────────────────────


def test_fetch_dry_run_no_targets(tmp_path):
    # With no targets.yaml the dry run must still exit 0 (nothing to do).
    r = run("fetch.py", "--dry-run", "--root", str(tmp_path))
    assert r.returncode == 0, r.stderr


def test_location_filter_matching():
    sys.path.insert(0, os.path.join(BIN, "lib"))
    from locations import location_matches

    patterns = [
        "sydney", "australia", r"\bau\b", r"\baus\b", r"\bnsw\b",
        "melbourne", "brisbane", "perth", "adelaide", "canberra",
    ]
    for loc in (
        "Sydney, New South Wales, Australia",
        "AU - Sydney",
        "AU: Sydney (45 Clarence St)",
        "Melbourne, au",
        "Melbourne",  # some boards report a bare city, no country token
        "Remote - AUS",
        "",  # unknown location goes to triage, not the bin
    ):
        assert location_matches(loc, patterns), loc
    for loc in ("Austin, Texas", "London, UK", "US Remote", "Auckland, NZ"):
        assert not location_matches(loc, patterns), loc
    # No filter configured -> keep everything.
    assert location_matches("London, UK", [])


def test_freshness_filter():
    sys.path.insert(0, os.path.join(BIN, "lib"))
    from datetime import datetime, timezone

    from freshness import is_fresh, parse_updated_at

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


# ── tracker.py determinism (Phase 7 invariant) ─────────────────────────────


def test_tracker_regeneration_identical(tmp_path):
    applied = tmp_path / "applied" / "2026-07-17_example_staff-eng"
    applied.mkdir(parents=True)
    (applied / "meta.yaml").write_text(
        "company: Example Co\n"
        "title: Staff Engineer\n"
        "date: 2026-07-17\n"
        "applied: 2026-07-17\n"
        "status: applied\n"
        "url: https://example.com/job\n"
    )
    out = tmp_path / "tracker.csv"
    r1 = run("tracker.py", "--root", str(tmp_path), "-o", str(out), "--today", "2026-07-20")
    assert r1.returncode == 0, r1.stderr
    first = out.read_bytes()
    out.unlink()
    r2 = run("tracker.py", "--root", str(tmp_path), "-o", str(out), "--today", "2026-07-20")
    assert r2.returncode == 0, r2.stderr
    assert out.read_bytes() == first


def test_tracker_auto_ghost(tmp_path):
    applied = tmp_path / "applied" / "2026-01-01_old_role"
    applied.mkdir(parents=True)
    (applied / "meta.yaml").write_text(
        "company: Old Co\ntitle: Engineer\ndate: 2026-01-01\napplied: 2026-01-01\nstatus: applied\n"
    )
    out = tmp_path / "tracker.csv"
    run("tracker.py", "--root", str(tmp_path), "-o", str(out), "--today", "2026-03-01")
    assert "ghosted" in out.read_text()
