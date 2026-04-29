#!/usr/bin/env python3
"""
show_comments.py — render a claude-collab essay with inline reader notes.

Usage:
    python show_comments.py random037
    python show_comments.py random037.md
    python show_comments.py /full/path/to/random037.md
"""

import json
import os
import sys
from datetime import datetime


def parse_timestamp(ts):
    # Strip timezone offset to keep it simple; show date only
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


def main():
    if len(sys.argv) != 2:
        print("Usage: show_comments.py <path-to-md-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    # Normalize: ensure .md extension
    if not path.endswith(".md"):
        path = path + ".md"

    # If not an absolute path, look in the claude-steve essays dir
    if not os.path.isabs(path):
        essays_dir = os.path.expanduser("~/showell_repos/claude-steve")
        path = os.path.join(essays_dir, path)

    if not os.path.exists(path):
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        content = f.read()

    # Split into paragraphs on blank lines (preserve original paragraph boundaries)
    raw_paragraphs = content.split("\n\n")
    # Strip trailing newline from each paragraph for cleaner display
    paragraphs = [p.rstrip("\n") for p in raw_paragraphs]

    # Load comments if sidecar exists
    comments_path = path + ".comments.json"
    comments_by_para = {}
    if os.path.exists(comments_path):
        with open(comments_path) as f:
            data = json.load(f)
        for c in data.get("comments", []):
            idx = c["para_index"]
            comments_by_para.setdefault(idx, []).append(c)

    # Render
    for i, para in enumerate(paragraphs):
        print(para)
        if i in comments_by_para:
            print()
            for c in comments_by_para[i]:
                ts = parse_timestamp(c.get("timestamp", ""))
                author = c.get("author", "?")
                text = c.get("text", "")
                print(f"  > NOTE ({author}, {ts}): {text}")
        print()


if __name__ == "__main__":
    main()
