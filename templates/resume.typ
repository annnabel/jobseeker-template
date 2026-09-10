// resume.typ — reference of the ATS-safe layout render.py emits. PRD §8.2, §25.
//
// Rules an ATS parser needs, all obeyed below:
//   real text (not an image) · single column · no layout tables · no columns
//   no graphics/icons/text boxes · standard headings · left-aligned body
//
// And the order a screener reads in: name, headline (the target, never a held
// title), contact, summary as prose, then Skills one category per line, so a
// reader who stops after the top third has seen the argument and what backs
// it. Experience follows, angle proof bullets first within each role.
//
// render.py generates equivalent markup from variant.yaml; this file is the
// human-readable spec of that output. Compile: `typst compile resume.typ`.

#set text(font: "Helvetica", size: 10.5pt)
#set page(margin: 1.9cm)
#set par(justify: false, leading: 0.55em)

#align(center)[#text(size: 18pt, weight: "bold")[Full Name]]
#align(center)[#text(size: 12pt)[The Target Title, as the track or posting names it]]
#align(center)[email\@example.com  |  City, Region  |  a link worth following]
#v(0.4em)

== Summary
Three or four lines of prose that open on the angle's claim, made concrete for
this role, and name the posting's own required-tier terms where the evidence
plainly earns them (ev:0000, ev:0001 behind each sentence, never printed).

== Skills
// One line per category, category names in the posting's own vocabulary,
// the categories the angle rests on first. Whatever your field calls its
// capabilities: tools, clinical procedures, languages, curricula, licences,
// methods. Every item must be tagged by an evidence entry; a category name
// is layout, not a claim.
*A Category:* a-skill, another-skill, a-third

*Another Category:* a-fourth, a-fifth

== Experience
*Job Title*, Example Co #h(1fr) 2021-03 → 2023-08
- Accomplishment with a metric the evidence bank supports (ev:0000).
- A second bullet, one line, action verb first. No metric needed when the
  evidence entry is qualitative (ev:0001).
