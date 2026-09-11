#!/usr/bin/env python3
"""validate.py — the provenance gate. PRD §8.3, principle 3.4, red lines §10.

    validate.py <variant.yaml> [--bank profile/evidence-bank.md] [--resume profile/resume.yaml]
    validate.py --cover <cover.md> --variant <variant.yaml> [--bank ...] [--note ...]
    validate.py --lint-bank [--entries-only] [--bank ...] [--resume ...]

Deterministic. Regex-able. No model in the gate. Exits non-zero on any
violation, printing every violation found (not just the first).

This catches invention: a bullet with no evidence ID, a metric that traces to
an estimate, a technology with no backing. It does NOT catch *stretching* — a
bullet that cites ev:0031 but overstates what ev:0031 says. That is the walkthrough's
job. See PRD §1/G6. Do not trust the green check to mean more than it does.

It also enforces the style gate (PRD §14): banned substrings — em dashes and
stock AI phrasing — fail resume bullets and covers. The list lives in
`profile/config.yaml` under `style.banned`; without a config the built-in
defaults apply. Deterministic, like everything else here.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

# Make lib/ importable whether run from repo root or elsewhere.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "lib"))

import yaml  # noqa: E402

from variant import flat_text, skill_groups, skills as variant_skills  # noqa: E402

# ── evidence bank parsing ──────────────────────────────────────────────────

EV_HEADER = re.compile(r"^###\s+(ev:\d+)\b", re.MULTILINE)
FIELD = re.compile(r"^([a-z_]+):\s*(.*)$")


def parse_bank(path: str) -> dict[str, dict]:
    """Parse evidence-bank.md into {ev_id: {confidence, tags, metric, ...}}.

    Entries are `### ev:NNNN` headers followed by `field: value` lines up to
    the next header. Free-form narrative blocks are ignored for gating.
    """
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    entries: dict[str, dict] = {}
    headers = list(EV_HEADER.finditer(text))
    for i, m in enumerate(headers):
        ev_id = m.group(1)
        if ev_id in entries:
            entries[ev_id].setdefault("duplicates", 0)
            entries[ev_id]["duplicates"] += 1
            continue
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[start:end]
        fields: dict[str, str] = {}
        for line in block.splitlines():
            fm = FIELD.match(line.strip())
            if fm:
                fields[fm.group(1)] = fm.group(2).strip()
        tags = [t.strip().lower() for t in fields.get("tags", "").split(",") if t.strip()]
        entries[ev_id] = {
            "confidence": fields.get("confidence", "").strip().lower(),
            "tags": tags,
            "raw": fields,
        }
    return entries


SEPARATORS = re.compile(r"[\s_/-]+")


def norm_tag(text: str) -> str:
    """One spelling for one skill: lowercase, separators folded to a hyphen.

    The bank tags `github-actions`; the resume prints `GitHub Actions`; a
    posting says `CI/CD` where the bank says `ci-cd`. Same word, different
    punctuation — the gate matches the word. It does not fold anything else,
    so `kubernetes` still does not match `k8s`: a synonym is a claim the bank
    has to make itself.
    """
    return SEPARATORS.sub("-", str(text).strip().lower()).strip("-")


def bank_tags(entries: dict[str, dict]) -> set[str]:
    tags: set[str] = set()
    for e in entries.values():
        tags.update(norm_tag(t) for t in e["tags"])
    return tags


def entry_angles(entries: dict[str, dict]) -> dict[str, list[str]]:
    """{ev_id: [angle slug, ...]} from each entry's `angles:` field."""
    out: dict[str, list[str]] = {}
    for ev, e in entries.items():
        raw = e["raw"].get("angles", "")
        out[ev] = [a.strip().lower() for a in raw.split(",") if a.strip()]
    return out


# ── angle parsing (PRD §21) ────────────────────────────────────────────────

ANGLE_HEADER = re.compile(
    r"^###\s+angle:\s*([a-z0-9][a-z0-9-]*)\s*$", re.MULTILINE | re.IGNORECASE
)
LEGACY_ANGLE = re.compile(
    r"^[-*]\s+`([a-z0-9][a-z0-9-]*)`\s*[—-]\s*(.+)$", re.MULTILINE | re.IGNORECASE
)
EV_REF = re.compile(r"ev:\d+")


