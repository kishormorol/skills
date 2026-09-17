#!/usr/bin/env python3
"""Print the prompts a user typed in past Claude Code sessions for one project.

Claude Code stores each session as JSONL under ~/.claude/projects/<slug>/, where
<slug> is the project's absolute path with every non-alphanumeric character
replaced by "-". This reads those files and prints one typed prompt per line,
oldest first, as "YYYY-MM-DD<TAB>prompt".

Skipped: tool results, sidechain (subagent) turns, meta turns, slash-command and
system wrappers, and anything longer than --max-len (pasted documents, not asks).

Usage:
  extract_asks.py [project_dir] [--since YYYY-MM-DD] [--max-len 400]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path


def slug(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(path))


def prompt_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir", nargs="?", default=os.getcwd())
    ap.add_argument("--since", default="")
    ap.add_argument("--max-len", type=int, default=400)
    args = ap.parse_args()

    sessions = Path.home() / ".claude" / "projects" / slug(args.project_dir)
    if not sessions.is_dir():
        sys.exit(f"no session history at {sessions}")

    asks = []
    for f in sessions.glob("*.jsonl"):
        with open(f, errors="ignore") as fh:
            for line in fh:
                try:
                    turn = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if turn.get("type") != "user" or turn.get("isMeta") or turn.get("isSidechain"):
                    continue
                text = prompt_text(turn.get("message", {}).get("content")).strip()
                if not text or text.startswith("<") or text.startswith("[Request"):
                    continue
                if len(text) > args.max_len:
                    continue
                day = turn.get("timestamp", "")[:10]
                if day < args.since:
                    continue
                asks.append((day, " ".join(text.split())))

    asks.sort()
    for day, text in asks:
        print(f"{day}\t{text}")
    print(f"{len(asks)} prompts from {sessions}", file=sys.stderr)


if __name__ == "__main__":
    main()
