#!/usr/bin/env python3
"""tracker.py — regenerate tracker.csv from meta.yaml files. PRD §8.4, §23, G4.

    tracker.py [--root .] [-o tracker.csv]
    tracker.py --stats [--root .]

The tracker is DERIVED, never maintained (principle 3.2). Delete tracker.csv,
regenerate, and get a byte-identical file. Scans applied/*/meta.yaml and
queue/ready/*/meta.yaml. Derives days_since_applied, status (auto-ghosted after
config.tracker.ghost_days silent days), next_action, funnel_stage.

Two derived views serve the callback loop (PRD §23):
  * An application silent past `config.tracker.followup_days` (default 7) gets
    next_action "send a follow-up" — a nudge to the HUMAN, who follows up in
    their own words, by hand. Nothing here contacts anyone.
  * `--stats` prints funnel counts and response/callback rates, overall and
    broken down by goals.yaml track, by source, and by the angle each variant
    was positioned on — so the human can see which argument actually earns
    callbacks. It reads the same meta.yaml files, writes nothing, and reports;
    retuning goals or angles stays the human's call (red line 7).

No Google Sheets push — GitHub renders a committed CSV as a sortable table on
desktop and mobile for free (PRD §8.4).
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import sys
from datetime import date, datetime

import yaml

COLUMNS = [
    "date",
    "company",
    "title",
    "status",
    "days_since_applied",
    "funnel_stage",
    "next_action",
    "url",
    "dir",
]

# Positive statuses the human sets in meta.yaml via /log. Silence -> ghosted.
FUNNEL = {
    "shortlisted": 0,
    "kept": 0,
    "queued": 0,
    "applied": 1,
    "ghosted": 1,
    "reply": 2,
    "screen": 3,
    "onsite": 4,
    "offer": 5,
    "rejected": -1,
    "withdrawn": -1,
}

NEXT_ACTION = {
    "shortlisted": "pick keeps with /choose",
    "kept": "run /tailor",
    "queued": "review at Gate 2",
    "applied": "wait",
    "ghosted": "follow up or drop",
    "reply": "schedule screen; run /prep",
    "screen": "run /prep; confirm onsite",
    "onsite": "send thank-you, await decision",
    "offer": "negotiate / decide",
    "rejected": "—",
    "withdrawn": "—",
}

# Statuses that mean an application was actually submitted (the /log record),
# split by what the employer did next. Everything else in FUNNEL is pre-apply.
APPLIED_STATUSES = {"applied", "ghosted", "reply", "screen", "onsite", "offer",
                    "rejected", "withdrawn"}
RESPONDED = {"reply", "screen", "onsite", "offer", "rejected"}  # any human answer
CALLBACKS = {"reply", "screen", "onsite", "offer"}              # positive interest


def _today(explicit: str | None) -> date:
    if explicit:
        return datetime.strptime(explicit, "%Y-%m-%d").date()
    return date.today()


def _parse_date(value) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(value), fmt).date()
        except ValueError:
            continue
    return None


def load_config(root: str) -> dict:
    path = os.path.join(root, "profile", "config.yaml")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _variant_angle(entry_dir: str) -> str:
    """The angle the entry's variant.yaml was positioned on, else "".

    `angle:` is the current key; `label:` the older spelling (PRD §21). Read
    only for --stats; tolerant of a missing or unparseable variant.
    """
    path = os.path.join(entry_dir, "variant.yaml")
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as fh:
            variant = yaml.safe_load(fh) or {}
    except yaml.YAMLError:
        return ""
    if not isinstance(variant, dict):
        return ""
    for key in ("angle", "label"):
        value = variant.get(key)
        if value and str(value).strip():
            return str(value).strip().lower()
    return ""


def collect_rows(root: str, ghost_days: int, today: date, followup_days: int = 0) -> list[dict]:
    rows: list[dict] = []
    patterns = [
        os.path.join(root, "applied", "*", "meta.yaml"),
        os.path.join(root, "queue", "ready", "*", "meta.yaml"),
    ]
    seen_dirs: set[str] = set()
    for pattern in patterns:
        for meta_path in sorted(glob.glob(pattern)):
            dir_name = os.path.basename(os.path.dirname(meta_path))
            if dir_name in seen_dirs:
                continue
            seen_dirs.add(dir_name)
            with open(meta_path, encoding="utf-8") as fh:
                meta = yaml.safe_load(fh) or {}

            status = str(meta.get("status", "queued")).strip().lower()
            applied_on = _parse_date(meta.get("applied") or meta.get("date"))
            days = (today - applied_on).days if applied_on else ""

            # Auto-ghost: applied, silent past ghost_days, no positive event.
            if status == "applied" and isinstance(days, int) and days >= ghost_days:
                status = "ghosted"

            next_action = NEXT_ACTION.get(status, "review")
            # Applied, silent past followup_days but not yet ghosted: nudge the
            # human to follow up (by hand, in their own words). 0 disables.
            if (
                status == "applied"
                and followup_days > 0
                and isinstance(days, int)
                and days >= followup_days
            ):
                next_action = "send a follow-up"

            rows.append(
                {
                    "date": meta.get("date", applied_on.isoformat() if applied_on else ""),
                    "company": meta.get("company", ""),
                    "title": meta.get("title", ""),
                    "status": status,
                    "days_since_applied": days,
                    "funnel_stage": FUNNEL.get(status, 0),
                    "next_action": next_action,
                    "url": meta.get("url", ""),
                    "dir": dir_name,
                    # Not CSV columns — carried for --stats only.
                    "track": str(meta.get("track", "") or "").strip().lower(),
                    "source": str(meta.get("source", "") or "").strip().lower(),
                    "angle": _variant_angle(os.path.dirname(meta_path)),
                }
            )
    # Deterministic order so regeneration is byte-identical (G4 / Phase 7 test).
    rows.sort(key=lambda r: (str(r["date"]), r["dir"]))
    return rows


def write_csv(rows: list[dict], out_path: str) -> None:
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _rate(part: int, whole: int) -> str:
    return f"{part}/{whole} ({100 * part / whole:.0f}%)" if whole else "0/0"


def render_stats(rows: list[dict], followup_days: int) -> str:
    """The funnel, and who answered — overall and by track / source / angle.

    Reporting only: the numbers say which track, source, or angle earns
    callbacks; what to change about goals or angles stays the human's call.
    """
    apps = [r for r in rows if r["status"] in APPLIED_STATUSES]
    lines = ["Search funnel", ""]
    if not apps:
        lines.append("  no applications logged yet (rows appear after /log)")
        return "\n".join(lines)

    responded = [r for r in apps if r["status"] in RESPONDED]
    callbacks = [r for r in apps if r["status"] in CALLBACKS]
    interviews = [r for r in apps if r["status"] in ("screen", "onsite", "offer")]
    offers = [r for r in apps if r["status"] == "offer"]
    lines += [
        f"  applications   {len(apps)}",
        f"  any response   {_rate(len(responded), len(apps))}   (includes rejections)",
        f"  callbacks      {_rate(len(callbacks), len(apps))}   (reply or interview)",
        f"  interviews     {_rate(len(interviews), len(apps))}",
        f"  offers         {_rate(len(offers), len(apps))}",
    ]

    for field, label in (("track", "by track"), ("source", "by source"), ("angle", "by angle")):
        groups = sorted({r[field] for r in apps if r[field]})
        if not groups:
            continue
        lines += ["", f"  {label}"]
        for g in groups:
            sub = [r for r in apps if r[field] == g]
            got = [r for r in sub if r["status"] in CALLBACKS]
            lines.append(f"    {g:<28} callbacks {_rate(len(got), len(sub))}")

    due = [r for r in rows if r["next_action"] == "send a follow-up"]
    if due:
        lines += ["", f"  follow-ups due (applied ≥{followup_days}d ago, no response — "
                      "follow up by hand, in your own words):"]
        for r in due:
            lines.append(f"    {r['company']} · {r['title']} — applied {r['days_since_applied']}d ago")

    lines += ["", "  A low rate is information, not an instruction: report it, review the",
              "  drafts, or adjust your goals yourself — nothing here retunes anything."]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate tracker.csv from meta.yaml files.")
    parser.add_argument("--root", default=".")
    parser.add_argument("-o", "--out", default=None)
    parser.add_argument("--today", default=None, help="override today's date (YYYY-MM-DD)")
    parser.add_argument(
        "--stats",
        action="store_true",
        help="print funnel counts, response/callback rates, and follow-ups due "
        "(reads the same meta.yaml files; writes nothing)",
    )
    args = parser.parse_args(argv)

    config = load_config(args.root)
    tracker_cfg = config.get("tracker", {}) or {}
    ghost_days = int(tracker_cfg.get("ghost_days", 21))
    followup_days = int(tracker_cfg.get("followup_days", 7))
    today = _today(args.today)
    out_path = args.out or os.path.join(args.root, "tracker.csv")

    rows = collect_rows(args.root, ghost_days, today, followup_days)
    if args.stats:
        print(render_stats(rows, followup_days))
        return 0
    write_csv(rows, out_path)
    print(f"wrote {out_path} — {len(rows)} row(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