def parse_angles(path: str) -> dict[str, dict]:
    r"""Parse the bank's `## Angles` block into {slug: {claim, proof, serves}}.

    An angle is a positioning stance: one claim, proved by evidence, aimed at a
    track (PRD §21). The current shape is a block per angle —

        ### angle: the-slug
        claim:  one line, in the candidate's own words
        proof:  ev:0031, ev:0044
        serves: <track ids from goals.yaml>

    — and the original one-bullet shape (`- \`slug\` — claim`) still parses, so
    a bank written before §21 keeps working. A legacy angle carries no proof,
    which `--lint-bank` reports: an angle nothing proves is a slogan.
    """
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    angles: dict[str, dict] = {}
    headers = list(ANGLE_HEADER.finditer(text))
    for i, m in enumerate(headers):
        slug = m.group(1).lower()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[m.end() : end]
        # Stop at the next top-level section, so `## Evidence` is not read in.
        block = re.split(r"^##\s", block, maxsplit=1, flags=re.MULTILINE)[0]
        fields: dict[str, str] = {}
        for line in block.splitlines():
            fm = FIELD.match(line.strip())
            if fm:
                fields[fm.group(1)] = fm.group(2).strip()
        angles[slug] = {
            "claim": fields.get("claim", "").strip(),
            "proof": EV_REF.findall(fields.get("proof", "")),
            "serves": [s.strip() for s in fields.get("serves", "").split(",") if s.strip()],
            "legacy": False,
        }

    for m in LEGACY_ANGLE.finditer(text):
        slug = m.group(1).lower()
        angles.setdefault(
            slug, {"claim": m.group(2).strip(), "proof": [], "serves": [], "legacy": True}
        )
    return angles


def variant_angle(variant: dict) -> str:
    """The angle a variant declares, under either accepted key.

    `angle:` is the current key; `label:` is what early variants called the
    same thing.
    """
    for key in ("angle", "label"):
        value = variant.get(key)
        if value and str(value).strip():
            return str(value).strip().lower()
    return ""


CONFIDENCE_VALUES = ("measured", "estimated", "qualitative")
NO_SOURCE = {"", "n/a", "na", "none", "-", "tbd", "?"}


def canonical_facts(resume_path: str | None) -> tuple[set[tuple], list[str]]:
    """The (company, title, dates) triples resume.yaml declares, and its company names.

    Education rows count too: a draft prints a degree as an entry with the
    institution as `company` and the qualification as `title`, so those are
    canonical facts the same way an employer is.
    """
    if not resume_path or not os.path.exists(resume_path):
        return set(), []
    with open(resume_path, encoding="utf-8") as fh:
        resume = yaml.safe_load(fh) or {}
    triples: set[tuple] = set()
    companies: list[str] = []
    for e in resume.get("employers", []) or []:
        triples.add((e.get("company"), e.get("title"), str(e.get("dates"))))
        if e.get("company"):
            companies.append(str(e["company"]))
    for e in resume.get("education", []) or []:
        triples.add((e.get("institution"), e.get("qualification"), str(e.get("dates"))))
        if e.get("institution"):
            companies.append(str(e["institution"]))
    return triples, companies


def lint_entries(entries: dict[str, dict], companies: list[str]) -> list[str]:
    """Per-entry checks: the fields the draft gates read must be there and well-formed.

    `/setup` runs this after every batch of entries, so a malformed
    `confidence:` or an entry with no tags is caught while the person who
    knows the answer is still in the conversation, not days later when a
    draft fails. When resume.yaml exists, each `role:` must end in one of its
    employers or institutions, spelled the same way.
    """
    errors: list[str] = []
    lowered = [c.lower() for c in companies]
    for ev, e in entries.items():
        raw = e["raw"]
        if e.get("duplicates"):
            errors.append(f"{ev} appears {e['duplicates'] + 1} times; every ID is unique")
        conf = e["confidence"]
        if conf not in CONFIDENCE_VALUES:
            errors.append(
                f"{ev} confidence is {conf or 'missing'!r}; must be one of "
                f"{', '.join(CONFIDENCE_VALUES)}"
            )
        if conf == "measured" and raw.get("source", "").strip().lower() in NO_SOURCE:
            errors.append(
                f"{ev} is `measured` with no `source:`; a number nobody can point to is "
                f"`estimated`"
            )
        if not e["tags"]:
            errors.append(f"{ev} has no `tags:`; nothing in it can back a skill")
        role = raw.get("role", "").strip()
        if not role:
            errors.append(f"{ev} has no `role:` (Title, Employer)")
        elif lowered and not any(role.lower().endswith(c) for c in lowered):
            errors.append(
                f"{ev} role {role!r} names no employer or institution from resume.yaml; "
                f"spell it the way resume.yaml does"
            )
        if not raw.get("dates", "").strip():
            errors.append(f"{ev} has no `dates:`")
    return errors


