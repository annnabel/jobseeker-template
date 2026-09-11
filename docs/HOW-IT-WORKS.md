# How it works — one page

## The loop

```
/setup   once: interview → profile/ (goals, facts, evidence bank, angles, voice, config)
/apply   paste an ad → honest fit read → "draft it?" → tailored resume + cover,
         walked through together → saved as a draft
   ↓     the human applies by hand, in their own browser
/log     "I applied" / "got a reply" / "rejected" → tracker regenerates
/prep    an interview landed → questions, STAR stories, honest gap answers
/next    "what now?" → one prioritised action
```

Two human gates, never opened by Claude: **which roles to draft** (the yes in
`/apply`) and **is the draft right** (the walkthrough, where `[GAP]`s get
answered and `[SHORTFALL]`s get read aloud).

## What lives where

| Path | Holds | Written by |
|---|---|---|
| `profile/goals.yaml` | Career tracks: where the user wants to go | `/setup`, the user |
| `profile/evidence-bank.md` | Every true accomplishment (`### ev:NNNN`), `## Angles`, `## Shortfalls` | `/setup`, gap answers |
| `profile/resume.yaml` | Canonical facts: name and contact header, employers, education, each title and date exactly once | `/setup` |
| `profile/voice.md` | How the user writes | `/setup` |
| `profile/config.yaml` | Constraints, cover length, style bans, tracker timers | `/setup` |
| `profile/companies/<slug>.md` | The user's own lines on a company, plus dated researched facts with source URLs | the user, `/apply`, `/prep` |
| `queue/shortlist/<slug>/` | A role found but not drafted: `jd.md`, `meta.yaml` | `/apply` (and the sweep) |
| `queue/ready/<slug>/` | A drafted role: `jd.md`, `meta.yaml`, `resume.yaml`, `resume.md`, `cover.md` | `/apply` |
| `applied/<date>_<slug>/` | The same, after the user applied; `prep.md` joins it later | `/log`, `/prep` |
| `tracker.csv` | Derived view of `applied/` and `queue/ready/` | `bin/tracker.py` only |
| `optional/sweep/` | The nightly sweep: code, tests, and its own README | off unless `profile/targets.yaml` exists |
| `docs/archive/PRD.md` | The original design document and its amendment history | frozen |

## Statuses (`meta.yaml → status`)

`shortlisted` found, not drafted · `kept` legacy, same as shortlisted ·
`near_miss` sweep-only, scored below the bar · `queued` drafted, awaiting a
hand submit · `applied` · `reply` · `screen` · `onsite` · `offer` ·
`rejected` · `withdrawn` · `ghosted` (derived: applied and silent past
`tracker.ghost_days`).

## The three files a draft is built from

- **Track** (`goals.yaml`): the job applied *for*. Triage scores against it.
  A `pivot: true` track carries `transferable` (the evidence that genuinely
  crosses over) and `known_gaps` (pre-declared shortfalls).
- **Evidence** (`evidence-bank.md`): what the user has *done*. Each entry has
  `confidence: measured | estimated | qualitative`, and that field decides
  whether a number may appear, appear directionally, or not at all.
- **Angle** (`## Angles`): the *argument*. `claim`, `proof: ev:…, ev:…` (two
  or more), `serves: <track ids>`. A draft declares exactly one `angle:`.

## The deterministic checks

- `python3 bin/validate.py <resume.yaml>` fails a bullet with no `ev:`, an
  `ev:` not in the bank, a hard number on an `estimated` entry, any numeral on
  a `qualitative` one, an employer/title/date that differs from
  `resume.yaml`, a skill no entry tags, an undeclared angle, a colon-led
  bullet, and any banned style pattern from `config.yaml → style`.
- `python3 bin/validate.py --cover cover.md --variant resume.yaml [--note
  profile/companies/<slug>.md]` fails a numeral, employer or skill in the
  letter that the validated resume doesn't carry (the note's own numerals are
  allowed in the hook).
- `python3 bin/validate.py --lint-bank` fails an entry with a bad or missing
  `confidence`, a `measured` entry with no `source`, an untagged entry, a
  duplicate ID, a `role` naming no employer or institution in `resume.yaml`,
  an empty `## Shortfalls`, an angle with fewer than two proof entries, an
  angle with no claim, or an entry citing an undeclared angle.
  `--entries-only` skips the angle and shortfall checks; `/setup` runs it
  after every batch of entries, before angles exist.
- `python3 bin/ats_score.py --jd jd.md --variant resume.yaml --cover cover.md`
  computes keyword coverage from the posting's own repeated terms, tiered by
  where the posting puts them. Its numbers are the only coverage numbers
  reported. It measures the draft, never the fit.
- `python3 bin/render.py resume.yaml -o resume.md` renders the markdown
  (name, headline, contact, summary, skills, then sections) and refuses any
  bullet without an `ev:`.
- `python3 bin/tracker.py` regenerates `tracker.csv`; `--stats` prints the
  funnel and callback rates by track, source and angle.

None of these use a model. Together they catch invention. They cannot catch
stretching; the walkthrough does that.

## The models

Triage (`.claude/agents/triage.md`, cheap model) scores one posting and
returns JSON. The tailor (`.claude/agents/tailor.md`, strongest model) writes
one draft, self-validates, runs the scorecard, and reports. `/apply` calls
both. The sweep calls only triage.

## Git, hidden

Every skill ends with `python3 bin/save.py "<message>"`, which commits and
pushes so the repo stays the only database. It rebases once on a rejected
push, never merges or rewrites history, and refuses to run inside the
shared template (its `--guard` is `/setup`'s first step). The user is never
asked to know what any of that means.
