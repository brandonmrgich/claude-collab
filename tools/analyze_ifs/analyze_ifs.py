#!/usr/bin/env python3
"""analyze_ifs.py — extract and rank IF entries from a plan-executor log.

Reads .claude/plan-executor.log from a repo root, classifies every
this_would_have_been_easier_if entry by taxonomy, and reports:
  - counts by category (spinup-brief / tooling / task-spec / other)
  - DEFERRED spinup-brief IFs ranked by frequency (briefs most overdue for refresh)
  - FIXED vs DEFERRED breakdown

Usage:
    python3 analyze_ifs.py [repo_path]

repo_path defaults to the current directory.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path


CATEGORIES = ("spinup-brief", "tooling", "task-spec", "methodology")

# Matches: (category) description — ACTION
# or:      (category) description
IF_LINE = re.compile(
    r"^\s+\d+\.\s+\(([^)]+)\)\s+(.+?)(?:\s+[—–-]+\s*(.+))?$"
)


def parse_log(log_path):
    entries = []
    current_dispatch = None
    in_ifs = False
    if_count_expected = 0
    if_count_seen = 0

    with open(log_path) as f:
        for raw in f:
            line = raw.rstrip()

            # Dispatch header
            m = re.match(r"\[.+?\]\s+dispatching\s+(.+)", line)
            if m:
                current_dispatch = m.group(1).strip()
                in_ifs = False
                continue

            # Return header (may update dispatch name)
            m = re.match(r"\[.+?\]\s+(.+?)\s+RETURN", line)
            if m:
                current_dispatch = m.group(1).strip()
                in_ifs = False
                continue

            # Inline zero-IF: 0 IFs ("brief was good")
            m = re.match(r".*\b0 IFs\b", line)
            if m:
                in_ifs = False
                continue

            # IF block header: "IFs received: N"
            m = re.match(r"\s+IFs received:\s*(\d+)", line)
            if m:
                if_count_expected = int(m.group(1))
                if_count_seen = 0
                in_ifs = if_count_expected > 0
                continue

            # Numbered IF entry
            if in_ifs:
                m = IF_LINE.match(line)
                if m:
                    category = m.group(1).strip().lower()
                    description = m.group(2).strip()
                    action_raw = (m.group(3) or "").strip()
                    action = classify_action(action_raw)
                    entries.append({
                        "dispatch": current_dispatch,
                        "category": category,
                        "description": description,
                        "action": action,
                        "action_raw": action_raw,
                    })
                    if_count_seen += 1
                    if if_count_seen >= if_count_expected:
                        in_ifs = False
                    continue

    return entries


def classify_action(raw):
    u = raw.upper()
    if "FIXED" in u:
        return "FIXED"
    if "DEFERRED" in u:
        return "DEFERRED"
    if raw:
        return "OTHER"
    return "UNKNOWN"


def normalize_category(cat):
    for c in CATEGORIES:
        if c in cat:
            return c
    return "other"


def report(entries):
    if not entries:
        print("No IF entries found.")
        return

    by_cat = defaultdict(list)
    for e in entries:
        by_cat[normalize_category(e["category"])].append(e)

    total = len(entries)
    print(f"=== IF summary: {total} total entries ===\n")

    # Category counts
    for cat in CATEGORIES + ("other",):
        n = len(by_cat[cat])
        if n:
            fixed = sum(1 for e in by_cat[cat] if e["action"] == "FIXED")
            deferred = sum(1 for e in by_cat[cat] if e["action"] == "DEFERRED")
            print(f"  {cat:<16} {n:>3}  (fixed={fixed}, deferred={deferred})")

    # Spinup-brief deep-dive: DEFERRED entries ranked by keyword frequency
    sb = by_cat["spinup-brief"]
    if sb:
        deferred_sb = [e for e in sb if e["action"] == "DEFERRED"]
        print(f"\n=== spinup-brief IFs: {len(sb)} total, {len(deferred_sb)} DEFERRED ===\n")

        if deferred_sb:
            print("DEFERRED spinup-brief IFs (most in need of attention):\n")
            # Rank by keyword overlap — group descriptions sharing a keyword
            keyword_groups = cluster_by_keyword(deferred_sb)
            for kw, group in sorted(keyword_groups.items(), key=lambda x: -len(x[1])):
                print(f"  [{len(group)}x] {kw}")
                for e in group:
                    print(f"       dispatch={e['dispatch']}")
                    print(f"       {e['description']}")
                print()
        else:
            print("  No DEFERRED spinup-brief IFs — briefs look current.\n")

        fixed_sb = [e for e in sb if e["action"] == "FIXED"]
        if fixed_sb:
            print(f"FIXED spinup-brief IFs ({len(fixed_sb)}):\n")
            for e in fixed_sb:
                print(f"  {e['description']}")
            print()

    # Tooling IFs
    tooling = by_cat["tooling"]
    if tooling:
        print(f"=== tooling IFs: {len(tooling)} ===\n")
        deferred_t = [e for e in tooling if e["action"] != "FIXED"]
        if deferred_t:
            print("Not yet actioned:")
            for e in deferred_t:
                print(f"  {e['description']}  ({e['action_raw'] or 'no action recorded'})")
        else:
            print("  All tooling IFs actioned.")
        print()


def cluster_by_keyword(entries):
    # Simple keyword extraction: use the first 3-4 significant words as the key
    stop = {"the", "a", "an", "in", "on", "for", "of", "to", "was", "is",
            "be", "at", "by", "no", "not", "and", "or", "with", "from",
            "that", "this", "should", "would", "have", "had", "been"}
    groups = defaultdict(list)
    for e in entries:
        words = [w.lower().strip("().,—-") for w in e["description"].split()]
        key_words = [w for w in words if w and w not in stop][:3]
        key = " ".join(key_words) if key_words else e["description"][:40]
        groups[key].append(e)
    return dict(groups)


def main():
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    log_path = repo / ".claude" / "plan-executor.log"

    if not log_path.exists():
        print(f"No plan-executor.log found at {log_path}")
        sys.exit(1)

    entries = parse_log(log_path)
    report(entries)


if __name__ == "__main__":
    main()
