---
name: setup
description: Onboard a new user. Starts from what they already have (a resume, a LinkedIn profile, old cover letters, a few ads), then interviews them in small batches to confirm goals, canonical facts, evidence bank, angles and voice. Re-run any time to add evidence or change goals. No code editing, no terminal, no git talk.
---

# /setup — the whole onboarding

You are turning a fresh private copy into a working system. The user has a
browser and a phone, nothing else. Fill `profile/` by **confirmation where
they already wrote it down, interview where they didn't, in batches of three
to five questions, never a wall.** Save after each section (step 10) without
mentioning it. Never mention git, branches, commits or files; say "saved" at
most. Paths in this document are for you, not for them.

**You do not know this person.** Do not assume their field, seniority, or that
their work produces numbers. Ask, never fill in. Every value in the templates
is an angle-bracketed placeholder, not a suggestion. The red lines in
`CLAUDE.md` apply here as everywhere; the ones that bite during setup are 1
(never embellish), 9 (`[GAP]` and a question, never a guess) and 10 (a
`[SHORTFALL]` stated plainly).

**Two ways through.** The *quick start* gets them to a first `/apply` in
about half an hour: what they have, goals, facts confirmed, ten or so
entries, angles from those. The *full* interview is the same steps carried
further. Offer the quick start by default; the bank grows on every re-run
and on every `[GAP]` `/apply` answers.

## 0 — before anything: where are we, and where were we

**Guard.** Run `python3 bin/save.py --guard`. If it fails, this is the shared
template, not a private copy: relay its message (make a private copy with
"Use this template", open that, run `/setup` there), and stop. Write nothing.

**Resume from state.** The files present say where a previous session
stopped; nothing else needs remembering.

| Missing | Start at |
|---|---|
| anything in `profile/intake/` *and* `profile/goals.yaml` | step 1 |
| `profile/goals.yaml` or `profile/config.yaml` | step 2 |
| `profile/resume.yaml` | step 3 |
| `profile/evidence-bank.md` | step 4 |
| `## Angles` in the bank, or a track with empty `supporting_angles` | step 6 |
| `profile/voice.md` | step 7 |

