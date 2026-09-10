#!/usr/bin/env python3
"""render.py — variant.yaml -> resume.md (default) or PDF. PRD §8.2, §14.

    render.py <resume.yaml> -o <out.md>     # markdown — the routine's format
    render.py <resume.yaml> -o <out.pdf>    # Typst PDF — on demand only

Markdown is the deliverable (PRD §14): reviewable on a phone, diffable in a PR,
no Typst dependency. The human converts to a file themselves at submit time if
a portal demands an upload.

Both modes emit real text, single column, standard headings, and fail loudly if
any bullet lacks an evidence ID — a resume that renders is a resume that could
be sent, so the provenance floor is enforced here too, not only in validate.py.

The layout is the one recruiters read fastest and parsers read cleanly (PRD
§25): name, an optional `headline:` (the target, never a held title), the
contact line, then the sections in the variant's order — with Skills rendered
right after the summary, where a screener's eye lands, rather than after the
last job. A section with `style: paragraph` renders its bullets as prose (the
summary); everything else is a list. Skills are one category per line when the
variant groups them, one comma-separated line when it doesn't.

If the output isn't one you'd send unedited, fix this file — do not bail to
hand-editing. That failure mode kills the whole system (PRD §8.2).
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile

# Make lib/ importable whether run from repo root or elsewhere.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "lib"))

import yaml  # noqa: E402

from variant import skill_groups  # noqa: E402


def _contact_values(contact: dict):
    """Yield contact strings in display order, flattening list-valued fields.

    `contact.links` is naturally a YAML list (a person has several profiles);
    a bare `str(list)` would print `['https://…']` into the resume. Flatten so
    each link is its own entry. Scalar fields pass through unchanged.
    """
    for key in ("email", "phone", "location", "links"):
        value = contact.get(key)
        if not value:
            continue
        if isinstance(value, (list, tuple)):
            for item in value:
                if item:
                    yield str(item)
        else:
            yield str(value)


def _esc(text: str) -> str:
    """Escape Typst special characters in plain content."""
    out = str(text)
    for ch in ("\\", "#", "$", "*", "_", "`", "<", ">", "@", "[", "]", "~"):
        out = out.replace(ch, "\\" + ch)
    return out


def _is_paragraph(section: dict) -> bool:
    """`style: paragraph` renders a section's bullets as one block of prose."""
    return str(section.get("style", "") or "").strip().lower() == "paragraph"


def _skills_after(sections: list[dict]) -> int:
    """Index of the section Skills should follow: the summary when the variant
    opens with one (a bullets-only first section), else the last section.

    Skills near the top is the layout screeners and parsers both favour — a
    reader who stops after the summary has still seen the capabilities the
    angle rests on. A variant that opens straight into experience keeps
    Skills at the end, where it was.
    """
    if sections and sections[0].get("bullets") and not sections[0].get("entries"):
        return 0
    return len(sections) - 1


def _skills_lines(variant: dict, esc, bold) -> list[str]:
    """One rendered line per skills group; a nameless group is a bare list."""
    out: list[str] = []
    for category, items in skill_groups(variant):
        joined = esc(", ".join(items))
        out.append(f"{bold(esc(category))} {joined}" if category else joined)
    return out


def build_typst(variant: dict) -> str:
    """Generate ATS-safe Typst markup. Single column, standard headings, no
    tables/columns/graphics. Raises ValueError if a bullet lacks `ev`.
    """
    name = variant.get("name", "")
    headline = str(variant.get("headline", "") or "").strip()
    contact = variant.get("contact", {}) or {}
    contact_line = "  |  ".join(_contact_values(contact))

    lines: list[str] = [
        '#set text(font: "Helvetica", size: 10.5pt)',
        "#set page(margin: 1.9cm)",
        "#set par(justify: false, leading: 0.55em)",
        f"#align(center)[#text(size: 18pt, weight: \"bold\")[{_esc(name)}]]",
    ]
    if headline:
        lines.append(f"#align(center)[#text(size: 12pt)[{_esc(headline)}]]")
    if contact_line:
        lines.append(f"#align(center)[{_esc(contact_line)}]")
    lines.append("#v(0.4em)")

    sections = variant.get("sections", []) or []
    skills_lines = _skills_lines(variant, _esc, lambda t: f"*{t}:*")
    skills_after = _skills_after(sections)

    for i, section in enumerate(sections):
        heading = section.get("heading", "")
        lines.append(f"== {_esc(heading)}")
        bullets = section.get("bullets", []) or []
        for bullet in bullets:
            _require_ev(bullet, heading)
        if bullets and _is_paragraph(section):
            lines.append(" ".join(_esc(b.get("text", "")) for b in bullets))
        else:
            for bullet in bullets:
                lines.append(f"- {_esc(bullet.get('text', ''))}")
        for entry in section.get("entries", []) or []:
            company = _esc(entry.get("company", ""))
            title = _esc(entry.get("title", ""))
            dates = _esc(entry.get("dates", ""))
            header = f"*{title}*, {company}"
            lines.append(f"{header} #h(1fr) {dates}")
            for bullet in entry.get("bullets", []) or []:
                _require_ev(bullet, f"{heading}/{entry.get('company','?')}")
                lines.append(f"- {_esc(bullet.get('text', ''))}")
        lines.append("")
        if skills_lines and i == skills_after:
            lines.append("== Skills")
            for line in skills_lines:
                lines += [line, ""]

    if skills_lines and not sections:
        lines.append("== Skills")
        for line in skills_lines:
            lines += [line, ""]

    return "\n".join(lines) + "\n"


