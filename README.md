# Jobseeker

**A job-search assistant that runs inside Claude Code.** Paste in a job ad,
get an honest read on the fit, and, if you say yes, a tailored resume and
cover letter built only from facts you gave it. You review every line. You
always click "apply" yourself, in your own browser.

It works from **where you want to go**, not just where you've been, so it fits
a graduate, a career changer, and someone after the next rung equally well.
It assumes nothing about your field, seniority or country: every judgment it
makes comes from answers you give it during setup.

MIT licensed. Copy it, change it, keep it.

## What it does

- **Knows what you're aiming at.** Setup asks for one to three career tracks,
  in your words. Every role is scored against those, not against your last
  job title. If a track is a change of direction, you say so and name what
  genuinely carries across and what you're missing; drafts then lead with the
  transferable work and state the gap plainly.
- **Reads the fit honestly.** Paste an ad and you get a score, the reason, the
  red flags, and what the role wants that you don't have. Then it asks
  whether to draft it. "No" and "later" are fine answers.
- **Drafts for the screening software, then for the human.** Most
  applications are read by keyword-matching software first. A checker works
  out which words the employer keeps repeating and reports exactly which ones
  your draft uses. It will re-word your own experience in the employer's
  language and pull forward the evidence that proves the point. It will never
  add a skill you don't have: anything it can't cover honestly is written
  down as a gap for you to see.
- **Never makes things up.** Every claim in every draft traces back to a fact
  you told it during setup. An automated checker blocks drafts that invent
  numbers, employers or skills, and bans AI-sounding phrases so letters read
  like you wrote them.
- **Walks the draft with you.** The top third first (headline, summary,
  skills), because that's what a screener reads before deciding whether to
  read on. Questions it couldn't answer are asked now, and your answers are
  saved so it never asks twice.
- **Tracks everything.** A simple spreadsheet shows every application and its
  status. It updates itself. After a week of silence it nudges you to send a
  short follow-up, and it can report your callback rate by track and by
  resume angle so you can see which argument is landing.
- **Preps you for the interview.** When a reply comes, `/prep` builds likely
  questions, practice stories from your own history, and plain-spoken answers
  for the gaps. It preps you to back up what you claimed, never to claim more.

## What it will never do

- **Never submits an application.** You apply by hand, every time.
- **Never invents or exaggerates** a metric, title, date or skill.
- **Never scrapes** LinkedIn, Indeed, or anything behind a login.
- If it doesn't know something about you, it **asks** instead of guessing.
- If you're missing something a role wants, it **says so** instead of
  papering over it.

## What you need

- A free **GitHub account**. Your private copy of this system lives there,
  and Claude saves your work back to it.
