# The optional nightly sweep

**You don't need this.** The everyday loop (`/apply` → apply by hand →
`/log`) is complete without it. The sweep is for people who'd rather have
Claude check chosen companies' job boards overnight than go looking for ads.
It costs about ten minutes of one-time settings work outside the chat, and it
only reaches employers whose careers pages run on one of these systems:

**Greenhouse · Lever · Ashby · Workable · SmartRecruiters · Recruitee ·
Workday · Oracle Recruiting Cloud · PageUp · Teamtailor**

It only ever talks to those systems' official public job-listing APIs. Never
LinkedIn, Indeed, Seek, Glassdoor, or anything behind a login: those forbid
it, and reaching them would break the rule the whole system is built on. A
role found there goes in by hand with `/apply`, same as always. Public
sector, healthcare systems, education and small local employers often aren't
on these systems either; if that's your field, stay with `/apply`.

What the sweep does each weekday morning: fetch every open posting from the
boards you listed, drop anything outside your locations, older than 30 days,
or already seen, score the rest with the same cheap triage `/apply` uses,
and queue the ones that clear your bar (plus the closest few that didn't,
clearly labelled) for you to look at with `/apply`. It never drafts anything
and never picks for you. Roles you drop never come back.

## Switch it on (four steps)

### 1. Tell it which companies

In a Claude Code session on your private copy, say: *"Set up the sweep. Here
are the companies I'd go to and their careers-page URLs: …"*. Claude copies
`optional/sweep/targets.example.yaml` to `profile/targets.yaml`, reads each
board's system and slug off the URL, and asks you for three honest lines on
each company (they go into `profile/companies/<name>.md` and feed the cover
letter's opening). If you can't write three honest lines, the company
doesn't belong. Add companies that hire for **every** track in your goals,
not just the first one.

Claude will also add a `scoring` block to `profile/config.yaml`:

```yaml
scoring:
  threshold: 70        # postings scoring below this are dropped
  queue_cap: 6         # at most this many survivors per night; more raises the bar for that night
  near_miss_band: 15   # postings within this many points under the bar are shown separately
  near_miss_cap: 4     # at most this many near misses per night
```

Optionally, a `role_filter` on `profile/goals.yaml` narrows big boards by
title before anything is scored (case-insensitive patterns; a posting is kept
if any matches). It is the one narrowing that can silently drop a good role
with an unhelpful title, so leave it out unless a board lists hundreds of
roles across every function. A good starting set is your tracks' `titles`.

```yaml
role_filter:
  - "<title word>"
  - "<another variant>"
```

Check it works: `python3 optional/sweep/bin/fetch.py --dry-run` fetches and
writes nothing.

### 2. Give the sweep its own environment

At [claude.ai/code](https://claude.ai/code), open the environment selector
(the cloud icon) and create a new environment for your repo. Call it
`jobseeker-sweep`.

**Network access:** choose **Custom**, tick *"Also include default list of
common package managers"*, and add the hosts for the systems you use:

```
boards-api.greenhouse.io      # greenhouse
api.lever.co                  # lever
api.ashbyhq.com               # ashby
jobs.ashbyhq.com              # ashby
apply.workable.com            # workable
api.smartrecruiters.com       # smartrecruiters
*.recruitee.com               # recruitee
*.myworkdayjobs.com           # workday
*.oraclecloud.com             # oracle
careers.pageuppeople.com      # pageup
<the company's own careers host>   # teamtailor (one per company)
```

A board whose host you didn't add simply returns nothing; nothing breaks,
and the morning report names it. Keep this environment locked to these hosts
on purpose: an unattended agent that can only reach job boards can't send
your data anywhere else. That is also why the sweep never researches
companies; `/apply` does that, with you present, in your normal environment.

**Setup script:**

```bash
#!/bin/bash
set -euo pipefail
pip install --break-system-packages typst pyyaml httpx pydantic
python3 -c "import typst, yaml, httpx, pydantic"
```

No `|| true`: a swallowed install failure becomes a silent broken morning.

**Secrets:** none. The APIs are public.

### 3. Schedule it

At claude.ai/code → **Routines** → **New Routine**. Attach your private repo
and the `jobseeker-sweep` environment. Trigger: **Scheduled → Weekdays →
06:00** local (runs may start a few minutes late). Prompt, pasted verbatim:

```
Read optional/sweep/SWEEP.md and follow it exactly. It is the
authoritative procedure. Work on main the whole run.

Invariants, restated:
- Stop at a shortlist. Do NOT draft anything, do NOT invoke the tailor
  subagent, do NOT pick or discard anything; the human decides later
  with /apply.
- Push the shortlist BEFORE marking anything seen.
- If fetch exits non-zero, abort and say so; never report a broken
  environment as a quiet night.
- Never submit an application, never fetch outside the job-board hosts,
  never modify profile/resume.yaml, config.yaml or goals.yaml, never
  create a branch or open a pull request.
- More survivors than config.scoring.queue_cap: raise the bar for THIS
  RUN ONLY, never write it to config.yaml, and say so.

End with the morning report from SWEEP.md. Nothing else.
```

The prompt is deliberately small: the procedure lives in this repo, so
improvements reach the routine without re-pasting.

### 4. Run it once by hand

The first run triages your whole backlog, possibly a hundred postings. Start
it yourself, on a day you're not busy, by opening a session in the
`jobseeker-sweep` environment and pasting the same prompt.

## Every morning after

Read the report. Open a normal session and run `/apply` with nothing pasted:
it shows what the sweep queued, you say which to draft. Discards are gone
for good.

## Notes

- **The bar is per run.** If a night has more survivors than `queue_cap`,
  the sweep raises the threshold for that night and says so. See the same
  override three mornings running? Change `config.yaml` yourself.
- **A track that never produces anything** usually has `titles` that are too
  narrow, or no company in `targets.yaml` hires for it. The report says which.
- **Cost.** One cheap triage call per new posting; zero expensive drafting.
  The expensive spend happens only when you say yes in `/apply`.
- **Switch it off** by deleting `profile/targets.yaml` and the routine.
  Nothing else changes.

## For technical users

```
optional/sweep/bin/fetch.py      fetch + filter + dedupe → queue/raw/  (--dry-run writes nothing)
optional/sweep/bin/seen.py       the dedupe index: status | check | mark | audit
optional/sweep/bin/lib/          schema, filters, dedupe, seen, sources/<ats>.py adapters
optional/sweep/tests/            sweep-only tests (python3 -m pytest runs them with the core suite)
state/seen/<date>.jsonl          the index itself, committed to main, append-only
```

Each supported system is one adapter file; a new one is a small addition.
