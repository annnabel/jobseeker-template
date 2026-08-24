"""Shared readers for a tailored variant.yaml.

validate.py, ats_score.py, and render.py each need the same two views of a
variant — every human-readable string in it, and its skills list — and each
had grown its own copy. One definition here keeps the three gates reading the
draft the same way; a variant that validates is the variant that scores and
renders.
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


def skills(variant: dict) -> list[str]:
    """The variant's skills list, under either accepted key (PRD §19).

    `technologies:` is the original key and still works. `skills:` is the
    field-neutral synonym — a nurse's variant lists clinical competencies, a
    teacher's lists curricula, and neither is a technology. Both may be
    present; the union, in that order and without duplicates, is what gets
    gated and rendered.
    """
    out: list[str] = []
    for key in ("skills", "technologies"):
        for item in variant.get(key, []) or []:
            if str(item).strip() and str(item) not in out:
                out.append(str(item))
    return out
