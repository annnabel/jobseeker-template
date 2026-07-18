# Annabel's Jobseeker — operating rules

This repo automates a personal job search: fetch postings from public ATS APIs,
triage cheaply into a shortlist pushed to `main`, let the human pick the keeps
(`/choose`, Gate 1), then tailor resumes and cover letters for those only
(`/tailor` — never during the unattended sweep, PRD §15/§18), gate every claim
for provenance, all before the human applies **by hand**. The full design is
in `PRD.md`. Read it before changing behaviour.

## Red lines (PRD §10) — load-bearing, non-negotiable

The sweep runs unattended, with no human in the loop and no approval prompts.
These hold everywhere, but especially there:

1. **Never fabricate or embellish** a metric, title, date, employer, or
   technology. A resume that wins an interview the candidate can't survive is
   worse than no resume.
2. **Never present an estimated or qualitative metric as a fact.** Directional
   phrasing only, and never a number, for estimates.
3. **Never submit an application. Never navigate to a submit button. Never POST
   to an ATS.** The human applies, in their own browser.
4. **Never scrape** LinkedIn, Indeed, or anything behind auth. Public ATS APIs,
   the user's own exports, the user's own notes.
5. **Never fetch outside the allowlist during the unattended sweep**, including
   for company research (§4.3). In an interactive session (`/tailor`, `/add`),
   public-web company research is allowed (PRD §16) — but red line 4 still has
   no exceptions, and the sweep's environment stays locked to the ATS hosts.
6. **Never assert a fact about the target company** that isn't in the JD or
   `profile/companies/<slug>.md`. Not from memory. Not from the model's priors.
   Research does not bypass this: findings go into the company note first, each
   with a source URL, and are cited from there (PRD §16).
7. **Never write to `profile/resume.yaml` or `profile/config.yaml` during a
   sweep.** Variants only.
8. **Never put seen-state in a PR.** It goes to `main` (§6).
9. **Never exceed `queue_cap`.** More survivors → raise the threshold for this
   run and say so.
10. **Never open a gate yourself.** Gate 1 is the human picking keeps in
    `/choose` — never pick, discard, or recommend on their behalf. And never
    merge your own PR (`/add`'s, or any other): a gate you can open yourself
    isn't a gate.
11. **Never delete from the evidence bank.** Mark `status: retired`.
12. On a missing fact about the user: **`[GAP]` + a specific question.** Never a
    plausible guess.
13. On a missing qualification: **`[SHORTFALL]`, stated plainly.** Never hidden,
    never written around.

## Invariants (PRD §3)

- **The repo is the database.** Everything that must survive a session is
  committed. There is no other storage.
- **The tracker is derived, never maintained.** Delete `tracker.csv`,
  regenerate with `bin/tracker.py`, get an identical file.
- **Every claim traces to an evidence ID**, enforced by `bin/validate.py`, not
  by vibes.
- **Questions are cheap; assumptions are expensive.** Write `[GAP]` and move on;
  never invent.
- **Bookkeeping is not a decision.** Gates review judgment; never gate a fact.
  Seen-state is a fact and goes straight to `main`.

## Two gap types — do not conflate (PRD §8.5)

- **`[GAP]`** — you don't know something about the *candidate*. Answerable. Gets
  answered at Gate 2 and written back to the evidence bank.
- **`[SHORTFALL]`** — the candidate doesn't have something the *role* wants. Not
  answerable. State it plainly; it appends to `## Shortfalls`.

## The linter's boundary (PRD §1/G6)

`validate.py` catches invention (a metric from nothing, an ev that doesn't
exist). It does **not** catch *stretching* (citing `ev:0031` but overstating
what `ev:0031` says). That's Gate 2's job. Never trust the green check to mean
more than it does.
