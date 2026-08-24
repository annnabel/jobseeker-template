---
name: next
description: Answers "what should I do now?" Reads the repo state (queue, drafts, tracker, targets) and gives one prioritized, concrete next action plus a short list of everything else pending. Changes nothing except regenerating the derived tracker.
---

# /next — where am I, what do I do (PRD §14)

The user should never have to remember how this system works. Read the state,
tell them the single next action, list the rest. Be brief: this is a glance,
not a report. Change nothing (regenerating `tracker.csv` is allowed — it's
derived, not a decision).

## Read, in order

0. **Is the system set up at all?** If `profile/goals.yaml` is missing, that is
   the top action, ahead of everything below: *"Run `/setup` — without
   `profile/goals.yaml` nothing knows what job you're looking for, and triage
   falls back to scoring roles by how much they resemble your last one."* If
   `goals.yaml` exists but `profile/evidence-bank.md` doesn't, the action is
   `/setup` to continue the interview.
0b. **Does the bank hold together?** If `profile/evidence-bank.md` exists, run
   `python3 bin/validate.py --lint-bank`. A failure is a top-three action and
   the message says which: an angle nothing proves, an angle with no claim, or
   an entry citing an angle the bank never declared (PRD §21). The fix is a
   short `/setup`-style pass over `## Angles`, not a rewrite — say that.
1. **Drafts awaiting submission** — `queue/ready/*/meta.yaml` on `main` (and
   this branch, if different). Each is a tailored role the human has not
   applied to yet. Sort by `closes:` date; a role closing soon is always the
   top action.
2. **Queued roles awaiting a pick or a tailor** — `queue/shortlist/*/
   meta.yaml` on `main` (pull first). `source: manual` entries (pasted in via
   `/add`), `status: shortlisted` (sweep survivors), and `status: near_miss`
   (below-threshold roles the sweep surfaced for the human to judge) all mean
   nobody has picked yet: the action is `/choose` in a fresh session (Gate 1).
   `status: kept` entries mean the pick happened but `/tailor` hasn't run:
   the action is `/tailor`.
3. **Drafts not yet walked through** — drafts in `queue/ready/` whose Gate 2
   walkthrough was deferred are a `/review` action.
4. **The tracker** — run `python3 bin/tracker.py`, read `tracker.csv`. Surface
   anything with a `next_action` — a `send a follow-up` row (applied, silent
   past `tracker.followup_days`) is a top-three action: a short, polite
   check-in the human sends themselves, in their own words — plus anything
   freshly `ghosted` and any positive status the human may want to act on.
   When the human asks how the search is going (or ~10+ applications have
   accumulated), run `python3 bin/tracker.py --stats` and relay the response
   and callback rates, including the by-track / by-angle breakdown. Report the
   numbers; never suggest retuning `goals.yaml` or the bank yourself.
5. **The sweep, only if it's on** — the sweep is optional (`/setup` offers
   it, PRD §22). If `profile/targets.yaml` is absent or has no companies, the
   system is paste-driven (`/add`) by design — that is not a problem and
   needs no nagging; mention the sweep exists only if the human asks what
   else the system can do. If `targets.yaml` *does* have companies but
   `queue/shortlist/` and `state/seen/` show no sweep has ever landed,
   say so: the routine may not be set up (docs/ROUTINE.md).
6. **Track health** — compare the `track:` values across recent
   `queue/shortlist/` and `applied/` entries against the tracks in
   `profile/goals.yaml`. A track that has produced nothing at all is worth one
   line: its `titles` may be too narrow, or no company in `targets.yaml` hires
   for it. Report it; never edit `goals.yaml` yourself.

## Output shape

```
NEXT: <the one thing to do now, with the exact command or link>

Also pending:
- <item> — <why / by when>
- ...

Quiet: <one line on what needs nothing, e.g. "3 applied roles, none stale">
```

If truly nothing is pending, say so and suggest the one thing that would make
tomorrow better (usually: `/add` a posting they've been sitting on; or, if the
sweep is on, a company added to `targets.yaml`).
