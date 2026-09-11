---
name: next
description: Answers "what should I do now?" Reads the queue, drafts, tracker and goals, and gives one prioritised next action plus a short list of everything else pending. Changes nothing except regenerating the tracker.
---

# /next — where am I, what do I do

Read the state, name the single next action, list the rest. A glance, not a
report. Change nothing (regenerating `tracker.csv` is allowed; it's derived).
`git pull -q origin main` first.

## Read, in order

0. **Set up at all?** No `profile/goals.yaml` → the action is `/setup`. Goals
   but no `profile/evidence-bank.md` → `/setup` to continue the interview.
0b. **Bank holds together?** `python3 bin/validate.py --lint-bank`. A failure
   is a top-three action; the fix is a short pass over `## Angles` in
   `/setup`, not a rewrite.
1. **Drafts awaiting a hand submit**: `queue/ready/*/meta.yaml`. Sort by
   `closes:` if present; a role closing soon is always the top action.
2. **Roles waiting for a yes**: `queue/shortlist/*/meta.yaml`. The action is
   `/apply` with nothing pasted.
3. **The tracker**: `python3 bin/tracker.py`, then read `tracker.csv`. A
   `send a follow-up` row is a top-three action (a short check-in the human
   sends in their own words). A `reply`, `screen` or `onsite` with no
   `prep.md` in its directory is a `/prep` action, and an upcoming interview
   outranks everything else here. When asked how the search is going, or once
   ten or so applications exist, run `python3 bin/tracker.py --stats` and
   relay the rates by track and angle. Report; never suggest retuning
   `goals.yaml` or the bank.
4. **Track health**: compare `track:` values across recent queue and applied
   entries against `profile/goals.yaml`. A track that has produced nothing
   gets one line. Report it; never edit the file.
5. **Sweep, only if on**: `profile/targets.yaml` present with companies but
   no sweep has ever landed (`state/seen/` empty) → one line pointing at
   `optional/sweep/README.md`. If `targets.yaml` is absent, say nothing about
   the sweep; paste-driven is the normal state.

## Output shape

```
NEXT: <the one thing to do now, with the exact command>

Also pending:
- <item> — <why / by when>

Quiet: <one line on what needs nothing>
```

If truly nothing is pending, say so and suggest the one thing that would make
tomorrow better (usually: `/apply` with a posting they've been sitting on).
