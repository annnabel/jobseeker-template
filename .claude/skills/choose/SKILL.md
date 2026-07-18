---
name: choose
description: Gate 1. Run in a fresh session on main after a sweep. Pulls up the shortlist queue cheaply (meta.yaml only, no JDs unless asked), the human picks keeps, and the picks are committed — discards deleted, keeps marked. Then the human runs /tailor. Never tailors, never submits.
---

# /choose — Gate 1, pick the keeps (PRD §18)

The sweep ended with a shortlist on `main`. This session answers one question —
**"which of these is worth tailoring?"** — as cheaply as possible, then records
the answer in the repo so `/tailor` (a different session) can act on it without
re-asking. The repo is the database; a pick that isn't committed didn't happen.

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

- **Empty shortlist** → say "nothing to choose — the queue is empty" and
  point at `/next`. Stop.
- Entries already `status: kept` (a prior `/choose` that wasn't tailored yet)
  → list them separately as "already kept, awaiting /tailor"; don't re-ask.

## Step 2 — present the queue

One block per role, compact enough to skim on a phone: company, title,
location, triage score + reason, red flags, keywords, referral match, and
`[GAP] No company note` where the note is missing. Number the blocks so the
human can answer "keep 1 and 3, kill the rest".

If the human asks for more detail on a specific role ("show me the JD for
the Torrens one"), *then* read that one `jd.md` — on request only, one at a
time. Answer questions about a role **only** from its `jd.md` and
`profile/companies/<slug>.md` if present — never from memory or priors
(red line 6). No web research here; that happens in `/tailor` (PRD §16).

## Step 3 — get the decision

Ask once, with the list in front of them: *"Which of these should I keep for
tailoring? The rest get discarded — they're already in seen-state and will
never come back."*

- Keeps and discards must together cover the queue; if the human names only
  keeps, confirm the rest are discards.
- "Discard all" is a valid outcome.
- Do not recommend, rank beyond triage's score, or nudge. The pick is the
  human's — that is what makes this a gate.

## Step 4 — commit the picks

For every **discard**: delete `queue/shortlist/<slug>/`. It is already in
`state/seen/` (disposition `shortlisted`), so it can never come back. No new
seen-state is written — discarding a shortlist entry is not a new disposition
(PRD §15.7).

For every **keep**: in `queue/shortlist/<slug>/meta.yaml`, set
`status: kept`. Touch nothing else in the file — `fingerprint:`, `swept:`,
and the triage block must survive verbatim (`seen.py audit` needs them).

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
- Never write seen-state — discards are already seen.
- Never modify `profile/resume.yaml` or `profile/config.yaml`.