- A paid **Claude plan** with Claude Code on the web at
  [claude.ai/code](https://claude.ai/code). Nothing to install, no API key.

You do not need to know how to code, and you never touch git. You type
commands like `/setup` and `/apply` into a chat; saving is automatic.

## Set it up (once)

1. **Copy the template.** On this repository's GitHub page click
   **Use this template → Create a new repository**. Name it (for example
   `my-jobseeker`) and choose **Private**. Private matters: your copy will
   hold your real career history.
2. **Connect GitHub to Claude.** Open [claude.ai/code](https://claude.ai/code)
   and, when prompted, install the Claude GitHub app and grant it access to
   the repository you just created. This is what lets Claude read your copy
   and save changes to it. If GitHub is already connected, add the new
   repository in Claude's settings under **Connectors → GitHub**.
3. **Open the repository.** In claude.ai/code pick your new repository and
   start a session. The first start installs its own tools; wait for the
   prompt before typing.
4. **Run `/setup`.** Have your current resume handy, plus a cover letter you
   liked and two or three job ads you'd apply to today. Claude reads them,
   then interviews you a few questions at a time: where you want to go, the
   plain facts (employers, titles, dates), and what you've actually done,
   which becomes the evidence bank every draft draws from. A first pass takes
   about half an hour. Everything is saved as you go, so you can stop at any
   point and re-run `/setup` later to continue or add more. Honest answers
   matter more than impressive ones.
5. **Try it.** Find a job ad anywhere, run `/apply`, and paste it in.

Lost at any point? Type `/next`.

## The everyday loop

| Command | What it does |
|---|---|
| `/apply` | Paste an ad. Get the fit read. Say yes and it drafts the resume and cover letter and walks them with you. Run it with nothing pasted to see what's waiting. |
| *(you)* | Open the employer's site and submit the application yourself, using the approved draft. |
| `/log` | "I applied to X." Later: "X replied" / "rejected". Two minutes. The tracker updates itself. |
| `/prep` | An interview is coming: likely questions, practice stories, honest answers for the gaps. |
| `/next` | "What should I do now?" One prioritised action and the short list of everything pending. |
| `/setup` | The one-time interview. Re-run it any time to add to your evidence bank or change your goals. |

## Changing direction, or aiming at two things

Your career tracks live in `profile/goals.yaml`, and they are meant to be
edited. Open it, or just tell Claude in a session, when you're pivoting, when
you're open to a second direction, or when a track keeps coming up empty.
Nothing edits that file but you. Claude reads your goals and reports when a
track isn't working, and leaves the decision alone.

## Optional: the nightly sweep

If you'd rather not go looking for ads, the sweep can check chosen companies'
public job boards every weekday morning and queue anything promising for you
to look at with `/apply`. It costs about ten minutes of one-time settings work
outside the chat and only covers employers on the big job-board systems.
Everything about it, including how to switch it on, is in
[`optional/sweep/README.md`](optional/sweep/README.md). The everyday loop is
complete without it.

## What's in the folders

```
profile/       Everything about you (starts empty; /setup fills it in)
queue/         Roles in flight: ads you've pasted and drafts ready to send
applied/       Roles you've applied to (created by /log)
tracker.csv    The self-maintaining application tracker
templates/     Blank starting points the system copies from
bin/           The scripts that fact-check drafts and build the tracker
optional/      The nightly sweep, if you ever want it
docs/          A one-page explanation of how it all fits together
.claude/       The commands and rules Claude follows
CLAUDE.md      The rules Claude must obey in this repo
```

## Getting improvements later

Your copy is a snapshot. To pick up fixes made to the template afterwards,
ask Claude in a session:

> Pull the latest changes from the upstream template, but keep everything in
> `profile/`, `queue/`, `applied/`, `state/` and `tracker.csv` exactly as it is.

## Sharing it on

Point people at the template repo, not at your copy. They click **Use this
template**, make it **private**, and run `/setup`. Nothing about your search
carries across.

## Good to know

- **Your data stays in your private repo.** The template contains no personal
  data (an automated check enforces that), and your copy should stay private
  because it will.
- **Everything is saved automatically.** Every draft, answer and status change
  is kept, so nothing is lost and you can always look back.
- **It's honest by design.** The checker catches invention. What it can't
  catch is stretching a real fact; that's what your walkthrough is for. When
  in doubt, tone it down.
- **Costs nothing beyond your Claude subscription.** No API keys anywhere.

## For technical users

```bash
pip install --break-system-packages typst pyyaml pytest ruff
python3 -m pytest -q                         # core + optional sweep tests
python3 bin/validate.py <resume.yaml>        # provenance + style gate
python3 bin/validate.py --lint-bank          # the bank's angles hold together
python3 bin/ats_score.py --jd jd.md --variant <resume.yaml> --cover cover.md
python3 bin/tracker.py --stats               # funnel, callback rates, follow-ups due
python3 bin/check_template_clean.py          # template guard (fails in your copy, by design)
```

`docs/HOW-IT-WORKS.md` is the one-page map. `docs/archive/PRD.md` is the
original design document, kept for the reasoning. `CLAUDE.md` holds the
operating rules.

Released under the MIT License. See `LICENSE`.
