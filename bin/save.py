#!/usr/bin/env python3
"""save.py — commit and push the repo, quietly. The one git call every skill makes.

    save.py "<commit message>"       stage everything, commit, push; rebase on a
                                     rejected push and push once more
    save.py --guard                  only check this is a private copy, not the
                                     shared template; write nothing

The repo is the database (CLAUDE.md): anything that must survive the session
is committed and pushed before it ends. Every skill used to carry its own
copy of the same shell one-liner, and the one place a git error could reach a
browser-only user was that line. This script owns it instead: one tested
path, plain messages, a non-zero exit the skill can act on.

Two guards live here because every save goes through here:

* **The template guard.** `/setup` run inside the shared template would push
  a real career history to a repo other people copy. If the origin remote's
  repository name is the template's (the same test CI uses,
  `.github/workflows/ci.yml`), refuse before anything is written. A private
  copy made with "Use this template" has the name the user gave it.
* **Nothing to commit is not an error.** A section that changed no file still
  ends cleanly.

Pushes go to the branch that is checked out, which in a private copy is
`main`. No merges, no force, no history rewriting: a rejected push pulls with
`--rebase` and tries once more, and if that fails too the message says what
to do.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

# The shared template's repository name. Mirrors the `endsWith(github.repository,
# '/jobseeker-template')` scope in ci.yml; keep the two in step.
TEMPLATE_REPO_NAME = "jobseeker-template"


def git(*args: str, cwd: str | None = None, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
    )


def remote_repo_name(url: str) -> str:
    """`owner/name` → `name` for the URL shapes git prints for `origin`."""
    tail = url.strip().rstrip("/").rsplit("/", 1)[-1]
    tail = tail.rsplit(":", 1)[-1]  # git@github.com:owner/name.git → name.git
    return re.sub(r"\.git$", "", tail)


def is_template(cwd: str | None = None) -> bool:
    r = git("remote", "get-url", "origin", cwd=cwd)
    if r.returncode != 0:
        return False  # no remote: nothing this could leak to
    return remote_repo_name(r.stdout).lower() == TEMPLATE_REPO_NAME


TEMPLATE_MESSAGE = (
    "This is the shared template, not a private copy. Nothing was saved.\n"
    "Make your own copy first: on the template's GitHub page choose "
    "'Use this template' -> 'Create a new repository', set it to Private, "
    "then open that copy in Claude Code and run /setup there."
)


def save(message: str, cwd: str | None = None) -> int:
    if is_template(cwd):
        print(TEMPLATE_MESSAGE, file=sys.stderr)
        return 2

    git("add", "-A", cwd=cwd)
    if git("diff", "--cached", "--quiet", cwd=cwd).returncode == 0:
        print("nothing to save", file=sys.stderr)
        return 0

    r = git("commit", "-q", "-m", message, cwd=cwd)
    if r.returncode != 0:
        print(f"commit failed:\n{r.stderr.strip()}", file=sys.stderr)
        return 1

    branch = git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd).stdout.strip() or "main"
    if git("remote", "get-url", "origin", cwd=cwd).returncode != 0:
        print("saved locally; no remote to push to", file=sys.stderr)
        return 0

    push = git("push", "-q", "-u", "origin", branch, cwd=cwd)
    if push.returncode == 0:
        print(f"saved: {message}", file=sys.stderr)
        return 0

    pull = git("pull", "-q", "--rebase", "origin", branch, cwd=cwd)
    if pull.returncode != 0:
        git("rebase", "--abort", cwd=cwd)
        print(
            "saved locally, but the copy on GitHub has changes that conflict with "
            "these. Nothing is lost. Open the repository on GitHub, or ask for help "
            "resolving the conflict, before the next save.\n" + pull.stderr.strip(),
            file=sys.stderr,
        )
        return 1

    push = git("push", "-q", "-u", "origin", branch, cwd=cwd)
    if push.returncode != 0:
        print(
            "saved locally, but pushing to GitHub failed twice. Nothing is lost; "
            "the next save will retry.\n" + push.stderr.strip(),
            file=sys.stderr,
        )
        return 1
    print(f"saved: {message}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Commit and push, quietly.")
    parser.add_argument("message", nargs="?", help="commit message")
    parser.add_argument(
        "--guard",
        action="store_true",
        help="only check this is a private copy, not the shared template",
    )
    parser.add_argument("--cwd", help="repository to operate on (default: current directory)")
    args = parser.parse_args(argv)

    if args.guard:
        if is_template(args.cwd):
            print(TEMPLATE_MESSAGE, file=sys.stderr)
            return 2
        print("OK: private copy", file=sys.stderr)
        return 0
    if not args.message:
        parser.error("a commit message is required (or --guard)")
    return save(args.message, args.cwd)


if __name__ == "__main__":
    raise SystemExit(main())