def has_shortfalls(bank_path: str) -> bool:
    with open(bank_path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^##\s+Shortfalls\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    return bool(m and m.group(1).strip())


def lint_bank(
    bank_path: str, resume_path: str | None = None, entries_only: bool = False
) -> list[str]:
    """Check the bank holds together: every entry well-formed, every angle proved.

    Deterministic, like everything else in this file, and the same boundary
    applies: it catches an angle that does not exist or that nothing proves,
    and an entry a draft gate could not read. Whether an angle is a *good*
    pitch, or an entry an honest one, is a human judgment.

    `entries_only` is the mid-interview mode: `/setup` runs it after each
    batch of entries, before any angle exists, so a bank with no `## Angles`
    and no `## Shortfalls` yet is not an error there.
    """
    if not os.path.exists(bank_path):
        return [f"evidence bank not found: {bank_path}"]
    entries = parse_bank(bank_path)
    _triples, companies = canonical_facts(resume_path)
    errors: list[str] = lint_entries(entries, companies)
    if not entries:
        errors.append("bank holds no `### ev:NNNN` entries")
    if entries_only:
        return errors

    angles = parse_angles(bank_path)
    if not has_shortfalls(bank_path):
        errors.append(
            "bank has no `## Shortfalls`, or it is empty; every candidate lacks "
            "something a target role asks for"
        )

    if not angles:
        errors.append("bank declares no `## Angles`; every variant is then unpositioned")

    for ev, slugs in entry_angles(entries).items():
        for slug in slugs:
            if slug not in angles:
                errors.append(f"{ev} claims angle {slug!r} which is not declared in `## Angles`")

    for slug, angle in sorted(angles.items()):
        if not angle["claim"]:
            errors.append(f"angle {slug!r} has no claim line")
        for ev in angle["proof"]:
            if ev not in entries:
                errors.append(f"angle {slug!r} cites {ev} which is not in the bank")
        proven_by = [ev for ev, s in entry_angles(entries).items() if slug in s]
        support = set(angle["proof"]) | set(proven_by)
        if len(support) < 2:
            errors.append(
                f"angle {slug!r} rests on {len(support)} evidence entr(y/ies); an angle "
                f"two entries cannot prove is a slogan (add `proof:` or tag more entries)"
            )
    return errors


# ── style gate ─────────────────────────────────────────────────────────────

# Applied when profile/config.yaml has no style.banned list. Case-insensitive
# substring match. "leverag" covers leverage/leveraging; "delve" covers delved;
# "unlock" covers unlocking/unlocked.
DEFAULT_BANNED = [
    "—",
    "I am writing to apply",
    "excited to apply",
    "thrilled",
    "delve",
    "spearhead",
    "leverag",
    "seamless",
    "cutting-edge",
    "fast-paced",
    "proven track record",
    "passionate about",
    "not just",
    "not only",
    "not merely",
    "not simply",
    "tapestry",
    "unlock",
    "paramount",
    "furthermore",
    "moreover",
    "symphony",
    "testament",
    "game-chang",
    "in today's",
    "here's the truth",
    "what nobody tells you",
    "at the end of the day",
    "in conclusion",
]

# Case-insensitive regexes for structures a substring can't catch — chiefly the
# "It's not X, it's Y" negation cliché in its common spellings.
DEFAULT_BANNED_REGEX = [
    r"\bit'?s not [^.!?\n]{1,60}?[,;.] ?it'?s\b",
    r"\bisn'?t [^.!?\n]{1,60}?[,;.] ?it'?s\b",
]


def load_banned(config_path: str | None) -> tuple[list[str], list[str]]:
    """Return (banned substrings, banned regexes) from config, else defaults."""
    banned = list(DEFAULT_BANNED)
    banned_regex = list(DEFAULT_BANNED_REGEX)
    if config_path and os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh) or {}
        style = cfg.get("style") or {}
        if isinstance(style.get("banned"), list) and style["banned"]:
            banned = [str(b) for b in style["banned"]]
        if isinstance(style.get("banned_regex"), list) and style["banned_regex"]:
            banned_regex = [str(b) for b in style["banned_regex"]]
    return banned, banned_regex


