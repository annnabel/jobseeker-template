# Annabel's Jobseeker

**A job-search assistant that runs inside Claude Code.** It finds job postings,
drafts a tailored resume and cover letter for the ones you pick, checks every
claim against facts you provided, and keeps a tracker of where each application
is up to. You review everything, and **you always click "apply" yourself, in
your own browser**.

Created by **Annabel Nguyen**.

---

## What it does

Think of it as a very careful assistant that:

- **Finds roles for you.** Either you paste in a job ad you found anywhere
  (`/add`), or an optional nightly sweep checks the public job boards of
  companies you choose and leaves you a morning shortlist.
- **Drafts for you.** For the roles you pick, it writes a tailored resume and
  cover letter in plain markdown, easy to read on your phone.
- **Never makes things up.** Every claim in every draft must trace back to a
  fact *you* told it during setup. An automated checker blocks drafts that
  invent numbers, employers, or technologies, and even bans AI-sounding
  phrases so letters read like you wrote them.
- **Tracks everything.** A simple spreadsheet (`tracker.csv`) shows every
  application and its status. It updates itself; you never edit it.

## What it will never do

These rules are built in and non-negotiable:

- **Never submits an application.** You apply by hand, every time.
- **Never invents or exaggerates** a metric, job title, date, or skill.
- **Never scrapes** LinkedIn, Indeed, or anything behind a login.
- If it doesn't know something about you, it **asks** instead of guessing.
- If you're missing something a role wants, it **says so plainly** instead of
  papering over it.

## What you need

- A **GitHub account** (free) — your copy of this system lives in a GitHub
  repository.
- **Claude Code** — the easiest way is Claude Code on the web at
  [claude.ai/code](https://claude.ai/code), which needs a paid Claude plan.
  No API keys, no extra costs, nothing to install on your computer.

You do **not** need to know how to code. Everything is driven by typing
simple commands like `/setup` and `/add` into a Claude Code chat.

## Set it up (one time, ~30 minutes plus the interview)

1. **Make your own private copy.** On this repository's GitHub page, click
   **Use this template → Create a new repository**. Name it something like
   `my-jobseeker` and set it to **Private**. Private matters: your copy will
   hold your real career history. (If you don't see the "Use this template"
   button, ask the person who shared this with you to enable it, or fork the
   repo and make your fork private.)
2. **Open it in Claude Code.** Go to [claude.ai/code](https://claude.ai/code)
   and connect your new private repository.
3. **Configure the environment** (only needed for the automated sweep, but
   quick): follow `docs/ENVIRONMENT.md` — it's a copy-paste of a short list of
   allowed websites and a 4-line setup script into the environment settings.
4. **Run `/setup`.** This is the big one: Claude interviews you about your
   career, a few questions at a time, and builds your "evidence bank" — the
   master list of everything true about you that all future resumes draw
   from. Budget a relaxed hour or three; you can stop and pick it up later.
   Honest answers matter more than impressive ones — the system is designed
   so drafts can only use what's in the bank.
5. **Try it.** Find a job ad anywhere, run `/add`, and paste the ad in.
   You'll get an honest fit read, and if you say "go", a tailored draft to
   review right there in the chat.

Lost at any point? Type **`/next`** — it looks at where things stand and
tells you the one best thing to do now.

## The everyday workflow

### When you find a job yourself (most common)

1. **`/add`** — paste the job ad. Claude reads it, scores the fit honestly
   (including what the role wants that you don't have), and asks if you want
   to pursue it.
2. **Review together.** If yes, it drafts the resume and cover letter and
   walks them with you line by line. It will ask you questions where it's
   unsure rather than guess; your answers are saved so it never asks twice.
3. **Apply by hand.** Open the company's site in your browser and submit the
   application yourself, using the approved drafts.
4. **`/log`** — tell it "I applied". The tracker updates itself. Later, when
   you hear back (or don't), one more `/log` line records it. Silence
   eventually auto-marks the role "ghosted" with no effort from you.

### With the automatic sweep turned on (optional)

1. **Add target companies** to `profile/targets.yaml` (the `/setup` interview
   helps with this), then create the scheduled routine by copy-pasting the
   prompt from `docs/ROUTINE.md`. Each weekday morning the sweep checks those
   companies' job boards and leaves you a shortlist report.
2. **`/choose`** — over coffee, skim the shortlist and pick the keepers.
   "None of these" is a fine answer; rejected roles never come back.
3. **`/tailor`** — drafts resumes and cover letters for your picks only, and
   reviews them with you live, same as `/add`.
4. **Apply by hand, then `/log`.** Same as always.

## The commands

| Command | What it does |
|---|---|
| `/setup` | One-time interview that builds your profile and evidence bank |
| `/add` | Paste in a job ad you found; fit read + tailored draft in one sitting |
| `/next` | "What should I do now?" — reads the state of play, gives you one next step |
| `/choose` | Morning pick: which shortlisted roles are worth tailoring? |
| `/tailor` | Write the resume + cover letter for the roles you kept |
| `/review` | Re-open a draft you deferred and finish reviewing it |
| `/log` | Record "I applied" or any status change, in about two minutes |
| `/sweep` | The nightly search itself (normally run by the schedule, not by you) |

## What's in the folders

```
profile/     Everything about you (starts empty; /setup fills it in)
queue/       Roles in flight: the sweep's shortlist and your ready-to-send drafts
applied/     Roles you've applied to (created by /log)
tracker.csv  The self-maintaining application tracker
templates/   Blank starting points the system copies from
docs/        The two copy-paste setup guides (environment + schedule)
bin/         The scripts that fetch postings and fact-check drafts
.claude/     The commands and rules Claude follows
PRD.md       The full design document, if you're curious how it all works
CLAUDE.md    The safety rules Claude must obey in this repo
```

## Good to know

- **Your data stays in your private repo.** This template contains no
  personal data, and your copy should stay private because it will.
- **Everything is saved in Git automatically.** Every draft, decision, and
  status change is committed, so nothing is ever lost and you can always see
  history on GitHub.
- **It's honest by design.** The fact-checker catches invention (made-up
  numbers, employers, technologies). What it can't catch is *stretching* a
  real fact — that's what your review is for. When in doubt, tone it down.
- **Costs nothing beyond your Claude subscription.** The job-board checks use
  free public APIs; there are no API keys anywhere in the system.

## For technical users

```bash
pip install --break-system-packages typst pyyaml httpx pydantic pytest
python3 -m pytest tests/            # acceptance tests
python3 bin/fetch.py --dry-run      # fetch + dedupe, writes nothing
python3 bin/seen.py status          # what the dedupe index has seen
python3 bin/validate.py <variant.yaml>
```

The full design and rationale live in `PRD.md`; the operating rules and red
lines in `CLAUDE.md`.

---

Created by **Annabel Nguyen**.
