"""
parse_return.py — extract structured fields from a sub-agent's return.

Reads a sub-agent's reply text (stdin or --file), pulls out the
fields the dispatch asked for, and reports any missing required
field — especially the IF, which is the orchestrator's only
window into sub-agent friction.

Output is JSON to stdout. Missing-required-field warnings go
to stderr; the script exits non-zero if the IF is missing.

Usage:

    cat sub_agent_reply.txt | python3 parse_return.py
    python3 parse_return.py --file sub_agent_reply.txt
"""

import argparse
import json
import re
import sys

from dispatch_dsl import RETURN_FIELDS, RETURN_REQUIRED


def _strip_marker(line):
    """Strip a leading bullet/dash from a field line."""
    return re.sub(r"^\s*[-*]\s*", "", line)


def parse_return(text):
    """Extract structured fields from a sub-agent's reply.

    Returns a dict mapping field-key -> value (string or list).
    Unparsed input is ignored; the parser walks the text looking
    for `<Field>:` prefixes and captures each field's value
    (which may span lines until the next field begins).
    """
    field_labels = {label: key for key, label in RETURN_FIELDS.items()}
    label_pattern = "|".join(re.escape(l) for l in field_labels)
    field_re = re.compile(rf"^\s*[-*]?\s*({label_pattern})\s*:\s*(.*)$", re.IGNORECASE)

    fields = {}
    current_key = None
    current_buf = []

    def flush():
        if current_key is not None:
            fields[current_key] = "\n".join(current_buf).strip()

    for raw_line in text.splitlines():
        line = _strip_marker(raw_line) if False else raw_line
        m = field_re.match(line)
        if m:
            flush()
            label = m.group(1)
            current_key = field_labels[label.title() if label.title() in field_labels else label]
            # Case-insensitive label match: find the right key
            for lbl, key in field_labels.items():
                if lbl.lower() == label.lower():
                    current_key = key
                    break
            current_buf = [m.group(2).strip()] if m.group(2).strip() else []
        else:
            if current_key is not None:
                current_buf.append(raw_line)

    flush()

    # Post-process: split files_changed into a list if comma-separated
    if "files_changed" in fields and fields["files_changed"]:
        val = fields["files_changed"]
        if val.lower() == "none":
            fields["files_changed"] = []
        elif "," in val:
            fields["files_changed"] = [s.strip() for s in val.split(",") if s.strip()]
        else:
            fields["files_changed"] = [val] if val else []

    return fields


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured fields from a sub-agent reply.",
    )
    parser.add_argument(
        "--file", default=None,
        help="Path to a file containing the reply (default: read from stdin).",
    )
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    fields = parse_return(text)

    missing = [k for k in RETURN_REQUIRED if not fields.get(k)]
    if missing:
        print(
            f"parse_return.py: missing required field(s): {', '.join(sorted(missing))}",
            file=sys.stderr,
        )

    print(json.dumps(fields, indent=2))

    # IF is load-bearing — exit non-zero if absent so callers can branch on it.
    if "if_easier" in missing:
        sys.exit(3)


if __name__ == "__main__":
    main()
