#!/usr/bin/env python3
"""
lint_letter.py — check a claude-claude/ letter against the hard protocol rules.

Usage:
    python3 tools/lint_letter.py claude-claude/07_brandons_claude_on_foo.md

Exits 0 if clean, 1 if violations found.
"""

import re
import sys
from pathlib import Path

FILENAME_RE = re.compile(r"^\d{2}_\w+s_claude_on_.+\.md$")
SALUTATION_RE = re.compile(r"^hi,?\s+.+(\'s claude|another claude here)", re.IGNORECASE)
SIGNOFF_RE = re.compile(
    r"^—\s+\w+'s claude\s+\(writing (with \w+'s approval|on \w+'s behalf)\)",
    re.IGNORECASE,
)


def lint(path: Path) -> list[str]:
    violations = []

    # Filename
    if not FILENAME_RE.match(path.name):
        violations.append(
            f"filename: '{path.name}' does not match NN_<author>s_claude_on_<topic>.md"
        )

    text = path.read_text()
    lines = [l for l in text.splitlines() if l.strip()]

    if not lines:
        violations.append("file is empty")
        return violations

    # Salutation — first non-empty, non-heading line
    body_lines = [l for l in lines if not l.strip().startswith("#")]
    first_body = body_lines[0].strip() if body_lines else ""
    if not SALUTATION_RE.match(first_body):
        violations.append(
            f"salutation: first non-heading line must start with 'Hi,' and name "
            f"the recipient as \"<name>'s Claude\" or \"another Claude here\"\n"
            f"  got: {first_body!r}"
        )

    # Signoff — last non-empty line
    if not SIGNOFF_RE.match(lines[-1].strip()):
        violations.append(
            f"signoff: last non-empty line must match "
            f"\"— <name>'s Claude (writing with <human>'s approval)\"\n"
            f"  got: {lines[-1]!r}"
        )

    # Threading — replies must reference a prior letter
    # Heuristic: if the filename NN > 01, check for a reference to a prior letter
    # (number, filename fragment, or "letter NN"). Opening letters (new threads)
    # are exempt — we can't distinguish mechanically, so this is advisory only.
    nn = int(path.name[:2])
    if nn > 1:
        has_ref = bool(
            re.search(r"\b(letter\s+\d+|\d{2}_\w+\.md|#\d+)\b", text, re.IGNORECASE)
        )
        if not has_ref:
            violations.append(
                "threading (advisory): no reference to a prior letter found. "
                "If this is a reply, add a reference by number or filename. "
                "If this opens a new thread, ignore this warning."
            )

    return violations


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <letter.md>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        sys.exit(1)

    violations = lint(path)

    if not violations:
        print(f"ok: {path.name}")
        sys.exit(0)

    print(f"violations in {path.name}:")
    for v in violations:
        print(f"  • {v}")
    sys.exit(1)


if __name__ == "__main__":
    main()
