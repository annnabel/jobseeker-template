"""Deterministic role scoping for the fetch layer. PRD §19.

`profile/goals.yaml` may set `role_filter`, a list of case-insensitive regexes
matched against the posting title. A posting is kept when any pattern matches.
Like `locations.py` this is bookkeeping, not judgment: it scopes which postings
enter the queue at all, it never ranks them. A posting with no title is kept —
missing data goes to triage, which can judge it; a filter cannot.

Off by default. Unlike the location filter, this one can drop a role a keyword
rule misjudges (a "Growth Associate" posting that is really the analyst job),
so the sweep reports the drop count every run rather than letting the narrowing
go unseen.
"""
from __future__ import annotations

import os
import re

import yaml


def title_matches(title: str, patterns: list[str] | None) -> bool:
    if not patterns:
        return True
    if not title.strip():
        return True
    return any(re.search(p, title, re.IGNORECASE) for p in patterns)


def load_goals(root: str) -> dict:
    """Return profile/goals.yaml as a dict, or {} when it does not exist.

    Absent goals is a valid state (the file arrives during /setup), so this
    never raises on a missing file — callers degrade to no role filtering.
    """
    path = os.path.join(root, "profile", "goals.yaml")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def role_filter(goals: dict) -> list[str]:
    return goals.get("role_filter") or []
