# The sweep — unattended procedure

You are running with **no human in the loop**. Be precise. `CLAUDE.md` applies
in full, and these hold above all: never draft, never pick, never submit,
never fetch outside the job-board hosts, never edit `profile/goals.yaml`,
`resume.yaml` or `config.yaml`, never create a branch or pull request. The
run ends at a shortlist on `main` plus a report.

If `profile/targets.yaml` is absent or lists no companies, the sweep is off:
say so and stop.

**Full coverage, every run.** Fetch every board in `targets.yaml` and triage
every posting that survives fetch. The only narrowing is what the human
configured: the location filter, the optional `role_filter`, the 30-day
freshness cut, seen-state dedupe, and the threshold. Never subset boards or
skip postings by title, keyword or seniority to save effort.

## Order of operations

0. **Audit** — `python3 optional/sweep/bin/seen.py audit`. A `MISS` means a
   previously queued role has no seen record and would be re-triaged; repair
   as the output says, then continue. An empty index is normal only on the
   first run.

1. **Fetch** — `python3 optional/sweep/bin/fetch.py --source all`. Writes new
   postings to `queue/raw/`. One dead adapter logs a warning and the run
   continues; note it for the report. Exit **non-zero** (every adapter
   failed) → the environment is broken: **abort and say so.** Carry any
   `role_filter dropped N` line into the report.

2. **Triage** — invoke the `triage` subagent once per posting in `queue/raw/`,
   none skipped. Order by likely fit (postings whose title matches a track's
   `titles` in `goals.yaml` first, in track order) but score all. Using
   `config.scoring` (defaults: threshold 70, queue_cap 6, near_miss_band 15,
   near_miss_cap 4), band each posting: **survivor** (score ≥ threshold),
   **near miss** (within `near_miss_band` below it), **killed** (the rest).

3. **Cap** — more than `queue_cap` survivors → raise the threshold **for this
   run only** until it fits; record the raised value and what it cost. The
   near-miss window follows the effective threshold. Keep at most
   `near_miss_cap` near misses by score; kill the rest. Near misses never
   count toward `queue_cap` and never become survivors.

4. **Shortlist** — for each survivor and near miss write
   `queue/shortlist/<slug>/jd.md` (company, title, location, apply URL,
   source ATS, full JD text) and `meta.yaml`:
   ```yaml
   company:
   title:
   location:
   url:
   source:            # greenhouse | lever | ashby | workable | smartrecruiters | recruitee | workday | oracle | pageup | teamtailor
   fingerprint:       # VERBATIM from the raw posting JSON; the seen-state identity
   status: shortlisted   # near misses: near_miss
   swept: <YYYY-MM-DD>
   track:             # from triage, or none
   triage:
     score:
     reason:
     red_flags: []
     miss_reason:     # near misses only: the one line that kept it under the bar
   keywords: []       # the posting's top five repeated terms
   referral:          # matching name in profile/connections.csv, else none
   company_note:      # present | missing
   ```
   No resume, no cover. Zero survivors is valid; zero of both means skip
   step 5, still do step 6.

5. **Commit the shortlist first**
   ```
   git add queue/shortlist/
   git commit -m "sweep: shortlist $(date +%F) · <n> roles"
   git push origin main || (git pull --rebase origin main && git push origin main)
   ```
   The shortlist must reach the remote **before** anything is marked seen. A
   crash after this push costs a duplicate triage; the reverse order loses
   roles silently.

6. **Seen-state, its own commit**
   ```
   python3 optional/sweep/bin/seen.py mark --disposition killed      <each killed raw .json>
   python3 optional/sweep/bin/seen.py mark --disposition shortlisted <each surviving raw .json>
   python3 optional/sweep/bin/seen.py mark --disposition near_miss   <each near-miss raw .json>
   python3 optional/sweep/bin/seen.py audit --date $(date +%F)       # must print OK
   ```
   Then delete the processed files from `queue/raw/` and:
   ```
   git add state/seen/ && git commit -m "sweep: seen-state $(date +%F)"
   git push origin main || (git pull --rebase origin main && git push origin main)
   ```

7. **Report** — this is what the human reads in the morning:
   - Shortlist, grouped by track in `goals.yaml` order under each track's
     `label`: company, title, location, score and reason, red flags, top
     keywords, referral match, and `[GAP] no company note` where missing. An
     empty track gets one line saying so.
   - Closest misses, if any, each with its `miss_reason`, labelled as below
     the bar and not a recommendation.
   - "swept N, shortlisted X, near misses Y (threshold T)"; boards that
     failed; the `role_filter` drop count; a raised threshold and what it
     cost.
   - One closing line: *"Run /apply with nothing pasted to pick which to
     draft."* Nothing else.