If everything exists, this is a re-run: ask what they want to add or change
and go straight to that section. Adding evidence continues at step 4 with the
next unused `ev:` number (highest `### ev:NNNN` in the bank plus one; never
reuse a number, even a retired entry's), then re-runs step 6 for any new
entry. A changed goal, and any new or changed `pivot` track, re-runs steps 5
and 6 in full: angles argue for tracks, so new tracks need their angles
checked and `supporting_angles` refilled. New documents can be brought in on
any re-run (step 1); a new resume or letter feeds whichever section it bears
on.

**The progress line.** At every stop point, and whenever they ask where
things stand, print one line, nothing more:

```
What you have ✓ · Goals ✓ · Facts ✓ · Evidence 12 entries · Angles · Voice
```

A finished section gets a tick, the current one a count or nothing, the rest
their plain names. When the quick-start bar is met (facts confirmed, ten or
so entries, angles), say so on the same line: `ready for a first /apply`.

**Stopping is fine.** Each section is saved as it completes. When one ends,
print the progress line, say in one sentence that they can stop here and
`/setup` will pick up at the next section, then ask whether to go on.

## 1 — what they already have (about five minutes)

Before asking a single interview question, ask once, in one message, for
everything they have already written down. Each item is optional; "none of
these" is a fine answer and the interview simply runs longer.

- **Their current resume**, dropped into the chat or pasted as text. Any
  version, however stale.
- **Their own LinkedIn profile**, copied as text from their own page. Pasted
  text is theirs to give; nothing is fetched from LinkedIn (red line 4).
- **One or two cover letters they were happy with.** These set the voice.
- **Two or three ads they would apply to today.** These seed the goals and
  are the reality checks later. Ask for the whole posting, not a link.
- **Their LinkedIn connections export**, if they want referral paths spotted:
  LinkedIn → Settings → Data Privacy → Get a copy of your data →
  Connections. Only if it takes them under a minute; it can come later.

**Bringing a document in.** A file dropped into the chat arrives with a
path: run `python3 bin/intake.py <that path>`. It copies the file into
`profile/intake/`, writes a readable text twin beside a PDF or Word file,
and recognises the connections export by its header, writing it straight to
`profile/connections.csv` with LinkedIn's preamble dropped. Pasted text you
write yourself to `profile/intake/<short-name>.md` (`resume.md`,
`linkedin.md`, `cover-letter-1.md`, `ad-1.md`, …). A screenshot or photo of
a resume: read it and write what it says to `profile/intake/resume.md`. If
the script says it can't read a file, ask for the text pasted instead; never
guess at what a file you couldn't open contains.

**Read everything brought in before step 2**, and hold it in mind for the
rest of the session. From here on the rule is: **never ask for something the
intake already answers; show what you read and ask whether it is right.**

**What an old resume is, and is not.** It is a list of claims the user once
made, often stretched to fit a page. It is a fine source for names, titles,
dates and the shape of the work. It is **not** evidence: no number in it
earns a `confidence:` until they answer "is that a number you could point
to?", and nothing in it is `measured` without a source they name. An entry
seeded from it says so (`source: intake/resume.pdf`) only once its
confidence has been settled in conversation.

Save (step 10), then print the progress line.

## 2 — `profile/goals.yaml` and `profile/config.yaml`: where they want to GO (about ten minutes)

Copy `templates/goals.example.yaml` and `templates/config.example.yaml`.
Open with what you read: one or two sentences on where their history has
been, then the question: **where do they want to go next?** If they brought
ads, name what those ads have in common and ask whether that is the target.

Interview for one to three **tracks**. Per track: `label` (the job as they'd
describe it to a friend), `titles` (the title words employers actually use,
including the ugly variants; seed these from the ads' own titles and read
them back), `seniority` for them (student, graduate, early, mid, senior,
lead, exec, returner), `why` in one honest line, `must_have` / `avoid`.

Then the question that decides everything downstream: **is this track a
pivot?** Have they done this kind of work before, or are they moving into it?

- Not a pivot → `pivot: false`.
- A pivot → `pivot: true`, and fill `transferable` (which of their experience
  genuinely carries across, in their words) and `known_gaps` (what they
  plainly don't have yet). Both are honest-answer fields. A padded
  `transferable` produces a resume that wins an interview they can't survive.

Leave `supporting_angles` empty until step 6.

**Constraints belong here, not at the end.** In the same conversation, one
batch: pay floor in their currency, remote or not, locations as boards print
them, dealbreakers in their words. Write `constraints` into `config.yaml`
from those answers. Take `cover.max_words` and `tracker.ghost_days` from the
template defaults and say in one line what they are; change them only if
asked. Leave `style` and `ats` at their defaults unless asked.

## 3 — `profile/resume.yaml`: canonical facts and the header

Copy `templates/resume.example.yaml`. This comes **before** the evidence bank
because every entry's `role:` must end in an employer named here, and the
timeline is the spine the interview walks along.

**With a resume or profile in the intake, this is one batch, not an
interview.** Fill the file from what you read, then show it back compactly
(header, then each employer as `company · title · dates`, then education)
and ask for corrections. Ask only for what the documents lack: usually the
email and phone they want printed, the exact date format for jobs that only
say a year, the spelling they want for a company that changed its name.

**Without one, interview:**

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

## 4 — `profile/evidence-bank.md`: the master resume (the long one)

The source of truth every draft is capped by. Walk the timeline from
`resume.yaml`, most recent role first, steered by the tracks: on a pivot, dig
hardest at the experience the `transferable` line points to; it is usually
buried in a job called something else. On a student or graduate track,
coursework, projects, part-time work and volunteering all count.

**Seeded from the intake.** Where a resume or profile describes a role,
draft the entries yourself before asking anything: one entry per bullet or
per distinct piece of work (`templates/evidence-entry.md`: `role`, `dates`,
`metric`, `confidence`, `source`, `scope`, `tags`, `narrative`; leave
`angles:` empty). Then, per role, show the headlines you drafted in one short
list and run the confirmation for each, three to five at a time:

- the two or three lines that carry risk, read back verbatim: the `metric`
  and its `confidence`, and anything in the narrative that reads stronger
  than the bullet it came from. A resume bullet with a number is a claim;
  the question is "is that a number you could point to?" **measured** (a
  real number with a source they can name), **estimated** (a number they
  believe but can't cite), or **qualitative** (no number). Never push for a
  number they don't have; the honest qualitative version is stronger than a
  hedged fake. Never carry a resume's number into `metric` as `measured`
  on the strength of the resume alone.
- what the bullet leaves out: "the resume says X; what actually happened?"
  Old bullets are compressed. The narrative is where the story goes.
- one line saying what the entry proves about them, in three or four words.
  Keep it as a note beside the entry (`# proves: …`). Step 6 sorts these
  into angles instead of re-reading the whole bank.

Then ask for what no resume holds: the one or two things about that role
they'd want a stranger to know that never made it onto the page.

**Not seeded (no documents, or a role the documents skip): story first,
fields second.** Never ask for the fields one at a time. Per role, ask for
the two or three things they'd want a stranger to know, in their own words.
From each story draft the whole entry yourself, then read back only the two
risky lines above (metric and confidence; the `# proves:` note).

`tags` are whatever their field calls its capabilities. `role` ends in the
employer exactly as `resume.yaml` spells it.

**After every batch** of three to five entries, run
`python3 bin/validate.py --lint-bank --entries-only` and fix what it names
before asking the next question. It catches a malformed `confidence`, a
`measured` with no source, an untagged entry, a duplicate ID and a `role`
that matches no employer, while the person who knows the answer is still
here.

**First reality check, after the first ten or so entries.** Take the first
ad from the intake (a pivot track's if there is one), or ask them to paste
one now. Match its asks against what the bank holds so far and say which
land on an entry, which land on nothing, and which are a `[SHORTFALL]`. This
steers the rest of the interview toward what postings actually ask for, and
catches a `transferable` line that overreached while it is cheap to fix.

**The quick-start bar.** After the first reality check, if the bank holds
ten or so confirmed entries across the roles that matter most to the first
track, offer the exit: finish steps 5 to 7 now, which takes about ten
minutes, and come back to add more evidence any time. Say plainly that a
thin bank means more `[GAP]` questions during `/apply` and every answer
lands in the bank; it is not a worse route, only a shorter first pass.

How many is enough in the end depends on the career. These ranges are what a
finished bank tends to hold, reached across re-runs and `/apply` answers, not
a gate before the first draft. Stop a session when new questions stop
producing new material, not when a counter hits a number:

| Where they are | Realistic range |
|---|---|
| Student / graduate / first job | 10–20 |
| Career changer | 20–40, weighted toward the pivot |
| Early career | 20–35 |
| Mid career | 35–60 |
| Senior / long career / returner | 50+, pruned rather than skipped |

## 5 — `## Shortfalls`

Write a non-empty `## Shortfalls`: things target roles ask for that they
don't have, including everything the reality check surfaced and every pivot
track's `known_gaps`. Empty means they weren't honest. Nothing is ever
deleted from the bank; obsolete entries get `status: retired`.

## 6 — Angles: the argument each resume will make

Derive these **after** the entries exist. Group the `# proves:` notes from
step 4, read the groups back, and ask which of them they'd want a stranger to
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
argue for? A pivot track with no angle serving it means step 4 missed the
transferable work; go back for it.

## 7 — `profile/voice.md`: tone

A short description of how they write: plain vs formal, dry vs warm, how
they'd open a letter. **With a cover letter or two in the intake, draft this
yourself from them**, quote the one sentence that best shows the voice, and
ask whether that is how they want to sound. Without one, ask for a paragraph
they wrote and liked, if they have one to paste; otherwise interview in one
batch. Written once, used by every draft.

## 8 — `profile/connections.csv` (optional)

Usually handled in step 1. If it wasn't and they want referral paths spotted:
LinkedIn → Settings → Data Privacy → Get a copy of your data → Connections.
They drop the file into the chat and `python3 bin/intake.py <path>` writes
it to `profile/connections.csv`, header first, LinkedIn's preamble notes
dropped. Keep only the columns present; add nothing.

## 9 — the first ads

The ads brought in at step 1 are the user's own shortlist. Do not draft any
of them; they haven't said yes yet (red line 7). Point at them at the close.

## 10 — after each section

Save quietly:

```
python3 bin/save.py "setup: <section>"
```

If it fails, tell them in one plain line that saving didn't work and what the
message said; their answers are still in the files. Then offer the stop
point (step 0).

## 11 — close

Second reality check: hand-match two more real ads (the remaining ones from
the intake, or two they paste now) from their target tracks against the
finished bank. Can't find support? Either the bank is thin (interview more,
step 4) or the `transferable` line overreached (make it honest). Both are
better found now than in a draft.

Print the progress line, all ticks. Name the loop once: **`/apply` an ad →
apply by hand → `/log` it → `/prep` when an interview lands**. Suggest one
next thing: `/apply` one of the ads they brought in. If they took the quick
start, say in one sentence that `/setup` any time adds evidence, a role at a
time. Mention in one sentence that an optional nightly sweep of chosen
companies' job boards exists (`optional/sweep/README.md`) and needs some
settings work outside the chat; don't sell it.
