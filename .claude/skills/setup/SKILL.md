---
name: setup
description: Onboard a new user. Interviews them in small batches to build their goals, evidence bank, angles, voice and constraints. Re-run any time to add evidence or change goals. No code editing, no terminal, no git talk.
---

# /setup — the whole onboarding

You are turning a fresh private copy into a working system. The user has a
browser and a phone, nothing else. Fill `profile/` by **interview, in batches
of three to five questions, never a wall.** Save after each section (step 8)
without mentioning it.

**You do not know this person.** Do not assume their field, seniority, or that
their work produces numbers. Ask, never fill in. Every value in the templates
is an angle-bracketed placeholder, not a suggestion.

If `profile/` is already populated, ask what they want to add or change and
go straight to that section.

## 1 — `profile/goals.yaml`: where they want to GO (do this first)

Copy `templates/goals.example.yaml`. Interview for one to three **tracks**.
Per track: `label` (the job as they'd describe it to a friend), `titles` (the
title words employers actually use, including the ugly variants),
`seniority` for them (student, graduate, early, mid, senior, lead, exec,
returner), `why` in one honest line, `must_have` / `avoid`.

Then the question that decides everything downstream: **is this track a
pivot?** Have they done this kind of work before, or are they moving into it?

- Not a pivot → `pivot: false`.
- A pivot → `pivot: true`, and fill `transferable` (which of their experience
  genuinely carries across, in their words) and `known_gaps` (what they
  plainly don't have yet). Both are honest-answer fields. A padded
  `transferable` produces a resume that wins an interview they can't survive.

Leave `supporting_angles` empty until step 3.

## 2 — `profile/evidence-bank.md`: the master resume (the long one)

The source of truth every draft is capped by. Interview story by story,
steered by the tracks: on a pivot, dig hardest at the experience the
`transferable` line points to; it is usually buried in a job called something
else.

Each accomplishment becomes an `### ev:NNNN` entry (`templates/evidence-entry.md`):
`role` (must match an employer in resume.yaml), `dates`, `metric`, `scope`,
`tags`, `angles`, `narrative`, and `confidence`: **measured** (a real number
with a source, recorded), **estimated** (a number they believe but can't
cite), or **qualitative** (no number). This field is load-bearing; the
linter enforces it.

How many is enough depends on the career. Stop when new questions stop
producing new material, not when a counter hits a number:

| Where they are | Realistic range |
|---|---|
| Student / graduate / first job | 10–20 (coursework, projects, part-time work, volunteering all count) |
| Career changer | 20–40, weighted toward the pivot |
| Early career | 20–35 |
| Mid career | 35–60 |
| Senior / long career / returner | 50+, pruned rather than skipped |

**Not every accomplishment has a number, and that is fine.** Never push for a
number they don't have; the honest qualitative version is stronger than a
hedged fake. `tags` are whatever their field calls its capabilities.

Then write a non-empty `## Shortfalls`: things target roles ask for that they
don't have. Empty means they weren't honest. A pivot track's `known_gaps`
belong here too. Nothing is ever deleted from the bank; obsolete entries get
`status: retired`.

## 3 — Angles: the argument each resume will make

Derive these **after** the entries exist. Read back what the bank holds and
ask which of these they'd want a stranger to conclude about them. Aim for
three or more, each into `## Angles` (`templates/angle-entry.md`):

```
### angle: <slug>
claim:  <one line, their words: what they are for>
proof:  ev:0031, ev:0044        # two or more entries that demonstrate it
serves: <track ids from goals.yaml>
```

Tag each relevant entry's `angles:` field, fill each track's
`supporting_angles`, then run `python3 bin/validate.py --lint-bank` and fix
what it names. Two questions catch a weak angle: which two entries prove it,
and which track does it argue for?

## 4 — `profile/resume.yaml`: canonical facts

Every employer, title and date, exactly once. Drafts must match this.

## 5 — `profile/voice.md`: tone

A short description of how they write: plain vs formal, dry vs warm, how
they'd open a letter. Written once, used by every draft.

## 6 — `profile/config.yaml`: behaviour

Copy `templates/config.example.yaml`. Interview for `constraints` (pay floor
in their currency, remote, locations as boards print them, dealbreakers in
their words), `cover.max_words`, `tracker.ghost_days`. Leave `style` and
`ats` at their defaults unless asked.

## 7 — `profile/connections.csv` (optional)

LinkedIn → Settings → Data Privacy → Get a copy of your data → Connections.
They upload the CSV; it's used to spot referral paths.

## 8 — after each section

Save quietly:

```
git add -A && git commit -q -m "setup: <section>" && git push -q origin main \
  || (git pull -q --rebase origin main && git push -q origin main)
```

At the end, have them hand-match three real ads from their target tracks
against the bank (a pivot track included). Can't find support? Either the
bank is thin (interview more) or the `transferable` line overreached (make it
honest). Both are better found now than in a draft.

Close by naming the loop once: **`/apply` an ad → apply by hand → `/log`
it → `/prep` when an interview lands**. Suggest one next thing: `/apply` a
real ad they've been sitting on. Mention in one sentence that an optional
nightly sweep of chosen companies' job boards exists
(`optional/sweep/README.md`) and needs some settings work outside the chat;
don't sell it.