def style_errors(
    text: str, banned: list[str], where: str, banned_regex: list[str] | None = None
) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    for pat in banned:
        idx = lowered.find(pat.lower())
        if idx != -1:
            context = text[max(0, idx - 25) : idx + len(pat) + 25].replace("\n", " ").strip()
            errors.append(f"[{where}] banned style pattern {pat!r}: …{context}…")
    for pat in banned_regex or []:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            context = text[max(0, m.start() - 25) : m.end() + 25].replace("\n", " ").strip()
            errors.append(f"[{where}] banned style regex {pat!r}: …{context}…")
    return errors


# ── numeral / metric detection ─────────────────────────────────────────────

NUMERAL = re.compile(r"\d+(?:[.,]\d+)?")
# A hedge makes a number directional rather than a hard claim.
HEDGE = re.compile(
    r"(~|≈|about|around|roughly|approximately|approx\.?|est\.?|estimated|"
    r"nearly|almost|over|under|up to|order of)",
    re.IGNORECASE,
)


def numerals(text: str) -> list[str]:
    """Digit sequences in `text`, normalized (commas stripped)."""
    return [n.replace(",", "") for n in NUMERAL.findall(text)]


def has_hard_metric(text: str) -> bool:
    """True if `text` contains a number NOT softened by a nearby hedge word.

    We check a small window before each numeral for a hedge. This is the
    "measured may appear as a hard metric; estimated may be directional only"
    rule from PRD §8.0.
    """
    for m in NUMERAL.finditer(text):
        window = text[max(0, m.start() - 20) : m.start()]
        if not HEDGE.search(window):
            return True
    return False


# ── variant flattening ─────────────────────────────────────────────────────


def flatten_bullets(variant: dict) -> list[tuple[str, dict]]:
    """Yield (context_label, bullet_dict) for every bullet in the variant.

    A bullet is {text, ev}. Bullets live directly under a section, or under an
    entry within a section.
    """
    out: list[tuple[str, dict]] = []
    for section in variant.get("sections", []) or []:
        heading = section.get("heading", "?")
        for bullet in section.get("bullets", []) or []:
            out.append((heading, bullet))
        for entry in section.get("entries", []) or []:
            label = f"{heading}/{entry.get('company', '?')}"
            for bullet in entry.get("bullets", []) or []:
                out.append((label, bullet))
    return out


def canonical_employers(variant: dict) -> list[dict]:
    out: list[dict] = []
    for section in variant.get("sections", []) or []:
        for entry in section.get("entries", []) or []:
            if "company" in entry and "title" in entry:
                out.append(entry)
    return out


# ── resume mode ────────────────────────────────────────────────────────────


