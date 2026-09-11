---
name: log
description: Record a status change in about two minutes. "I applied to X" moves the draft to applied/; "X replied / screen / onsite / offer / rejected" bumps its status. Regenerates the tracker. Never hand-edit tracker.csv.
---

# /log — status updates

The tracker is derived, never maintained. You edit a role's `meta.yaml` and
regenerate. Silence needs no input: an application quiet past
`tracker.ghost_days` is marked ghosted automatically.

## "I applied to <role>"

The human submitted in their own browser. Promote the draft:

- `git mv queue/ready/<slug>/ applied/<YYYY-MM-DD>_<slug>/`
- In its `meta.yaml` set `status: applied` and `applied: <today>` (and
  `date:` if unset).
- Mention once: if it stays silent past `tracker.followup_days` (default 7)
  the tracker will nudge them to send a short follow-up, theirs to write.

## "<role> → <event>"

Set `status:` in the role's `meta.yaml` to one of `reply`, `screen`,
`onsite`, `offer`, `rejected`, `withdrawn`. On `reply`, `screen` or `onsite`,
mention once that `/prep` builds interview prep for it.

## Always, after any change

```
python3 bin/tracker.py
python3 bin/save.py "log: <role> -> <status>"
```

Don't narrate the saving. One line back: the new status and the next thing.

## Never
- Never hand-edit `tracker.csv`.
- Never invent a status the human didn't report.
