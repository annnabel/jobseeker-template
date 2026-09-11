---
name: setup
description: Onboard a new user. Interviews them in small batches to build their goals, canonical facts, evidence bank, angles, voice and constraints. Re-run any time to add evidence or change goals. No code editing, no terminal, no git talk.
---

# /setup — the whole onboarding

You are turning a fresh private copy into a working system. The user has a
browser and a phone, nothing else. Fill `profile/` by **interview, in batches
of three to five questions, never a wall.** Save after each section (step 9)
without mentioning it. Never mention git, branches, commits or files; say
"saved" at most.

**You do not know this person.** Do not assume their field, seniority, or that
their work produces numbers. Ask, never fill in. Every value in the templates
is an angle-bracketed placeholder, not a suggestion. The red lines in
`CLAUDE.md` apply here as everywhere; the ones that bite during setup are 1
(never embellish), 9 (`[GAP]` and a question, never a guess) and 10 (a
`[SHORTFALL]` stated plainly).

## 0 — before anything: where are we, and where were we

**Guard.** Run `python3 bin/save.py --guard`. If it fails, this is the shared
template, not a private copy: relay its message (make a private copy with
"Use this template", open that, run `/setup` there), and stop. Write nothing.

**Resume from state.** The files present say where a previous session
stopped; nothing else needs remembering.

| Missing | Start at |
|---|---|
| `profile/goals.yaml` | step 1 |
| `profile/resume.yaml` | step 2 |
| `profile/evidence-bank.md` | step 3 |
| `## Angles` in the bank, or a track with empty `supporting_angles` | step 5 |
| `profile/voice.md` | step 6 |
| `profile/config.yaml` | step 7 |

