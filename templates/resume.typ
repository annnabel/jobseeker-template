// resume.typ — reference of the ATS-safe layout render.py emits. PRD §8.2.
//
// Rules an ATS parser needs, all obeyed below:
//   real text (not an image) · single column · no layout tables · no columns
//   no graphics/icons/text boxes · standard headings · left-aligned body
//
// render.py generates equivalent markup from variant.yaml at sweep time; this
// file is the human-readable spec of that output. Compile: `typst compile resume.typ`.

#set text(font: "Helvetica", size: 10.5pt)
#set page(margin: 1.9cm)
#set par(justify: false, leading: 0.55em)

#align(center)[#text(size: 18pt, weight: "bold")[Full Name]]
#align(center)[email\@example.com  |  City, ST  |  github.com/handle]
#v(0.4em)

== Summary
- One line positioning statement tied to the target angle.

== Experience
*Staff Engineer*, Example Co #h(1fr) 2021-03 → 2023-08
- Accomplishment with a metric the evidence bank supports (ev:0000).
- A second bullet, one line, action verb first.

== Skills
technology, another-technology, a-third
