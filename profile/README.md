# Your profile lives here

This folder is empty on purpose. It gets filled in when you run **`/setup`**
in a Claude Code session — an interview that builds everything the system
knows about you:

| File | What it is | Created by |
|---|---|---|
| `evidence-bank.md` | Your "master resume" — every job, project, and accomplishment, each with an ID and an honesty rating | `/setup` |
| `resume.yaml` | The canonical facts: every employer, title, and date, exactly once | `/setup` |
| `voice.md` | A short description of how you write, so drafts sound like you | `/setup` |
| `config.yaml` | Your preferences: salary floor, locations, dealbreakers, scoring threshold | `/setup` (from `templates/config.example.yaml`) |
| `targets.yaml` | The companies whose job boards the automated sweep watches | `/setup` (from `templates/targets.example.yaml`) |
| `companies/<name>.md` | Three honest lines about why you'd join each company you care about | you, with help from `/setup` |
| `manual-postings/` | Job ads you found yourself and pasted in with `/add` | `/add` |
| `connections.csv` | (Optional) your LinkedIn connections export, for spotting referral paths | you |

Never edit these by hand unless you want to — every skill knows how to
maintain them for you.

**Privacy note:** this folder will contain your real career history. That is
why your copy of this repository must be **private** (see the README's setup
steps).