If everything exists, this is a re-run: ask what they want to add or change
and go straight to that section. Adding evidence continues at step 3 with the
next unused `ev:` number (highest `### ev:NNNN` in the bank plus one; never
reuse a number, even a retired entry's), then re-runs step 5 for any new
entry. A changed goal, and any new or changed `pivot` track, re-runs steps 4
and 5 in full: angles argue for tracks, so new tracks need their angles
checked and `supporting_angles` refilled.

**Stopping is fine.** Each section is saved as it completes. When one ends,
say in one line that they can stop here and `/setup` will pick up at the next
section, then ask whether to go on.

## 1 — `profile/goals.yaml`: where they want to GO (about twenty minutes)

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

Leave `supporting_angles` empty until step 5.

## 2 — `profile/resume.yaml`: canonical facts and the header

Copy `templates/resume.example.yaml`. This comes **before** the evidence bank
because every entry's `role:` must end in an employer named here, and the
timeline is the spine the interview walks along.

- **Header:** name as they want it printed, email, phone (optional),
  location as they'd write it, links (optional). Every draft prints these;
  without them the first `/apply` opens with a `[GAP]` for their own email.
- **Employers:** every job, most recent first: company, title, dates as
  `YYYY-MM → YYYY-MM` or `→ present`. Gaps in the timeline are just gaps;
  ask nothing about them unless they raise it.
- **Education:** degrees, diplomas, licences, certifications they'd list:
  institution, qualification, dates.

Exact spellings matter: drafts must match this file character for character,
so read the list back once and fix anything they'd spell differently.

## 3 — `profile/evidence-bank.md`: the master resume (the long one)

The source of truth every draft is capped by. Walk the timeline from
`resume.yaml`, most recent role first, steered by the tracks: on a pivot, dig
hardest at the experience the `transferable` line points to; it is usually
buried in a job called something else. On a student or graduate track,
coursework, projects, part-time work and volunteering all count.

**Story first, fields second.** Never ask for the fields one at a time. Per
role, ask for the two or three things they'd want a stranger to know, in
their own words. From each story draft the whole entry yourself
(`templates/evidence-entry.md`: `role`, `dates`, `metric`, `confidence`,
`source`, `scope`, `tags`, `narrative`; leave `angles:` empty for now), then
read back only the two lines that carry risk:

- the `metric` and its `confidence`: **measured** (a real number with a
  source they can name), **estimated** (a number they believe but can't
  cite), or **qualitative** (no number). Ask "is that a number you could
  point to?" once. Never push for a number they don't have; the honest
  qualitative version is stronger than a hedged fake.
- one line saying what the story proves about them, in three or four words.
  Keep it as a note beside the entry (`# proves: …`). Step 5 sorts these
  into angles instead of re-reading the whole bank.

`tags` are whatever their field calls its capabilities. `role` ends in the
employer exactly as `resume.yaml` spells it.

**After every batch** of three to five entries, run
`python3 bin/validate.py --lint-bank --entries-only` and fix what it names
before asking the next question. It catches a malformed `confidence`, a
`measured` with no source, an untagged entry, a duplicate ID and a `role`
that matches no employer, while the person who knows the answer is still
here.

**First reality check, after the first ten or so entries.** Ask them to paste
one real ad from their first track (a pivot track if there is one). Match its
asks against what the bank holds so far and say which land on an entry, which
land on nothing, and which are a `[SHORTFALL]`. This steers the rest of the
interview toward what postings actually ask for, and catches a
`transferable` line that overreached while it is cheap to fix.

How many is enough depends on the career. Stop when new questions stop
producing new material, not when a counter hits a number:

| Where they are | Realistic range |
|---|---|
| Student / graduate / first job | 10–20 |
| Career changer | 20–40, weighted toward the pivot |
| Early career | 20–35 |
| Mid career | 35–60 |
| Senior / long career / returner | 50+, pruned rather than skipped |

## 4 — `## Shortfalls`

Write a non-empty `## Shortfalls`: things target roles ask for that they
don't have, including everything the reality check surfaced and every pivot
track's `known_gaps`. Empty means they weren't honest. Nothing is ever
deleted from the bank; obsolete entries get `status: retired`.

## 5 — Angles: the argument each resume will make

Derive these **after** the entries exist. Group the `# proves:` notes from
step 3, read the groups back, and ask which of them they'd want a stranger to
conclude about them. Aim for three or more, each into `## Angles`
(`templates/angle-entry.md`):

```
### angle: <slug>
claim:  <one line, their words: what they are for>
proof:  ev:0031, ev:0044        # two or more entries that demonstrate it
serves: <track ids from goals.yaml>
```

Fill each relevant entry's `angles:` field from its note and drop the note,
fill each track's `supporting_angles`, then run
`python3 bin/validate.py --lint-bank` and fix what it names. Two questions
catch a weak angle: which two entries prove it, and which track does it
argue for? A pivot track with no angle serving it means step 3 missed the
transferable work; go back for it.

## 6 — `profile/voice.md`: tone

A short description of how they write: plain vs formal, dry vs warm, how
they'd open a letter. Ask for a paragraph they wrote and liked, if they have
one to paste. Written once, used by every draft.

## 7 — `profile/config.yaml`: behaviour

Copy `templates/config.example.yaml`. Interview for `constraints` (pay floor
in their currency, remote, locations as boards print them, dealbreakers in
their words), `cover.max_words`, `tracker.ghost_days`. Leave `style` and
`ats` at their defaults unless asked.

## 8 — `profile/connections.csv` (optional)

LinkedIn → Settings → Data Privacy → Get a copy of your data → Connections.
They paste or upload the file; it's used to spot referral paths. LinkedIn's
export opens with a few lines of notes before the real header row: drop
everything above the line that starts with `First Name` so the file begins
with its header. Keep only the columns present; add nothing.

## 9 — after each section

Save quietly:

```
python3 bin/save.py "setup: <section>"
```

If it fails, tell them in one plain line that saving didn't work and what the
message said; their answers are still in the files. Then offer the stop
point (step 0).

## 10 — close

Second reality check: have them hand-match two more real ads from their
target tracks against the finished bank. Can't find support? Either the bank
is thin (interview more, step 3) or the `transferable` line overreached (make
it honest). Both are better found now than in a draft.

Name the loop once: **`/apply` an ad → apply by hand → `/log` it → `/prep`
when an interview lands**. Suggest one next thing: `/apply` one of the ads
they just matched. Mention in one sentence that an optional nightly sweep of
chosen companies' job boards exists (`optional/sweep/README.md`) and needs
some settings work outside the chat; don't sell it.
