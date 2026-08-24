---
name: prep
description: Interview prep for one role that got a real event (reply, screen, onsite). Builds likely questions, STAR stories, and honest shortfall answers from the evidence bank — grounded in what the submitted draft actually claimed. Interactive only; never runs in a sweep. Never coaches overstating.
---

# /prep — interview prep, grounded (PRD §24; the loop §2 deferred)

An interview is the one event where a stretched claim stops being Gate 2's
problem and becomes the candidate's, live, in the room. So `/prep` has one
governing rule: **prepare the candidate to defend what they actually said,
never to say more.** The submitted variant and cover are the script the
interviewer read; the evidence bank is what's true; prep is the bridge, and
it only bridges downward from claims to proof — never upward from proof to
new claims.

Interactive only. This never runs in the sweep or any unattended path
(PRD §2 stands: it is not part of that loop). All red lines hold —
especially: never fabricate, never assert an unbacked company fact, never
present an estimate as a fact.

## Step 1 — pick the role

The human names it, or read `tracker.csv` (regenerate first) and offer the
roles whose status is `reply`, `screen`, or `onsite`. Work from that role's
directory — usually `applied/<date>_<slug>/`, sometimes still
`queue/ready/<slug>/`. Read, from there and from `profile/`:

- `jd.md` — what they asked for.
- `variant.yaml` + `cover.md` — **what was submitted.** This is what the
  interviewer will probe. Note the `angle:` (or `label:`) it was positioned
  on.
- The evidence-bank entries the variant's `ev:` IDs cite — their `narrative`
  fields are the raw material for stories, their `confidence` governs what
  may be said as a number out loud (same rules as on paper: `measured` may be
  stated as fact; `estimated` only directionally; `qualitative` with no
  numeral at all).
- `profile/goals.yaml` — the track this role serves. On a `pivot` track,
  expect the pivot itself to be probed: the `transferable` list is the
  honest answer, the `known_gaps` are the questions to expect.
- `profile/companies/<slug>.md` — the note, if present.
- The bank's `## Shortfalls`, and any `[SHORTFALL]` in the draft's record.

## Step 2 — research, through the note (PRD §16)

Interactive session, human present: public-web research on the company is
allowed and useful (recent news, the product, the team's public work). The
§16 mechanics are unchanged — findings go into
`profile/companies/<slug>.md` under a `## Researched <YYYY-MM-DD>` heading,
**one source URL per fact, before use**; the human's own lines are never
edited. Red line 4 has no exceptions: nothing behind auth, never LinkedIn or
Indeed. A claim you can't pin to a fetched page goes nowhere.

## Step 3 — build `prep.md` in the role's directory

Four sections, every line grounded:

1. **Likely questions** — derived from the JD's requirements and from the
   submitted draft's own claims (an interviewer probes the resume in front
   of them). For each: the `ev:` entries that answer it — or, where the
   honest answer is a gap, say so here and prep it in section 3. Cite
   evidence IDs in this file (it is internal, like the variant; IDs never
   reach the interviewer).

2. **STAR stories** — one per leading claim, built from the cited entries'
   `narrative` fields, starting with the angle's `proof` entries. Situation,
   task, action, result — where the result's entry is `estimated` or
   `qualitative`, write the result the way the confidence rules allow it to
   be *spoken*, so the rehearsed sentence is the compliant one. A thin
   narrative is a **`[GAP]`**: ask the human the specific question now,
   write the answer back to the entry in `profile/evidence-bank.md` (enrich,
   never delete — red line 11), and build the story from the enriched entry.

3. **Shortfalls, said plainly** — for each `[SHORTFALL]` the role touches
   (including a pivot track's `known_gaps`): a direct acknowledgment in the
   candidate's own register, plus the *adjacent real evidence* worth
   volunteering right after it. Never a script for talking around the gap.
   The honest version is also the strategically better one: interviewers
   probe evasions.

4. **Questions to ask them** — drawn from the JD and the company note
   (including researched facts with their sources) only. Specific beats
   generic here for exactly the reason it does in the cover.

Style: `voice.md` governs; the banned-style list applies to prose you write
here as much as to a cover — the human may read these lines aloud.

## Step 4 — walk it live, then commit

Walk the questions and stories with the human, in the session — this is a
rehearsal, and their edits in their own words beat your phrasing. Then:

```
git add applied/ queue/ profile/evidence-bank.md profile/companies/
git commit -m "prep: <company> · <role>"
git push origin main
```

The repo is the database: a prep the human can reread on their phone outside
the interview room is the deliverable. Close by naming the interview's
logged next step (`/log` records how it went: `screen`, `onsite`, `offer`,
`rejected`).

## Never

- Never run in the sweep or any unattended session — human present, always.
- Never build a story a cited `ev:` doesn't support, and never coach the
  candidate to state more than the entry holds. A rehearsed stretch is worse
  than a written one: they will be asked the follow-up question.
- Never state a number `confidence` doesn't license — spoken claims follow
  the same rules as printed ones.
- Never assert a company fact that isn't in the JD or the company note
  (researched facts enter the note first, with sources — PRD §16).
- Never fetch anything behind auth. Paste-only for anything off the public
  web.
- Never contact the employer, schedule anything, or submit anything.
- Never edit `profile/goals.yaml`, `resume.yaml`, or `config.yaml`. Bank
  write-backs are Gate-2-style answers to `[GAP]`s only.
