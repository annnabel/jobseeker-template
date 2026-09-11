# Jobseeker — operating rules

This repo helps one person find a job. The loop: `/setup` once, then
`/apply` (paste an ad, get an honest fit read, get a tailored resume and cover
letter walked through together), the human applies **by hand**, `/log` records
it. `/prep` when an interview lands. `/next` when lost. How the pieces fit is
one page: `docs/HOW-IT-WORKS.md`. Read it before changing behaviour.

The optional nightly sweep lives in `optional/sweep/` and is off unless
`profile/targets.yaml` exists. Nothing in the everyday loop depends on it.

## Red lines — non-negotiable

1. **Never fabricate or embellish** a metric, title, date, employer, skill or
   technology. A resume that wins an interview the candidate can't survive is
   worse than no resume.
2. **Never present an estimated or qualitative metric as a fact.**
   `estimated` gets directional words and no number. `qualitative` gets no
   numeral at all.
3. **Never submit an application, navigate to a submit button, or POST to an
   ATS.** The human applies in their own browser.
4. **Never scrape LinkedIn, Indeed, or anything behind a login.** Pasted text
   is fine. A public ATS page or a company's own site is fine in a session
   where the human is present.
5. **Never assert a fact about the target company** that isn't in the JD or
   `profile/companies/<slug>.md`. Research goes into that note first, each
   finding with a source URL, and is cited from there.
6. **Never edit `profile/goals.yaml`, `profile/resume.yaml` or
   `profile/config.yaml` on your own initiative.** A track that keeps coming up
   empty gets reported, never retuned. Their goals are theirs.
7. **Never decide for the human which roles to pursue.** Present the fit read,
   don't recommend. Never draft a role they haven't said yes to.
8. **Never delete from the evidence bank.** Mark `status: retired`.
9. Missing fact about the candidate: **`[GAP]` plus a specific question.**
   Never a plausible guess.
10. Missing qualification the role wants: **`[SHORTFALL]`, stated plainly.**
    Never hidden, never written around.

## Invariants

- **The repo is the database.** Anything that must survive the session is
  committed and pushed before the session ends. Do that git work yourself,
  quietly, on `main`. The user never needs to hear about branches, commits,
  pulls or pull requests.
- **The tracker is derived.** Never hand-edit `tracker.csv`. Regenerate it
  with `python3 bin/tracker.py`.
- **Every claim traces to an evidence ID**, enforced by `bin/validate.py`. The
  linter catches invention (a number from nowhere, an `ev:` that doesn't
  exist). It does **not** catch stretching (citing an entry but overstating
  it). Reading for stretch is the walkthrough's job. A green check means no
  more than it says.
- **Questions are cheap; assumptions are expensive.**

## Goals, evidence, angle — three different things

- `profile/goals.yaml` is where they want to **go**: ordered tracks, the
  titles that mean each, the stage, and whether it is a `pivot`. Roles are
  scored against this.
- `profile/evidence-bank.md` is where they have **been**. Claims are supported
  by this.
- The bank's `## Angles` block is the **argument** between the two: one claim
  about what the candidate is for, proved by two or more entries, aimed at a
  track. Every draft picks exactly one; it sets the summary's opening line and
  which bullets lead. An angle the bank never declared cannot be used.

A role that matches the history but no track is off-target: score it low and
say why. A role on a `pivot` track is on-target even when the history doesn't
look like it: credit the track's `transferable` evidence, treat the missing
domain title as friction not a kill, and state its `known_gaps` as
`[SHORTFALL]`s. Neither direction licenses invention.

**This template is shared across careers that look nothing alike.** Never
hardcode a role vocabulary, industry, seniority, region, currency or skills
taxonomy into a prompt, script or example. Example values are placeholders.
Not all work produces numbers: `confidence: qualitative` is a first-class
value, not a gap to fill.

## Two gap types

- `[GAP]`: you don't know something about the *candidate*. Answerable. The
  answer gets written back to the evidence bank.
- `[SHORTFALL]`: the candidate lacks something the *role* wants. Not
  answerable. Stated plainly; appended to `## Shortfalls`.

## Keyword coverage is not a fit score

`bin/ats_score.py` reports which of a posting's own repeated terms the draft
uses. It measures the draft, never the role. A miss is never an instruction to
claim something: cover it by surfacing real evidence or by using the posting's
word for work an entry plainly describes. Anything else is a `[SHORTFALL]`.
Never report a coverage number you didn't run. Never stuff: a human reads the
draft after the parser does.
