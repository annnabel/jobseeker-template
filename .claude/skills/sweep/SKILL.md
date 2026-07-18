---
name: sweep
description: The nightly routine entrypoint. Fetch ATS postings, triage them cheaply, and push a shortlist to main. No tailoring happens here — the human picks keeps later with /choose, then /tailor develops them. Runs unattended — no approval prompts. Never submits, never merges.
---

# /sweep — the unattended job search (PRD §4, §9, §15, §18)

You are running with **no human in the loop**. There is no one to ask. Be
precise. The red lines in `CLAUDE.md` are load-bearing here above all.

The sweep's job ends at a **shortlist**, committed straight to `main`
(PRD §18 — no sweep branch, no PR). It does not tailor. Tailoring is
expensive and human-triggered (`/choose` picks the keeps, `/tailor` develops
them, PRD §15/§18) — invoking the `tailor` subagent from a sweep is a bug.

Work on `main` the whole run; never create a branch.

## Order of operations

0. **Pre-flight dedupe check** — `python3 bin/seen.py audit`. Confirms every
   role a prior sweep queued has a seen record; a `MISS` means the index is
   incomplete and this run would re-triage those roles. Repair first (the audit
   output names the fix), then continue. `bin/seen.py status` shows what the
   index currently holds. An empty index is normal only on the very first sweep.

1. **Fetch** — `python3 bin/fetch.py --source all`. This reads
   `profile/targets.yaml`, skips postings last updated more than 30 days ago
   (postings with no parseable date pass through to triage), dedupes against
   `state/seen/*.jsonl`, and writes new postings to `queue/raw/`. One dead adapter logs a warning and the run
   continues — note which boards failed for the closing report, so the human
   knows coverage was partial. If fetch exits **non-zero** (every adapter
   failed), the environment is broken: **abort the sweep** and say so plainly.
   Do not report a quiet night. It also warns loudly if the seen
   index is empty.

2. **Triage** — for each posting in `queue/raw/`, invoke the `triage` subagent
   (haiku) once. Collect `{score, reason, red_flags}`. Keep postings scoring
   at or above `config.scoring.threshold`. Everything below is **killed**.

3. **Cap** — if more than `config.scoring.queue_cap` postings survive, raise the
   threshold **for THIS RUN ONLY**. Do not write it to `config.yaml`. Record in
   the closing report what you raised it to and which roles it cost. (PRD §9.)

4. **Shortlist** — for each survivor, write `queue/shortlist/<slug>/`:
   - `jd.md` — the full posting: company, title, location, apply URL, source
     ATS, and the complete JD text. This is everything `/tailor` will need;
     it must not have to re-fetch.
   - `meta.yaml` — the sweep's findings, no judgment beyond triage's:
     ```yaml
     company:
     title:
     location:
     url:
     source:            # greenhouse | lever | ashby | workable | smartrecruiters
     fingerprint:       # copy VERBATIM from the raw posting JSON — this is the
                        # seen-state identity; audit depends on it being exact
     status: shortlisted
     swept: <YYYY-MM-DD>
     triage:
       score:
       reason:
       red_flags: []
     keywords: []       # top-5 ATS keywords from the JD, for the human's skim
     referral:          # matching name from connections.csv, else "none"
     company_note:      # present | missing (profile/companies/<slug>.md)
     ```
   No resume, no cover, no Opus. A shortlist entry is a *finding*, not a draft.

   **Zero survivors** is a valid outcome: skip step 5 (nothing to commit),
   still do step 6 for the killed postings (marking them on `main` is what
   stops tomorrow's sweep re-triaging them), and end by reporting
   "swept N, shortlisted 0" with the threshold used.

5. **Commit the shortlist to `main` — make it durable first.**
   ```
   git add queue/shortlist/
   git commit -m "sweep: shortlist $(date +%F) · <n> candidates"
   git push origin main
   ```
   Commit `queue/shortlist/` only (`queue/raw/` is gitignored scratch;
   seen-state is its own commit in step 6). If the push is rejected
   (someone pushed to `main` meanwhile), `git pull --rebase origin main`
   and push again.

   The order is load-bearing: the shortlist must reach the remote **before**
   any posting is marked seen. A crash after this push but before step 6
   costs at worst a duplicated triage next run; the reverse order costs
   roles marked seen that were never durably queued — gone silently, forever
   (PRD §6).

6. **Seen-state — its own commit, never mixed with the shortlist.** Mark
   every terminal disposition with the CLI — do not hand-write JSONL or
   improvise inline Python:
   ```
   python3 bin/seen.py mark --disposition killed      <each killed raw .json>
   python3 bin/seen.py mark --disposition shortlisted <each surviving raw .json>
   python3 bin/seen.py audit --date $(date +%F)       # must print OK
   ```
   `mark` is idempotent (already-seen fingerprints are skipped), so retrying
   is safe. The audit checks both directions: a `MISS` means a shortlisted
   role has no seen record; a `LOST` means a seen record has no shortlist
   entry. Repair before going further — the output names the fix.
   Then delete the processed files from `queue/raw/` (they are recorded in
   the shard and the shortlist now), and land the shard:
   ```
   git add state/seen/ && git commit -m "sweep: seen-state $(date +%F)"
   git push origin main
   ```
   Seen-state contains no judgment and is never reviewable — it is a fact,
   not a proposal. Keeping it in its own commit keeps the shortlist commit
   readable as pure findings.

7. **Report** — end the run with a summary in the session (this is what the
   human reads in the morning; there is no PR): one block per shortlisted
   role — company, title, location, triage score + reason, red flags, top-5
   JD keywords, referral match, and `[GAP] No company note for <company>`
   where the note is missing. If any adapters failed in step 1, one line
   naming them ("coverage was partial: …"). If the cap raised the threshold,
   say so and name what it cost. Close with one line telling the human what
   to do next: *"Run /choose in a fresh session to pick keeps, then /tailor."*
   Nothing else. No drafts. No interview prep.

## Never (red lines)
- Never invoke the `tailor` subagent — tailoring is human-triggered (PRD §15).
- Never pick keeps or discard shortlist entries — that is `/choose`, Gate 1,
  and it is the human's (PRD §18).
- Never submit an application or navigate to a submit button.
- Never modify `profile/resume.yaml` or `profile/config.yaml`.
- Never create a branch or open a PR — the sweep lands on `main` (PRD §18).
- Never fetch outside the ATS allowlist, including for company research (§4.3).
- Never exceed `queue_cap` — raise the threshold for this run and say so.

The shortlist on `main` plus the report is the deliverable: the morning's job
search, done. The human reads it over coffee, then runs `/choose` in a fresh
session (Gate 1: which of these is worth tailoring?) and `/tailor` for the
keeps.
