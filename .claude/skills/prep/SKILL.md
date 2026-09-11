---
name: prep
description: Interview prep for one role that got a reply, screen or onsite. Likely questions, STAR stories, and honest shortfall answers from the evidence bank, grounded in what the submitted draft actually claimed. Never coaches overstating.
---

# /prep — interview prep, grounded

One governing rule: **prepare the candidate to defend what they actually
said, never to say more.** The submitted resume and cover are the script the
interviewer read; the evidence bank is what's true; prep bridges from claims
down to proof, never from proof up to new claims.

`git pull -q origin main` first.

## 1 — pick the role

The human names it, or regenerate the tracker and offer the roles at `reply`,
`screen` or `onsite`. From its directory (`applied/<date>_<slug>/`, or
`queue/ready/<slug>/`) and `profile/`, read:

- `jd.md`: what they asked for.
- `resume.yaml` + `cover.md`: **what was submitted.** Note the `angle:`.
- The bank entries the draft's `ev:` IDs cite: their `narrative` is the story
  material; their `confidence` governs what may be said as a number out loud
  (same rules as on paper).
- `profile/goals.yaml`: the track. On a `pivot`, expect the pivot to be
  probed: `transferable` is the honest answer, `known_gaps` the questions.
- `profile/companies/<slug>.md` if present, and the bank's `## Shortfalls`.

## 2 — research, through the note

Public-web research on the company is allowed and useful. Findings go into
`profile/companies/<slug>.md` under `## Researched <YYYY-MM-DD>`, one source
URL per fact, before use. Never edit the human's own lines. Nothing behind a
login, never LinkedIn or Indeed. A claim you can't pin to a fetched page goes
nowhere.

## 3 — build `prep.md` in the role's directory

1. **Likely questions**, from the JD's requirements and the draft's own
   claims. For each, the `ev:` entries that answer it, or "gap, see section
   3".
2. **STAR stories**, one per leading claim, starting with the angle's proof
   entries, built from `narrative` fields. Where the result is `estimated` or
   `qualitative`, write the rehearsed sentence the way it may be *spoken*. A
   thin narrative is a `[GAP]`: ask now, write the answer back to the entry
   (enrich, never delete), build from the enriched entry.
3. **Shortfalls, said plainly**: for each `[SHORTFALL]` the role touches
   (including a pivot's `known_gaps`), a direct acknowledgment in their own
   register plus the adjacent real evidence worth volunteering right after.
   Never a script for talking around it; interviewers probe evasions.
4. **Questions to ask them**, from the JD and the company note only.

`voice.md` governs the style; the banned-style list applies here too, since
they may read these lines aloud.

## 4 — walk it live, then save

Rehearse the questions and stories with the human; their edits in their own
words beat your phrasing. Then:

```
git add -A && git commit -q -m "prep: <company> · <title>" && git push -q origin main \
  || (git pull -q --rebase origin main && git push -q origin main)
```

Close by naming what `/log` records after the interview (`screen`, `onsite`,
`offer`, `rejected`).

## Never
- Never build a story a cited entry doesn't support, or coach a claim the
  entry doesn't hold. A rehearsed stretch gets the follow-up question.
- Never state a number the entry's `confidence` doesn't license.
- Never assert a company fact that isn't in the JD or the note.
- Never contact the employer, schedule anything, or submit anything.
- Never edit `goals.yaml`, `resume.yaml` or `config.yaml`.
