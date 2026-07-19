---
name: setup
description: Onboard a new user. Interviews them in small batches to build the evidence bank (the master resume), then their voice, constraints, and targets. This is the whole onboarding — no code editing, no terminal, no PRD reading.
---

# /setup — the whole onboarding (PRD §11 Phase 2, §12)

You are turning a fresh private instance into a working system. The user has a
browser and a phone, nothing else. No code edits. Your job is to fill
`profile/`. Do it by **interview, in batches of 3–5 questions — never a wall**.

## What you're building (in order)

### 1. `profile/evidence-bank.md` — the master resume (half a day, unavoidable)
This is the source of truth every resume is capped by. Exhaustive by design.
Interview the user story by story. For each accomplishment, capture an
`### ev:NNNN` entry (see `templates/evidence-entry.md`) with:
- `role` (must match an employer you'll record in resume.yaml)
- `dates`, `metric`, `scope`, `tags`, `angles`, `narrative`
- `confidence`: **measured** (a real number with a source — record the source),
  **estimated** (a number you believe but can't cite — phrase directionally),
  or **qualitative** (no number). Be honest; this field is load-bearing and the
  linter enforces it.

Push for 40+ entries. Then derive 3+ **angles** (positioning stances) and,
crucially, a non-empty `## Shortfalls` — things target roles ask for that the
user doesn't have. If Shortfalls is empty, they weren't honest, and triage will
be worthless. Nothing is ever deleted from the bank; obsolete entries get
`status: retired`.

### 2. `profile/resume.yaml` — canonical facts
Every employer, title, and date, exactly once. Variants must match this.

### 3. `profile/voice.md` — tone
A short description of how the user writes: plain vs. formal, dry vs. warm,
first-person cover voice. This is the tailor's TONE parameter, written once.

### 4. `profile/config.yaml` — behaviour
Copy `templates/config.example.yaml`. Interview for `constraints` (comp floor,
remote, dealbreakers), `scoring.threshold`, `scoring.queue_cap`,
`cover.max_words`, `tracker.ghost_days`. The template defaults for
`scoring.near_miss_band` / `scoring.near_miss_cap` (the tier that surfaces the
closest below-threshold roles at Gate 1 so a thin night isn't silent) are
sensible as-is — mention they exist and can be tuned, but don't belabour them;
set `near_miss_band: 0` if the user wants triage to be a hard cut.

### 5. `profile/targets.yaml` — companies (Phase 4)
Copy `templates/targets.example.yaml`. For each company the user names, find its
ATS + board slug (ask them to paste the careers-page URL). For the top ~20, have
them write `profile/companies/<slug>.md` — three honest lines on why they'd go
(PRD §4.3). If they can't write three honest lines, the company doesn't belong.

### 6. `profile/connections.csv` (optional)
LinkedIn → Settings → Data Privacy → Get a copy of your data → Connections.
Commit the CSV. It matches referral paths against each job's company.

## After each section
Commit it. In a cloud session, committed is the only kind of existing (PRD §5.2).

Then have the user hand-match 3 real JDs against the bank. Can't find support?
The bank is thin — go back and interview more. Every later phase is capped by
this file.
