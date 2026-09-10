"""Shared readers for a tailored variant.yaml.

validate.py, ats_score.py, and render.py each need the same views of a
variant — every human-readable string in it, and its skills — and each had
grown its own copy. One definition here keeps the three gates reading the
draft the same way; a variant that validates is the variant that scores and
renders.

The skills field (PRD §25) takes two shapes, and both keys (`skills:`, the
field-neutral name, and `technologies:`, the original) accept either:

    skills: [a-skill, another-skill]            # flat — the original shape

    skills:                                     # grouped — one line per category
      - category: <a heading in the posting's own vocabulary>
        items: [a-skill, another-skill]
      - category: <the next category>
        items: [a-third]

A flat list renders as one comma-separated line; grouped skills render one
category per line, in the order written, so the tailor's ordering (the
angle's categories first) survives into the document. `skills()` flattens
both shapes for the gates, which check items and never category names.
"""
from __future__ import annotations


def flat_text(variant: dict) -> str:
    """Every human-readable string in the variant, flattened for text search."""
    parts: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif node is not None:
            parts.append(str(node))

    walk(variant)
    return "\n".join(parts)


def skill_groups(variant: dict) -> list[tuple[str, list[str]]]:
    """The variant's skills as ordered (category, items) groups.

    A bare string in the list belongs to the unnamed group (category ""), so a
    flat list is one unnamed group and a grouped list keeps its headings. Both
    accepted keys are read, `skills:` first, and an item already listed is not
    listed again. Groups with nothing in them are dropped; validate.py reports
    them separately, since an empty category on a resume is a mistake, not a
    layout choice.
    """
    groups: list[tuple[str, list[str]]] = []
    seen: set[str] = set()

    def add(category: str, item) -> None:
        text = str(item).strip() if item is not None else ""
        if not text or text in seen:
            return
        seen.add(text)
        for name, items in groups:
            if name == category:
                items.append(text)
                return
        groups.append((category, [text]))

    for key in ("skills", "technologies"):
        for entry in variant.get(key, []) or []:
            if isinstance(entry, dict):
                category = str(entry.get("category", "") or "").strip()
                for item in entry.get("items", []) or []:
                    add(category, item)
            else:
                add("", entry)
    return [(name, items) for name, items in groups if items]


def skills(variant: dict) -> list[str]:
    """The variant's skills, flattened, under either accepted key (PRD §19).

    `technologies:` is the original key and still works. `skills:` is the
    field-neutral synonym — a nurse's variant lists clinical competencies, a
    teacher's lists curricula, and neither is a technology. Both may be
    present, flat or grouped; the union, in written order and without
    duplicates, is what gets gated and scored. Category names are layout,
    not claims, and are never in this list.
    """
    out: list[str] = []
    for _category, items in skill_groups(variant):
        out.extend(items)
    return out
