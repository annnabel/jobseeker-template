"""Deterministic fetch-layer scoping: location, role, freshness. PRD §8.1, §19.

One rule governs everything here: **bookkeeping, not judgment.** These filters
scope which postings enter the queue at all — a big employer's board lists
every office worldwide, and a board that never prunes still lists roles filled
months ago — but they never rank anything, and a posting with missing data is
always kept: missing data goes to triage, which can judge it; a filter cannot.

* **Location** — `profile/targets.yaml` may set `location_filter`, a list of
  case-insensitive regexes; a posting is kept when any pattern matches its
  location string.
* **Role** — `profile/goals.yaml` may set `role_filter`, the same shape,
  matched against the title. Off by default, because it is the one narrowing
  that can drop a role a keyword rule misjudges — a posting whose title names
  the team, the grade, or the employer's own coinage rather than the work —
  so fetch.py reports the drop count every run rather than letting it go
  unseen (PRD §19).
* **Freshness** — a posting not updated within `max_age_days` is skipped
  before it costs a triage call. Adapters normalize `updated_at`
  inconsistently (greenhouse/ashby/smartrecruiters emit ISO 8601, workable a
  bare date, lever epoch milliseconds); all are handled here, and an
  unparseable date reads as "unknown, keep", never as "stale".
"""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timedelta, timezone

import yaml


def _any_pattern_matches(text: str, patterns: list[str] | None) -> bool:
    """True when no filter is set, the text is empty (goes to triage), or any
    case-insensitive regex matches."""
    if not patterns:
        return True
    if not text.strip():
        return True
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def location_matches(location: str, patterns: list[str] | None) -> bool:
    return _any_pattern_matches(location, patterns)


def title_matches(title: str, patterns: list[str] | None) -> bool:
    return _any_pattern_matches(title, patterns)


def load_goals(root: str) -> dict:
    """Return profile/goals.yaml as a dict, or {} when it does not exist.

    Absent goals is a valid state (the file arrives during /setup), so this
    never raises on a missing file — callers degrade to no role filtering.
    A file that parses to something other than a mapping (a stray list, a bare
    string) is reported and treated as absent: a hand-edited profile must not
    end a sweep with an AttributeError three frames down.
    """
    path = os.path.join(root, "profile", "goals.yaml")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        print(f"warning: {path} is not a mapping; ignoring it", file=sys.stderr)
        return {}
    return data


def role_filter(goals: dict) -> list[str]:
    return goals.get("role_filter") or []


def parse_updated_at(value: str) -> datetime | None:
    """Best-effort parse of an adapter's `updated_at` into an aware UTC time.

    Returns None when the value is empty or unrecognizable — callers must
    treat that as "unknown, keep", never as "stale".
    """
    v = (value or "").strip()
    if not v:
        return None
    # Epoch seconds (10 digits) or milliseconds (13 digits), as lever emits.
    if re.fullmatch(r"\d{10}", v):
        return datetime.fromtimestamp(int(v), tz=timezone.utc)
    if re.fullmatch(r"\d{13}", v):
        return datetime.fromtimestamp(int(v) / 1000, tz=timezone.utc)
    try:
        parsed = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def is_fresh(updated_at: str, max_age_days: int, now: datetime | None = None) -> bool:
    """True when the posting was updated within `max_age_days`, or when its
    age is unknowable. `max_age_days <= 0` disables the filter entirely.
    """
    if max_age_days <= 0:
        return True
    parsed = parse_updated_at(updated_at)
    if parsed is None:
        return True
    if now is None:
        now = datetime.now(tz=timezone.utc)
    return now - parsed <= timedelta(days=max_age_days)
