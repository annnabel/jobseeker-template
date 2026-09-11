---
name: apply
description: Paste in a job ad. Honest fit read, then, if the human says yes, a tailored resume and cover letter walked through line by line. Run with nothing pasted to see what's waiting. Never submits.
---

# /apply — one role, start to draft

You are running with the human present. Be brief between steps; the draft
walkthrough is where the time goes. Never mention git, branches or commits to
the human; just save.

## 0 — load

`git pull -q origin main`. If `profile/goals.yaml` or
`profile/evidence-bank.md` is missing, stop: *"Run `/setup` first; nothing
knows what you're looking for yet."*

## 1 — intake

- **Text pasted** → use it as is.
- **A URL** on a public job board (Greenhouse, Lever, Ashby, Workable,
  SmartRecruiters, or the employer's own careers site) → fetch it. LinkedIn,
  Indeed, Seek, Glassdoor, or anything that needs a login → do not fetch; ask
  for the text pasted in.
- **Nothing pasted** → list what's waiting in `queue/shortlist/*/meta.yaml`
  (read only the meta files, never the JDs unless asked). Numbered blocks:
  company, title, location, score and reason, red flags, keywords, and
  `status: near_miss` entries under their own heading marked as below the
  sweep's bar. Ask which to draft. "None" is fine. Then continue from step 3
  with the chosen ones. Empty queue → say so, point at pasting an ad.

## 2 — fit read

Invoke the `triage` subagent with the JD text, company, title and location.
Show its verdict as it came back: score, the track it serves, reason, red
flags, plus any `## Shortfalls` from the bank the JD touches. Say in one line
what you'd tailor against and what's missing. If `track: none`, say the role
matches no track in their goals and that pursuing it anyway is their call.
Do not recommend.

## 3 — the human's call

Ask once: *"Draft this now, save it for later, or drop it?"*

- **Later** → write `queue/shortlist/<slug>/jd.md` (company, title,
  location, apply URL, source, full JD text) and `meta.yaml`:
  ```yaml
  company:
  title:
  location:
  url:
  source: manual
  status: shortlisted
  added: <YYYY-MM-DD>
  track:
  triage: {score:, reason:, red_flags: []}
  keywords: []       # the posting's top five repeated terms
  referral:          # matching name from profile/connections.csv, else none
  company_note:      # present | missing
  ```
  Save (step 6) and stop with one line.
- **Drop** → save nothing (delete the queue directory if it was one). Stop.
- **Now** → continue. A queued entry already has these files; leave any field
  in its `meta.yaml` you don't recognise (`fingerprint:`, `swept:`) untouched.

Never draft a role the human has not said yes to.

## 4 — draft

Invoke the `tailor` subagent with the JD text and the meta. It writes
`queue/ready/<slug>/`: `resume.yaml`, `resume.md`, `cover.md`, `jd.md`,
`meta.yaml` (the intake meta carried forward unchanged, `status: queued`),
researches the company on the public web into `profile/companies/<slug>.md`
with source URLs, self-validates, and runs the keyword scorecard. Markdown
only, no PDF. Then delete `queue/shortlist/<slug>/` if it existed.

If the tailor reports the draft can't pass validation honestly, say so and
show the `[SHORTFALL]`s. Do not ship it, do not paper over it.

## 5 — walk it through, now

Show `resume.md`, `cover.md`, the scorecard, and the tailor's changes-made
list. Read the top third with the human first: headline, summary, the skills
lines. If the first skills category isn't the one the angle rests on, fix that
before touching bullets.

- Show the scorecard as the script produced it, required tier first, every
  miss with its verdict. Say plainly which misses are `[SHORTFALL]`s.
- Ask each `[GAP]`. Write the answer into `profile/evidence-bank.md` as a
  proper entry (tags, scope, confidence, source, narrative), then re-tailor
  the affected bullet.
- Read the `[SHORTFALL]`s aloud. Append new ones to `## Shortfalls`.
- Apply the human's edits. Then re-run:
  ```
  python3 bin/validate.py queue/ready/<slug>/resume.yaml
  python3 bin/validate.py --cover queue/ready/<slug>/cover.md --variant queue/ready/<slug>/resume.yaml [--note profile/companies/<slug>.md]
  python3 bin/render.py queue/ready/<slug>/resume.yaml -o queue/ready/<slug>/resume.md
  python3 bin/ats_score.py --jd queue/ready/<slug>/jd.md --variant queue/ready/<slug>/resume.yaml --cover queue/ready/<slug>/cover.md
  ```
  Quote the new coverage number, never the old one.

If the human wants to stop early, save what exists and tell them `/apply`
with nothing pasted brings it back up.

## 6 — save and hand back

```
python3 bin/tracker.py
python3 bin/save.py "apply: <company> · <title>"
```

Close with the tailor's report for the role (angle and its proof entries,
scorecard, changes made, `[GAP]`s and their answers, `[SHORTFALL]`s, research
added, three things only the human can do to strengthen it), then one line:
*"Apply by hand from `queue/ready/<slug>/`, then run `/log`."*

## Never

- Never submit, never navigate to a submit button, never POST to an ATS.
- Never fetch LinkedIn, Indeed, or anything behind a login.
- Never pick, drop or rank roles for the human.
- Never edit `profile/goals.yaml`, `resume.yaml` or `config.yaml`.
- Never report a coverage number the script didn't produce.
