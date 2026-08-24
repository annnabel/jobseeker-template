---
name: choose
description: Gate 1. Run in a fresh session on main. Pulls up the queue cheaply (meta.yaml only, no JDs unless asked) — roles you added with /add and, if the sweep is on, its shortlist — the human picks keeps, and the picks are committed. Then the human runs /tailor. Never tailors, never submits.
---

# /choose — Gate 1, pick the keeps (PRD §18, §22)

The queue on `main` holds every role that's been found and not yet decided:
roles the human pasted in with `/add`, and — if the optional sweep is on —
its shortlist. This session answers one question — **"which of these is worth
tailoring?"** — as cheaply as possible, then records the answer in the repo so
`/tailor` (a different session) can act on it without re-asking. The repo is
the database; a pick that isn't committed didn't happen.

This session is deliberately small. Do not tailor, do not research companies,
do not fetch anything. The whole point of `/choose` being its own session is
that picking keeps should not spend the context window that tailoring needs.

## Step 1 — load the queue, cheaply

```
git checkout main && git pull origin main
```

Read **only** `queue/shortlist/*/meta.yaml` — never the `jd.md` files. The
meta has everything a pick needs: triage score, reason, red flags, top-5 JD
keywords, referral match, company-note presence.

Sort the entries into four groups — `/add` writes `source: manual`, the sweep
writes a `status:`, and the groups are not interchangeable:

- **`source: manual`** — roles the human found and pasted in with `/add`,
  whatever their score. Their queue, their finds; the threshold never applied.
- **`status: shortlisted`** (and not manual) — sweep survivors, scored at or
  above the threshold. The sweep's pick list.
- **`status: near_miss`** — scored *below* the threshold, surfaced by the
  sweep only so a thin night isn't silent (PRD §15). Each carries a
  `miss_reason:` line — the one thing that kept it under the bar. These are
  **not** the sweep's recommendations; they exist for you to overrule the
  threshold if you want to, nothing more.
- **`status: kept`** — a prior pick already kept these and `/tailor` hasn't
  run yet. List them separately as "already kept, awaiting /tailor"; don't
  re-ask.

- **Empty queue** (no entries at all) → say "nothing to choose — the queue
  is empty" and point at `/next`. Stop.

## Step 2 — present the queue

Present the groups **separately and labelled**, so a below-threshold role is
never mistaken for a survivor and the human's own finds are never mistaken for
the sweep's.

First, **Added by you (via /add)** — the `source: manual` entries, if any.
One block per role, compact enough to skim on a phone: company, title,
location, triage score + reason, red flags, keywords, referral match, and
`[GAP] No company note` where the note is missing.

Then, **Shortlist (met the bar)** — the sweep's `status: shortlisted`
entries, sub-grouped by their `track:` under each track's `label` from
`profile/goals.yaml`, in track order. Same fields per block. Entries with
`track: none` (or written before goals existed) go last, under "No track". If
`profile/goals.yaml` is absent, skip the grouping entirely and present one
flat list.

Then, only if any exist, **Closest misses (below the bar)** — the
`status: near_miss` entries, in their own clearly-headed section. Same fields,
plus the `miss_reason:` line, and say plainly these scored *below* the
threshold and are surfaced only so you can judge them — the sweep is not
recommending them. If there are none, omit the section entirely. Omit any
empty group.

Number every block across all sections so the human can answer "keep 1 and 3,
kill the rest" — a near miss is picked exactly the same way a survivor is; the
label just tells the human what they're overruling.

If the human asks for more detail on a specific role ("show me the JD for
the Torrens one"), *then* read that one `jd.md` — on request only, one at a
time. Answer questions about a role **only** from its `jd.md` and
`profile/companies/<slug>.md` if present — never from memory or priors
(red line 6). No web research here; that happens in `/tailor` (PRD §16).

## Step 3 — get the decision

Ask once, with the list in front of them: *"Which of these should I keep for
tailoring? The rest get discarded — say 'hold' on one to leave it queued for
next time."*

- Every entry ends up keep, discard, or (named explicitly) held. If the human
  names only keeps, confirm the rest are discards.
- "Discard all" is a valid outcome.
- Do not recommend, rank beyond triage's score, or nudge. The pick is the
  human's — that is what makes this a gate.

## Step 4 — commit the picks

For every **discard**: delete `queue/shortlist/<slug>/`. A swept role is
already in `state/seen/`, so it can never come back; a manual role has no seen
record, so `/add`-ing it again later is possible and fine — discarding it here
just clears the queue. No new seen-state is written — discarding a queue entry
is not a new disposition (PRD §15.7).

For every **keep**: in `queue/shortlist/<slug>/meta.yaml`, set
`status: kept`. Touch nothing else in the file — on swept entries,
`fingerprint:`, `swept:`, and the triage block must survive verbatim
(`seen.py audit` needs them).

A **held** entry is left exactly as it is.

Then make it durable:

```
git add queue/shortlist/
git commit -m "choose: <n> kept, <m> discarded"
git push origin main
```

If the push is rejected, `git pull --rebase origin main` and push again.

## Step 5 — hand off

Close with one line: *"<n> kept. Open a fresh session and run /tailor — it
will develop everything marked kept."* If the pick was discard-all, say the
queue is clear and point at `/next`.

## Never
- Never tailor, and never invoke the `tailor` subagent — that is `/tailor`'s
  spend, in its own session (PRD §15).
- Never submit an application or navigate to a submit button.
- Never fetch the web — no company research here (PRD §16 puts it in
  `/tailor` and `/add`).
- Never keep or discard a role the human didn't name — no picks without the
  human, no defaults, no "I went ahead and".
- Never write seen-state — swept discards are already seen, and manual finds
  never are.
- Never modify `profile/resume.yaml`, `profile/config.yaml`, or
  `profile/goals.yaml`. If a whole track keeps arriving empty or wrong, say so
  in one line at hand-off ("nothing on the *career-changer* track for three
  sweeps — its `titles` may be too narrow") and leave the edit to them. Their
  career goals are not yours to adjust.
