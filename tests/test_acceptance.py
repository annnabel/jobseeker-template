"""Acceptance tests for the interactive pipeline (validate, render, tracker, angles).

  * validate.py passes a good fixture and fails one with a missing ev
  * validate.py --cover fails a letter containing a number absent from its variant
  * the style gate fails em dashes and stock AI phrasing (resume and cover)
  * render.py emits a markdown resume and still enforces the ev floor
  * tracker.py regeneration is byte-identical

Sweep-only tests live in optional/sweep/tests/.
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


# ── angles: the bank's positioning stances (PRD §21) ───────────────────────

BANK = os.path.join(FIX, "evidence-bank.md")


ENTRY = (
    "### {ev} — {title}\nrole:       Staff Engineer, Example Co\n"
    "dates:      2021-03 → 2023-08\nconfidence: {confidence}\n{extra}"
    "tags:       {tags}\nangles:     {angles}\n\n"
)


def entry(ev, title="An entry", confidence="qualitative", tags="a-skill", angles="", extra=""):
    return ENTRY.format(
        ev=ev, title=title, confidence=confidence, tags=tags, angles=angles, extra=extra
    )


def write_bank(
    tmp_path,
    angles: str,
    entry_angles: str = "platform-leader",
    entries: str | None = None,
    shortfalls: str = "## Shortfalls\n- Something a target role asks for.\n",
) -> str:
    path = tmp_path / "bank.md"
    if entries is None:
        entries = entry("ev:0001", "First", angles=entry_angles) + entry(
            "ev:0002", "Second", angles=entry_angles
        )
    path.write_text(
        f"# Bank\n\n## Angles\n\n{angles}\n\n## Evidence\n\n{entries}\n{shortfalls}",
        encoding="utf-8",
    )
    return str(path)


def test_lint_bank_passes_a_well_formed_bank():
    r = run("validate.py", "--lint-bank", "--bank", BANK)
    assert r.returncode == 0, r.stderr
    assert "angles hold" in r.stderr


def test_lint_bank_catches_an_angle_no_entry_declares(tmp_path):
    bank = write_bank(
        tmp_path,
        "### angle: platform-leader\nclaim:  Builds the paved road.\nproof:  ev:0001, ev:0002\n",
        entry_angles="ghost-angle",
    )
    r = run("validate.py", "--lint-bank", "--bank", bank)
    assert r.returncode != 0
    assert "ghost-angle" in r.stderr


def test_lint_bank_catches_an_angle_nothing_proves(tmp_path):
    bank = write_bank(
        tmp_path,
        "### angle: thin-angle\nclaim:  A claim with one entry behind it.\nproof:  ev:0001\n",
        entry_angles="",
    )
    r = run("validate.py", "--lint-bank", "--bank", bank)
    assert r.returncode != 0
    assert "slogan" in r.stderr


def test_lint_bank_catches_a_claimless_angle(tmp_path):
    bank = write_bank(tmp_path, "### angle: platform-leader\nproof:  ev:0001, ev:0002\n")
    r = run("validate.py", "--lint-bank", "--bank", bank)
    assert r.returncode != 0
    assert "no claim line" in r.stderr


def test_legacy_bullet_angles_still_parse(tmp_path):
    # A bank written before the block format keeps working (PRD §21).
    bank = write_bank(tmp_path, "- `platform-leader` — builds the paved road.")
    r = run("validate.py", "--lint-bank", "--bank", bank)
    assert r.returncode == 0, r.stderr


# ── lint-bank: the entries themselves ─────────────────────────────────────

ONE_ANGLE = "### angle: platform-leader\nclaim:  Builds the paved road.\nproof:  ev:0001, ev:0002\n"


def lint(bank, *args):
    return run("validate.py", "--lint-bank", "--bank", bank, *args)


def test_lint_bank_catches_a_bad_confidence_value(tmp_path):
    bank = write_bank(
        tmp_path, ONE_ANGLE,
        entries=entry("ev:0001", confidence="solid") + entry("ev:0002"),
    )
    r = lint(bank)
    assert r.returncode != 0
    assert "confidence is 'solid'" in r.stderr


def test_lint_bank_catches_a_measured_entry_with_no_source(tmp_path):
    bank = write_bank(
        tmp_path, ONE_ANGLE,
        entries=entry("ev:0001", confidence="measured", extra="source:     n/a\n")
        + entry("ev:0002"),
    )
    r = lint(bank)
    assert r.returncode != 0
    assert "`measured` with no `source:`" in r.stderr
    bank = write_bank(
        tmp_path, ONE_ANGLE,
        entries=entry("ev:0001", confidence="measured", extra="source:     Q3 review deck\n")
        + entry("ev:0002"),
    )
    assert lint(bank).returncode == 0


def test_lint_bank_catches_untagged_and_duplicate_entries(tmp_path):
    bank = write_bank(
        tmp_path, ONE_ANGLE,
        entries=entry("ev:0001", tags="") + entry("ev:0002") + entry("ev:0002"),
    )
    r = lint(bank)
    assert r.returncode != 0
    assert "ev:0001 has no `tags:`" in r.stderr
    assert "ev:0002 appears 2 times" in r.stderr


def test_lint_bank_checks_roles_against_resume_yaml(tmp_path):
    bank = write_bank(tmp_path, ONE_ANGLE)
    ok = lint(bank, "--resume", os.path.join(FIX, "resume.yaml"))
    assert ok.returncode == 0, ok.stderr
    other = tmp_path / "resume.yaml"
    other.write_text("employers:\n  - company: Other Ltd\n    title: X\n    dates: '2020'\n")
    r = lint(bank, "--resume", str(other))
    assert r.returncode != 0
    assert "names no employer or institution from resume.yaml" in r.stderr
    # An institution counts as canonical too.
    edu = tmp_path / "resume-edu.yaml"
    edu.write_text(
        "employers: []\neducation:\n  - institution: Example Co\n"
        "    qualification: Diploma\n    dates: '2019'\n"
    )
    assert lint(bank, "--resume", str(edu)).returncode == 0


def test_lint_bank_wants_a_shortfalls_block_unless_entries_only(tmp_path):
    bank = write_bank(tmp_path, ONE_ANGLE, shortfalls="## Shortfalls\n")
    r = lint(bank)
    assert r.returncode != 0
    assert "Shortfalls" in r.stderr
    assert lint(bank, "--entries-only").returncode == 0


def test_entries_only_skips_angles_but_not_entries(tmp_path):
    # Mid-interview: no angles yet, and nothing cites one. That is fine.
    bank = write_bank(tmp_path, "", entry_angles="", shortfalls="")
    assert lint(bank).returncode != 0
    r = lint(bank, "--entries-only")
    assert r.returncode == 0, r.stderr
    assert "entries well-formed" in r.stderr
    # A malformed entry still fails in that mode.
    bank = write_bank(
        tmp_path, "", shortfalls="",
        entries=entry("ev:0001", angles="", extra="").replace("dates:      2021-03 → 2023-08\n", ""),
    )
    r = lint(bank, "--entries-only")
    assert r.returncode != 0
    assert "no `dates:`" in r.stderr


def test_empty_bank_fails_lint(tmp_path):
    bank = tmp_path / "bank.md"
    bank.write_text("# Bank\n", encoding="utf-8")
    r = lint(str(bank), "--entries-only")
    assert r.returncode != 0
    assert "no `### ev:NNNN` entries" in r.stderr


# ── resume.yaml: education rows are canonical facts too ───────────────────


def test_an_education_entry_must_match_resume_yaml(tmp_path):
    resume = tmp_path / "resume.yaml"
    resume.write_text(
        "name: Pat Doe\nemployers:\n  - company: Example Co\n    title: Staff Engineer\n"
        "    dates: \"2021-03 → 2023-08\"\neducation:\n  - institution: Example University\n"
        "    qualification: BSc Computing\n    dates: \"2014-09 → 2017-06\"\n",
        encoding="utf-8",
    )
    variant = tmp_path / "variant.yaml"
    body = (
        "angle: platform-leader\nsections:\n  - heading: Education\n    entries:\n"
        "      - company: Example University\n        title: {title}\n"
        "        dates: \"2014-09 → 2017-06\"\n        bullets:\n"
        "          - text: \"Rebuilt the CI pipeline as a project.\"\n            ev: ev:0031\n"
    )
    variant.write_text(body.format(title="BSc Computing"), encoding="utf-8")
    r = run("validate.py", str(variant), "--bank", BANK, "--resume", str(resume))
    assert r.returncode == 0, r.stderr
    variant.write_text(body.format(title="MSc Computing"), encoding="utf-8")
    r = run("validate.py", str(variant), "--bank", BANK, "--resume", str(resume))
    assert r.returncode != 0
    assert "diverges from canonical resume.yaml" in r.stderr


def test_variant_positioned_on_an_undeclared_angle_fails(tmp_path):
    variant = tmp_path / "variant.yaml"
    variant.write_text(
        "angle: invented-angle\nsections:\n  - heading: Summary\n"
        "    bullets:\n      - text: \"Ran the platform.\"\n        ev: ev:0031\n",
        encoding="utf-8",
    )
    r = run("validate.py", str(variant), "--bank", BANK, "--resume", os.path.join(FIX, "resume.yaml"))
    assert r.returncode != 0
    assert "invented-angle" in r.stderr


def test_variant_may_still_declare_its_angle_under_the_old_label_key():
    # variant_good.yaml carries `label: platform-leader`, the original spelling.
    r = run(
        "validate.py",
        os.path.join(FIX, "variant_good.yaml"),
        "--bank", BANK,
        "--resume", os.path.join(FIX, "resume.yaml"),
    )
    assert r.returncode == 0, r.stderr


# ── render.py contact links (list-valued fields) ───────────────────────────


def test_render_flattens_contact_links(tmp_path):
    variant = tmp_path / "variant.yaml"
    variant.write_text(
        "name: Pat Doe\n"
        "contact:\n"
        "  email: pat@example.com\n"
        "  links:\n"
        "    - github.com/pat\n"
        "    - linkedin.com/in/pat\n"
        "sections:\n"
        "  - heading: Summary\n"
        "    bullets:\n"
        "      - text: Builds reliable systems.\n"
        "        ev: ev:0001\n",
        encoding="utf-8",
    )
    out = tmp_path / "resume.md"
    r = run("render.py", str(variant), "-o", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text(encoding="utf-8")
    # Each link appears as its own entry, never as a Python list repr.
    assert "github.com/pat" in text
    assert "linkedin.com/in/pat" in text
    assert "['" not in text and "']" not in text


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


def test_tracker_followup_nudge(tmp_path):
    # Applied, silent past followup_days but under ghost_days -> the row's
    # next_action nudges the human to follow up. Nothing is sent by anything.
    applied = tmp_path / "applied" / "2026-07-01_example_role"
    applied.mkdir(parents=True)
    (applied / "meta.yaml").write_text(
        "company: Example Co\ntitle: Engineer\ndate: 2026-07-01\n"
        "applied: 2026-07-01\nstatus: applied\n"
    )
    out = tmp_path / "tracker.csv"
    run("tracker.py", "--root", str(tmp_path), "-o", str(out), "--today", "2026-07-10")
    text = out.read_text()
    assert "send a follow-up" in text
    assert "ghosted" not in text
    # Before followup_days it still just waits.
    run("tracker.py", "--root", str(tmp_path), "-o", str(out), "--today", "2026-07-03")
    assert "send a follow-up" not in out.read_text()


def test_tracker_stats(tmp_path):
    # --stats derives the funnel from the same meta.yaml files and writes
    # nothing. Rates are computed, never estimated.
    for slug, status, track in (
        ("a_co", "reply", "track-one"),
        ("b_co", "applied", "track-one"),
        ("c_co", "ghosted", "track-two"),
    ):
        d = tmp_path / "applied" / f"2026-07-01_{slug}"
        d.mkdir(parents=True)
        (d / "meta.yaml").write_text(
            f"company: {slug}\ntitle: Role\ndate: 2026-07-01\napplied: 2026-07-01\n"
            f"status: {status}\ntrack: {track}\n"
        )
    r = run("tracker.py", "--root", str(tmp_path), "--stats", "--today", "2026-07-05")
    assert r.returncode == 0, r.stderr
    assert "applications   3" in r.stdout
    assert "callbacks      1/3 (33%)" in r.stdout
    assert "track-one" in r.stdout and "track-two" in r.stdout
    assert not (tmp_path / "tracker.csv").exists()  # --stats writes nothing


def test_tracker_auto_ghost(tmp_path):
    applied = tmp_path / "applied" / "2026-01-01_old_role"
    applied.mkdir(parents=True)
    (applied / "meta.yaml").write_text(
        "company: Old Co\ntitle: Engineer\ndate: 2026-01-01\napplied: 2026-01-01\nstatus: applied\n"
    )
    out = tmp_path / "tracker.csv"
    run("tracker.py", "--root", str(tmp_path), "-o", str(out), "--today", "2026-03-01")
    assert "ghosted" in out.read_text()


# ── skills alias ───────────────────────────────────────────────────────────


def test_skills_key_is_a_synonym_for_technologies(tmp_path):
    # A nurse's variant lists clinical competencies, not technologies. Both key
    # names must validate and render identically.
    import yaml

    src = yaml.safe_load(open(os.path.join(FIX, "variant_good.yaml"), encoding="utf-8"))
    assert src.get("technologies"), "fixture should exercise the legacy key"
    src["skills"] = src.pop("technologies")
    variant = tmp_path / "variant_skills_key.yaml"
    variant.write_text(yaml.safe_dump(src, sort_keys=False), encoding="utf-8")

    r = run(
        "validate.py", str(variant),
        "--bank", os.path.join(FIX, "evidence-bank.md"),
        "--resume", os.path.join(FIX, "resume.yaml"),
        "--config", NO_CONFIG,
    )
    assert r.returncode == 0, r.stderr

    out = tmp_path / "resume.md"
    r = run("render.py", str(variant), "-o", str(out))
    assert r.returncode == 0, r.stderr
    assert "## Skills" in out.read_text(encoding="utf-8")


def test_unbacked_skill_still_fails(tmp_path):
    # The provenance gate must not weaken under the new key name.
    import yaml

    src = yaml.safe_load(open(os.path.join(FIX, "variant_good.yaml"), encoding="utf-8"))
    src.pop("technologies", None)
    src["skills"] = ["Underwater Basket Weaving"]
    variant = tmp_path / "variant_bad_skill.yaml"
    variant.write_text(yaml.safe_dump(src, sort_keys=False), encoding="utf-8")

    r = run(
        "validate.py", str(variant),
        "--bank", os.path.join(FIX, "evidence-bank.md"),
        "--resume", os.path.join(FIX, "resume.yaml"),
        "--config", NO_CONFIG,
    )
    assert r.returncode == 1, r.stderr
    assert "Underwater Basket Weaving" in r.stderr


# ── template hygiene (PRD §19.2) ───────────────────────────────────────────


def test_template_carries_no_personal_data():
    r = run("check_template_clean.py", "--root", ROOT)
    assert r.returncode == 0, r.stderr


def test_template_guard_catches_personal_data(tmp_path):
    (tmp_path / "profile").mkdir()
    (tmp_path / "profile" / "evidence-bank.md").write_text("### ev:0001\n", encoding="utf-8")
    r = run("check_template_clean.py", "--root", str(tmp_path))
    assert r.returncode == 1, r.stderr
    assert "evidence-bank.md" in r.stderr


# ── skills layout, headline, prose summary (PRD §25) ──────────────────────

GROUPED = os.path.join(FIX, "variant_grouped.yaml")


def validate_variant(path):
    return run(
        "validate.py", str(path),
        "--bank", BANK,
        "--resume", os.path.join(FIX, "resume.yaml"),
        "--config", NO_CONFIG,
    )


def test_grouped_skills_validate_and_render_one_category_per_line(tmp_path):
    assert validate_variant(GROUPED).returncode == 0
    out = tmp_path / "resume.md"
    r = run("render.py", GROUPED, "-o", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text(encoding="utf-8")
    # Each category is its own line, not one long comma-joined list.
    assert "**Delivery Pipelines:** CI-CD, GitHub Actions, BuildKit" in text
    assert "**Infrastructure:** Docker, Terraform, AWS" in text
    assert "**Operations:** Incident Response, On-Call" in text
    block = text.split("## Skills\n\n")[1].split("\n\n")[0].splitlines()
    # Consecutive lines, hard-broken (two trailing spaces) except the last.
    assert block == [
        "**Delivery Pipelines:** CI-CD, GitHub Actions, BuildKit  ",
        "**Infrastructure:** Docker, Terraform, AWS  ",
        "**Operations:** Incident Response, On-Call",
    ]


def test_skills_render_after_the_summary_not_after_the_last_job(tmp_path):
    out = tmp_path / "resume.md"
    run("render.py", GROUPED, "-o", str(out))
    text = out.read_text(encoding="utf-8")
    assert text.index("## Summary") < text.index("## Skills") < text.index("## Experience")


def test_skills_stay_last_when_the_variant_opens_with_experience(tmp_path):
    variant = tmp_path / "variant.yaml"
    variant.write_text(
        "name: Pat Doe\nskills: [docker]\nsections:\n  - heading: Experience\n"
        "    entries:\n      - company: Example Co\n        title: Staff Engineer\n"
        "        dates: \"2021-03 → 2023-08\"\n        bullets:\n"
        "          - text: Ran the platform.\n            ev: ev:0031\n",
        encoding="utf-8",
    )
    out = tmp_path / "resume.md"
    r = run("render.py", str(variant), "-o", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text(encoding="utf-8")
    assert text.index("## Experience") < text.index("## Skills")


def test_grouped_skills_are_gated_item_by_item(tmp_path):
    import yaml

    src = yaml.safe_load(open(GROUPED, encoding="utf-8"))
    src["skills"][0]["items"].append("Underwater Basket Weaving")
    variant = tmp_path / "variant.yaml"
    variant.write_text(yaml.safe_dump(src, sort_keys=False, allow_unicode=True), encoding="utf-8")
    r = validate_variant(variant)
    assert r.returncode == 1, r.stderr
    assert "Underwater Basket Weaving" in r.stderr
    # The category heading is layout, not a claim: it is never reported.
    assert "Delivery Pipelines" not in r.stderr


def test_a_category_with_no_items_or_no_name_fails(tmp_path):
    import yaml

    src = yaml.safe_load(open(GROUPED, encoding="utf-8"))
    src["skills"].append({"category": "Empty", "items": []})
    src["skills"].append({"items": ["docker"]})
    variant = tmp_path / "variant.yaml"
    variant.write_text(yaml.safe_dump(src, sort_keys=False, allow_unicode=True), encoding="utf-8")
    r = validate_variant(variant)
    assert r.returncode == 1, r.stderr
    assert "lists no items" in r.stderr
    assert "no category name" in r.stderr


def test_mixing_grouped_and_bare_skills_fails(tmp_path):
    import yaml

    src = yaml.safe_load(open(GROUPED, encoding="utf-8"))
    src["skills"].append("docker")
    variant = tmp_path / "variant.yaml"
    variant.write_text(yaml.safe_dump(src, sort_keys=False, allow_unicode=True), encoding="utf-8")
    r = validate_variant(variant)
    assert r.returncode == 1, r.stderr
    assert "mix grouped and ungrouped" in r.stderr


def test_a_skill_matches_its_tag_however_it_is_punctuated(tmp_path):
    # The bank tags `github-actions` and `ci-cd`; the resume prints them the
    # way the product and the posting spell them. Same word, same claim.
    variant = tmp_path / "variant.yaml"
    variant.write_text(
        "name: Pat Doe\nskills: [GitHub Actions, CI/CD, incident_response]\n"
        "sections:\n  - heading: Summary\n    bullets:\n"
        "      - text: Ran the platform.\n        ev: ev:0031\n",
        encoding="utf-8",
    )
    assert validate_variant(variant).returncode == 0
    # A synonym is still a claim the bank has to make itself.
    variant.write_text(
        "name: Pat Doe\nskills: [k8s]\nsections:\n  - heading: Summary\n    bullets:\n"
        "      - text: Ran the platform.\n        ev: ev:0031\n",
        encoding="utf-8",
    )
    r = validate_variant(variant)
    assert r.returncode == 1 and "k8s" in r.stderr


def test_cover_skill_check_tolerates_punctuation_both_ways(tmp_path):
    # A cover saying "GitHub Actions" is backed by a variant printing it that
    # way, even though the bank's tag is hyphenated.
    cover = tmp_path / "cover.md"
    cover.write_text("I run GitHub Actions for a living.\n", encoding="utf-8")
    r = run(
        "validate.py", "--cover", str(cover), "--variant", GROUPED,
        "--bank", BANK, "--config", NO_CONFIG,
    )
    assert r.returncode == 0, r.stderr
    # ...and a skill the variant never carries is still caught in the cover.
    cover.write_text("I run Buildkit and Terraform and Kubernetes clusters.\n", encoding="utf-8")
    src = open(GROUPED, encoding="utf-8").read().replace("BuildKit", "Docker")
    variant = tmp_path / "variant.yaml"
    variant.write_text(src, encoding="utf-8")
    r = run(
        "validate.py", "--cover", str(cover), "--variant", str(variant),
        "--bank", BANK, "--config", NO_CONFIG,
    )
    assert r.returncode == 1, r.stderr
    assert "buildkit" in r.stderr


def test_headline_renders_under_the_name(tmp_path):
    out = tmp_path / "resume.md"
    run("render.py", GROUPED, "-o", str(out))
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Pat Doe\n\n**Platform Engineer**\n")


def test_headline_may_carry_no_numeral_and_no_banned_style(tmp_path):
    src = open(GROUPED, encoding="utf-8").read()
    variant = tmp_path / "variant.yaml"
    variant.write_text(
        src.replace("headline: Platform Engineer", "headline: Platform Engineer, 10 years"),
        encoding="utf-8",
    )
    r = validate_variant(variant)
    assert r.returncode == 1, r.stderr
    assert "headline asserts a numeral" in r.stderr
    variant.write_text(
        src.replace("headline: Platform Engineer", "headline: Platform Engineer — paved roads"),
        encoding="utf-8",
    )
    r = validate_variant(variant)
    assert r.returncode == 1, r.stderr
    assert "[headline] banned style pattern" in r.stderr


def test_a_paragraph_section_renders_as_prose(tmp_path):
    out = tmp_path / "resume.md"
    run("render.py", GROUPED, "-o", str(out))
    summary = out.read_text(encoding="utf-8").split("## Summary")[1].split("## Skills")[0]
    assert "- " not in summary
    assert (
        "Platform engineer who makes the paved road other teams ship on. "
        "Rebuilt the on-call rotation" in summary
    )


def test_a_paragraph_section_still_needs_evidence_ids(tmp_path):
    src = open(GROUPED, encoding="utf-8").read().replace("        ev: ev:0033\n", "", 1)
    variant = tmp_path / "variant.yaml"
    variant.write_text(src, encoding="utf-8")
    out = tmp_path / "resume.md"
    r = run("render.py", str(variant), "-o", str(out))
    assert r.returncode != 0
    assert not out.exists()


def test_grouped_skills_render_to_typst(tmp_path):
    r = run("render.py", GROUPED, "-o", "unused.pdf", "--dump-typst")
    assert r.returncode == 0, r.stderr
    assert "*Delivery Pipelines:* CI-CD, GitHub Actions, BuildKit" in r.stdout
    assert r.stdout.index("== Summary") < r.stdout.index("== Skills") < r.stdout.index("== Experience")
    assert "#text(size: 12pt)[Platform Engineer]" in r.stdout


def test_grouped_skills_are_scored_by_item():
    sys.path.insert(0, BIN)
    import yaml

    from ats_score import load_ats_config, score

    jd = open(os.path.join(FIX, "jd_sample.md"), encoding="utf-8").read()
    variant = yaml.safe_load(open(GROUPED, encoding="utf-8"))
    rows = {r["keyword"]: r for r in score(jd, variant, None, load_ats_config(None))["keywords"]}
    assert rows["ci/cd"]["in_resume"]
    assert rows["incident response"]["in_resume"]


# ── save.py: the one git call, with the template guard ────────────────────


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def make_repo(tmp_path, remote_name):
    """A working copy whose origin is a bare repo named `remote_name`."""
    bare = tmp_path / f"{remote_name}.git"
    git("init", "-q", "--bare", "-b", "main", str(bare), cwd=tmp_path)
    work = tmp_path / "work"
    git("clone", "-q", str(bare), str(work), cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=work)
    git("config", "user.name", "T", cwd=work)
    git("checkout", "-q", "-b", "main", cwd=work)
    (work / "README.md").write_text("seed\n", encoding="utf-8")
    git("add", "-A", cwd=work)
    git("commit", "-q", "-m", "seed", cwd=work)
    git("push", "-q", "-u", "origin", "main", cwd=work)
    return work, bare


def test_save_guard_refuses_the_shared_template(tmp_path):
    work, _bare = make_repo(tmp_path, "jobseeker-template")
    r = run("save.py", "--guard", "--cwd", str(work))
    assert r.returncode == 2
    assert "Use this template" in r.stderr
    (work / "profile").mkdir()
    (work / "profile" / "goals.yaml").write_text("tracks: []\n", encoding="utf-8")
    r = run("save.py", "setup: goals", "--cwd", str(work))
    assert r.returncode == 2
    # Nothing was committed.
    assert git("status", "--porcelain", cwd=work).stdout.strip() != ""
    assert "goals" not in git("log", "--oneline", cwd=work).stdout


def test_save_commits_and_pushes_a_private_copy(tmp_path):
    work, bare = make_repo(tmp_path, "my-jobseeker")
    assert run("save.py", "--guard", "--cwd", str(work)).returncode == 0
    (work / "profile").mkdir()
    (work / "profile" / "goals.yaml").write_text("tracks: []\n", encoding="utf-8")
    r = run("save.py", "setup: goals", "--cwd", str(work))
    assert r.returncode == 0, r.stderr
    assert "setup: goals" in git("log", "--oneline", "origin/main", cwd=work).stdout
    # Nothing new: a clean exit, no empty commit.
    r = run("save.py", "setup: goals again", "--cwd", str(work))
    assert r.returncode == 0
    assert "nothing to save" in r.stderr
    assert "again" not in git("log", "--oneline", cwd=work).stdout


def test_save_rebases_onto_a_moved_remote(tmp_path):
    work, bare = make_repo(tmp_path, "my-jobseeker")
    other = tmp_path / "other"
    git("clone", "-q", str(bare), str(other), cwd=tmp_path)
    git("config", "user.email", "o@example.com", cwd=other)
    git("config", "user.name", "O", cwd=other)
    (other / "elsewhere.md").write_text("from another session\n", encoding="utf-8")
    git("add", "-A", cwd=other)
    git("commit", "-q", "-m", "elsewhere", cwd=other)
    git("push", "-q", "origin", "main", cwd=other)

    (work / "local.md").write_text("from this session\n", encoding="utf-8")
    r = run("save.py", "setup: local", "--cwd", str(work))
    assert r.returncode == 0, r.stderr
    log = git("log", "--oneline", "origin/main", cwd=work).stdout
    assert "setup: local" in log and "elsewhere" in log
