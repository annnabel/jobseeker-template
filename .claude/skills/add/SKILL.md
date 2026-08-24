---
name: add
description: Paste in a job description you found yourself (LinkedIn, a friend, anywhere). Saves it to the queue with an honest fit read. You pick your keeps with /choose; /tailor drafts the picks. Never submits.
---

# /add — paste-in intake (PRD §14, §22)

The human found a posting themselves. `/add` is **intake only**: save the JD,
read the fit honestly, queue the role. Picking is `/choose`'s job (Gate 1) and
drafting is `/tailor`'s — the same gates every role goes through, whether the
human pasted it in or the optional sweep found it. One queue, one path.

Work on `main` (`git pull origin main` first). No branch, no PR. The red lines
in `CLAUDE.md` hold in full — especially: never submit, never fetch
off-allowlist, never invent.

## Step 1 — get the JD text

- Pasted text: use it as-is.
- A URL on an allowlisted ATS host (Greenhouse/Lever/Ashby/Workable/
  SmartRecruiters): you may fetch it.
- Any other URL (LinkedIn, a company careers page): **do not fetch**. Ask the
  human to paste the JD text. Their own copy of a posting is their notes, which
  is allowed; you fetching it is not.

## Step 2 — fit read

Invoke the `triage` subagent on the JD (score, reason, red_flags, track), then
show the human the score, the track it serves, plus any relevant
`## Shortfalls` from the evidence bank. Say what you'd tailor against and
what's missing. The threshold in `config.yaml` does **not** auto-kill here —
the human found this role, and whether to pursue it is their pick at `/choose`.

If triage returns `track: none`, say so plainly and neutrally — *"this doesn't
match any track in your goals.yaml; that's fine if you're widening the net, and
worth an edit to goals.yaml if you're changing direction"* — then queue it
anyway. A role off their stated goals is their call, not a reason to
discourage them.

## Step 3 — queue it

Write `queue/shortlist/<slug>/`, the same shape the sweep writes (PRD §18):

- `jd.md` — company, title, location, apply URL if known, source
  ("manual — pasted by the user"), and the full JD text. Everything `/tailor`
  will need; it must not have to re-fetch.
- `meta.yaml`:
  ```yaml
  company:
  title:
  location:
  url:               # if known
  source: manual     # what exempts this entry from the seen-state audit —
                     # manual finds were never fetched, so seen-state
                     # doesn't apply to them (bin/seen.py)
  status: shortlisted
  added: <YYYY-MM-DD>
  track:             # from triage's verdict; "none" if it serves no track
  triage:
    score:
    reason:
    red_flags: []
  keywords: []       # top-5 ATS keywords from the JD, for the /choose skim
  referral:          # matching name from connections.csv, else "none"
  company_note:      # present | missing (profile/companies/<slug>.md)
  ```
  No `fingerprint:`, no `swept:` — those are the sweep's dedupe bookkeeping.

Commit to `main` and push (`add: <company> · <role>`; if the push is rejected,
`git pull --rebase origin main` and push again). The repo is the database — a
role that isn't committed didn't happen.

## Step 4 — hand back

One line: *"Queued. `/add` more roles any time; run `/choose` when you want to
pick which get tailored, then `/tailor` drafts the keeps."*

If the human wants the draft right now, don't make them wait on ceremony: a
one-role `/choose` is a single question. Ask it — *"keep this one for
tailoring?"* — record the answer exactly as `/choose` would
(`status: kept`, committed), and point them at `/tailor` in a fresh session.
What you never do is skip the pick: tailoring an unpicked role opens Gate 1
yourself (red line 10).

## Never
- Never submit an application or navigate to a submit button.
- Never fetch LinkedIn, Indeed, or anything behind auth — paste only.
- Never tailor here, and never invoke the `tailor` subagent — that is
  `/tailor`'s spend, in its own session (PRD §15).
- Never discard, hold, or pass on a role yourself — every pasted role is
  queued; the pick is the human's, at `/choose`.
- Never write seen-state for a manual find — it was never fetched.
