# Your profile lives here

This folder is empty on purpose. It gets filled in when you run **`/setup`**
in a Claude Code session, an interview that builds everything the system
knows about you:

| File | What it is | Created by |
|---|---|---|
| `goals.yaml` | **Where you want to go**: one to three career tracks, and whether each is a change of direction. Written first, because it decides what everything else is measured against | `/setup` |
| `evidence-bank.md` | Your "master resume": every job, project and accomplishment, each with an ID and an honesty rating. **Where you have been.** Its `## Angles` block holds your positioning: each one a claim about what you're for and the evidence that proves it, the **argument** a tailored resume makes | `/setup` |
| `resume.yaml` | The canonical facts: every employer, title and date, exactly once | `/setup` |
| `voice.md` | A short description of how you write, so drafts sound like you | `/setup` |
| `config.yaml` | Your preferences: salary floor, locations, dealbreakers, cover-letter length | `/setup` |
| `companies/<name>.md` | Three honest lines about why you'd join a company you care about, plus anything Claude researched, with sources | you, `/apply`, `/prep` |
| `connections.csv` | (Optional) your LinkedIn connections export, for spotting referral paths | you |
| `targets.yaml` | (Only if you switch on the optional sweep) the companies whose job boards it watches | you, per `optional/sweep/README.md` |

Never edit these by hand unless you want to; every command knows how to
maintain them for you. The one worth revisiting yourself is `goals.yaml`: it's
the only file nothing else will ever change, because what you're aiming at is
your call.

**Privacy note:** this folder will contain your real career history. That is
why your copy of this repository must be **private**.