def build_markdown(variant: dict) -> str:
    """Generate the markdown resume. Single column, standard headings, plain
    text a human can review on a phone and paste into an ATS form. Raises
    ValueError if a bullet lacks `ev` (evidence IDs are not printed).
    """
    name = variant.get("name", "")
    headline = str(variant.get("headline", "") or "").strip()
    contact = variant.get("contact", {}) or {}
    contact_line = " | ".join(_contact_values(contact))

    lines: list[str] = [f"# {name}", ""]
    if headline:
        lines += [f"**{headline}**", ""]
    if contact_line:
        lines += [contact_line, ""]

    sections = variant.get("sections", []) or []
    # Two trailing spaces end a markdown line without opening a paragraph, so
    # each category stays on its own line in the rendered document and pastes
    # into a portal as separate lines.
    skills_lines = _skills_lines(variant, str, lambda t: f"**{t}:**")
    skills_block = ["## Skills", ""]
    skills_block += [line + "  " for line in skills_lines[:-1]] + skills_lines[-1:] + [""]
    skills_after = _skills_after(sections)

    for i, section in enumerate(sections):
        heading = section.get("heading", "")
        lines.append(f"## {heading}")
        lines.append("")
        bullets = section.get("bullets", []) or []
        for bullet in bullets:
            _require_ev(bullet, heading)
        if bullets and _is_paragraph(section):
            lines += [" ".join(str(b.get("text", "")) for b in bullets), ""]
        else:
            for bullet in bullets:
                lines.append(f"- {bullet.get('text', '')}")
        for entry in section.get("entries", []) or []:
            company = entry.get("company", "")
            title = entry.get("title", "")
            dates = entry.get("dates", "")
            location = entry.get("location", "")
            header = f"**{title}**, {company}"
            tail = " · ".join(str(x) for x in (dates, location) if x)
            if tail:
                header += f"  \n{tail}"
            lines += [header, ""]
            for bullet in entry.get("bullets", []) or []:
                _require_ev(bullet, f"{heading}/{entry.get('company', '?')}")
                lines.append(f"- {bullet.get('text', '')}")
            lines.append("")
        lines.append("")
        if skills_lines and i == skills_after:
            lines += skills_block

    if skills_lines and not sections:
        lines += skills_block

    out = "\n".join(lines)
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")
    return out.strip() + "\n"


def _require_ev(bullet: dict, where: str) -> None:
    if not str(bullet.get("ev", "")).strip():
        raise ValueError(
            f"bullet under {where!r} has no evidence ID; refusing to render: "
            f"{str(bullet.get('text',''))[:60]!r}"
        )


def render(variant_path: str, out_path: str, fmt: str | None = None) -> None:
    with open(variant_path, encoding="utf-8") as fh:
        variant = yaml.safe_load(fh) or {}

    if fmt is None:
        fmt = "pdf" if out_path.lower().endswith(".pdf") else "md"

    if fmt == "md":
        content = build_markdown(variant)  # raises before the file is touched
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return

    source = build_typst(variant)

    try:
        import typst  # lazy: only needed to produce the PDF
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "typst is not installed. Run: pip install typst  (see docs/ENVIRONMENT.md)"
        ) from exc

    with tempfile.NamedTemporaryFile("w", suffix=".typ", delete=False, encoding="utf-8") as tf:
        tf.write(source)
        typ_path = tf.name
    try:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        typst.compile(typ_path, output=out_path)
    finally:
        os.unlink(typ_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a resume variant to markdown (default) or PDF."
    )
    parser.add_argument("variant", help="path to variant.yaml")
    parser.add_argument("-o", "--out", required=True, help="output path (.md or .pdf)")
    parser.add_argument(
        "--format",
        choices=("md", "pdf"),
        default=None,
        help="output format; default inferred from the -o extension (.pdf -> pdf, else md)",
    )
    parser.add_argument(
        "--dump-typst", action="store_true", help="print generated Typst and exit (no PDF)"
    )
    args = parser.parse_args(argv)

    if args.dump_typst:
        with open(args.variant, encoding="utf-8") as fh:
            variant = yaml.safe_load(fh) or {}
        print(build_typst(variant))
        return 0

    render(args.variant, args.out, args.format)
    print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