def validate_resume(
    variant_path: str,
    bank_path: str,
    resume_path: str | None,
    banned: list[str] | None = None,
    banned_regex: list[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    banned = banned if banned is not None else list(DEFAULT_BANNED)
    banned_regex = banned_regex if banned_regex is not None else list(DEFAULT_BANNED_REGEX)
    with open(variant_path, encoding="utf-8") as fh:
        variant = yaml.safe_load(fh) or {}

    if not os.path.exists(bank_path):
        return [f"evidence bank not found: {bank_path}"]
    bank = parse_bank(bank_path)
    tags = bank_tags(bank)

    # Every bullet must cite an ev that exists; its metrics must be supported.
    for label, bullet in flatten_bullets(variant):
        text = str(bullet.get("text", "")).strip()
        ev = str(bullet.get("ev", "")).strip()
        snippet = text[:60]
        errors.extend(style_errors(text, banned, label, banned_regex))
        # Resume bullets lead with the action; no "Label: detail" structures
        # (requested 2026-07-18). Covers may still use colons in prose.
        if ": " in text:
            errors.append(
                f"[{label}] bullet uses a colon-led structure; lead with the "
                f"action and weave the detail in: {snippet!r}"
            )
        if not ev:
            errors.append(f"[{label}] bullet has no evidence ID: {snippet!r}")
            continue
        if ev not in bank:
            errors.append(f"[{label}] cites {ev} which is not in the bank: {snippet!r}")
            continue
        confidence = bank[ev]["confidence"]
        nums = numerals(text)
        if confidence == "qualitative" and nums:
            errors.append(
                f"[{label}] {ev} is qualitative but bullet asserts a numeral "
                f"({', '.join(nums)}): {snippet!r}"
            )
        elif confidence == "estimated" and has_hard_metric(text):
            errors.append(
                f"[{label}] {ev} is estimated but bullet states a hard metric "
                f"(use directional phrasing): {snippet!r}"
            )

    # A declared angle must exist in the bank. The angle is what the resume
    # argues; an argument the bank never makes is invention like any other
    # (PRD §21). Silent when the variant declares none, or the bank predates
    # angles entirely.
    angle = variant_angle(variant)
    if angle:
        angles = parse_angles(bank_path)
        if angles and angle not in angles:
            errors.append(
                f"variant is positioned on angle {angle!r} which the bank does not declare "
                f"(declared: {', '.join(sorted(angles)) or 'none'})"
            )

    # The headline is the target, never a held title (PRD §25). It cites no
    # evidence, so it may carry no numeral — there is nothing for one to trace
    # to — and the style gate applies to it as to any other line.
    headline = str(variant.get("headline", "") or "").strip()
    if headline:
        errors.extend(style_errors(headline, banned, "headline", banned_regex))
        nums = numerals(headline)
        if nums:
            errors.append(
                f"headline asserts a numeral ({', '.join(nums)}) which no evidence "
                f"entry can back; keep numbers in bullets that cite an ev: {headline[:60]!r}"
            )

    # A skill in the skills list must be tagged by some evidence entry.
    # Grouped or flat, the items are the claims; a category name is layout.
    for skill in variant_skills(variant):
        if norm_tag(skill) not in tags:
            errors.append(f"skill {skill!r} is claimed but no evidence entry tags it")
    for key in ("skills", "technologies"):
        for entry in variant.get(key, []) or []:
            if not isinstance(entry, dict):
                continue
            category = str(entry.get("category", "") or "").strip()
            items = [i for i in (entry.get("items", []) or []) if str(i).strip()]
            if not category:
                errors.append(f"[{key}] a skills group has no category name: {entry!r}")
            if not items:
                errors.append(f"[{key}] skills group {category!r} lists no items")
    if len(skill_groups(variant)) > 1 and any(not c for c, _ in skill_groups(variant)):
        errors.append(
            "skills mix grouped and ungrouped items; give every item a category "
            "or none of them"
        )

    # Canonical facts must match resume.yaml if present (employers and education).
    if resume_path and os.path.exists(resume_path):
        canon, _companies = canonical_facts(resume_path)
        for entry in canonical_employers(variant):
            key = (entry.get("company"), entry.get("title"), str(entry.get("dates")))
            if key not in canon:
                errors.append(
                    f"experience {key} diverges from canonical resume.yaml "
                    f"(employer/title/dates must match exactly)"
                )

    return errors


# ── cover mode ─────────────────────────────────────────────────────────────


def validate_cover(
    cover_path: str,
    variant_path: str,
    bank_path: str,
    note_path: str | None,
    banned: list[str] | None = None,
    banned_regex: list[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    banned = banned if banned is not None else list(DEFAULT_BANNED)
    banned_regex = banned_regex if banned_regex is not None else list(DEFAULT_BANNED_REGEX)
    with open(cover_path, encoding="utf-8") as fh:
        cover = fh.read()
    errors.extend(style_errors(cover, banned, "cover", banned_regex))
    with open(variant_path, encoding="utf-8") as fh:
        variant = yaml.safe_load(fh) or {}

    vtext = flat_text(variant)
    variant_nums = set(numerals(vtext))

    # Numerals from the company note (the hook) are also allowed — they are
    # claims about the company, not about the candidate. PRD §4.3, §8.6.
    allowed_nums = set(variant_nums)
    if note_path and os.path.exists(note_path):
        with open(note_path, encoding="utf-8") as fh:
            allowed_nums |= set(numerals(fh.read()))

    for n in numerals(cover):
        if n not in allowed_nums:
            errors.append(
                f"cover asserts numeral {n!r} that is absent from the validated variant "
                f"(a metric in the letter must trace to the resume)"
            )

    # Employer names present in the variant define the allowed employer vocab.
    variant_companies = {
        str(e.get("company", "")).strip()
        for e in canonical_employers(variant)
        if e.get("company")
    }
    # Any *other* known employer (from the bank's role: fields) mentioned in the
    # cover but not in the variant is a fabricated affiliation.
    if os.path.exists(bank_path):
        bank = parse_bank(bank_path)
        known_employers: set[str] = set()
        for e in bank.values():
            role = e["raw"].get("role", "")
            if "," in role:
                known_employers.add(role.split(",", 1)[1].strip())
        for emp in known_employers - variant_companies:
            if emp and re.search(rf"\b{re.escape(emp)}\b", cover):
                errors.append(
                    f"cover mentions employer {emp!r} that is not in the validated variant"
                )

        # Skills mentioned in the cover must be in the variant. A tag matches
        # however it is punctuated (see norm_tag), on both sides.
        for skill in bank_tags(bank):
            if len(skill) < 3:
                continue
            pattern = r"(?<![a-z0-9])" + r"[\s_/-]*".join(
                re.escape(part) for part in skill.split("-")
            ) + r"(?![a-z0-9])"
            if re.search(pattern, cover, re.IGNORECASE) and not re.search(
                pattern, vtext, re.IGNORECASE
            ):
                errors.append(
                    f"cover mentions skill {skill!r} that is not in the validated variant"
                )

    return errors


# ── cli ────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Provenance gate for resumes and covers.")
    parser.add_argument("variant", nargs="?", help="path to variant.yaml (resume mode)")
    parser.add_argument("--cover", help="path to cover.md (cover mode)")
    parser.add_argument("--variant", dest="variant_flag", help="variant.yaml for cover mode")
    parser.add_argument("--bank", default="profile/evidence-bank.md")
    parser.add_argument("--resume", default="profile/resume.yaml")
    parser.add_argument("--note", help="optional company note whose numerals are also allowed")
    parser.add_argument(
        "--lint-bank",
        action="store_true",
        help="check the bank's entries and `## Angles` block instead of a draft (PRD §21)",
    )
    parser.add_argument(
        "--entries-only",
        action="store_true",
        help="with --lint-bank: check entries only; no angles or shortfalls needed yet",
    )
    parser.add_argument(
        "--config",
        default="profile/config.yaml",
        help="config.yaml providing style.banned; built-in defaults if absent",
    )
    args = parser.parse_args(argv)

    banned, banned_regex = load_banned(args.config)

    if args.lint_bank:
        errors = lint_bank(args.bank, args.resume, args.entries_only)
        mode = f"bank {args.bank}" + (" (entries only)" if args.entries_only else "")
    elif args.cover:
        variant_path = args.variant_flag or args.variant
        if not variant_path:
            parser.error("--cover requires --variant")
        errors = validate_cover(
            args.cover, variant_path, args.bank, args.note, banned, banned_regex
        )
        mode = f"cover {args.cover}"
    else:
        if not args.variant:
            parser.error("a variant.yaml path is required")
        errors = validate_resume(args.variant, args.bank, args.resume, banned, banned_regex)
        mode = f"resume {args.variant}"

    if errors:
        print(f"FAIL: {mode} — {len(errors)} violation(s):", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print(
        f"OK: {mode} — "
        f"{'entries well-formed' if args.entries_only else 'angles hold' if args.lint_bank else 'provenance clean'}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
