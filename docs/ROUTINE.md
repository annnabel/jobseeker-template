# The routine (paste-in) — PRD §9, §18

**Only needed for the optional nightly sweep.** If you haven't switched the
sweep on (`/setup` asks; PRD §22), skip this file entirely.

Create at **claude.ai/code/routines → New Routine**. Attach your private
`my-jobseeker` repo and the environment you configured in `docs/ENVIRONMENT.md`.

- **Trigger:** Scheduled → Weekdays → 06:00 local. Runs may start a few minutes
  late due to stagger; the offset is consistent.
- Minimum interval is one hour. Custom cron needs the CLI, so stick to presets —
  and "weekdays at 6am" is a preset.

> The prompt below is deliberately minimal: the **`/sweep` skill in the repo
> is the authoritative procedure**, and because your instance clones the repo
> fresh on every run, improvements to the skill reach the routine with no
> re-pasting. The prompt carries only the invariants that never change — so
> once pasted, it should rarely if ever need re-pasting. (Editing this file
> does **not** update an already-created routine at claude.ai; if the prompt
> text below ever does change, open the routine and re-paste.)

## Routine prompt (paste verbatim)

```
Run /sweep and follow that skill exactly — it is the authoritative
procedure (fetch, triage, near-miss tier, cap, shortlist to main,
seen-state, morning report). Work on main the whole run.

Invariants, restated as defense in depth (the skill and CLAUDE.md
carry the full list):
- The sweep stops at a shortlist. Do NOT tailor, do NOT invoke the
  tailor subagent, and do NOT pick or discard anything — the human
  picks via /choose later.
- The shortlist commit must be pushed BEFORE anything is marked seen.
- If fetch exits non-zero (every adapter failed), abort and say so —
  never report a broken environment as a quiet night.
- Never submit an application; never fetch outside the ATS allowlist;
  never modify profile/resume.yaml, config.yaml, or goals.yaml; never
  create a branch, open a PR, or merge anything.
- More than config.scoring.queue_cap survivors: raise the threshold
  for THIS RUN ONLY, never write it to config.yaml, and report it.

End the run with the /sweep skill's morning report — that report is
what I read over coffee. Nothing else: no drafts, no interview prep.
```

## Notes

- **Threshold is per-run.** If "raise the bar" wrote to `config.yaml`, the
  unattended routine would edit its own config nightly and ratchet away the
  threshold you calibrated in Phase 5 — and never ratchet back. Per-run,
  reported in the run's report. See the same override three mornings running?
  Then *you* change the config.

- **Limits.** Routines have daily limits (check the current number in the UI).
  One sweep a day is comfortably inside it. Rate-limit draw is shared with your
  coding work: one cheap Haiku triage call per fresh posting — a handful, once
  the backlog is behind you — and **zero** Opus runs per sweep (PRD §15). The
  expensive tailoring spend happens only when you run `/tailor` on the roles
  you chose to keep.

- **After the sweep.** The shortlist is on `main` and the run's report is the
  job search's output: scores, reasons, and keywords. Read it, then open a
  **fresh session** and run `/choose` (Gate 1: which are worth tailoring? —
  it reads only the shortlist metadata, so the pick costs almost nothing),
  then another fresh session for `/tailor`, which develops everything you
  marked kept. Discards never come back — they're already in seen-state.

- **Day one is not steady-state.** The first sweep triages your entire backlog
  (100+ postings). Run it **manually**, on a day you're not working.
