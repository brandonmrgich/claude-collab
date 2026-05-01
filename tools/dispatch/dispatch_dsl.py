"""
Sub-agent dispatch DSL — shared grammar for dispatch + return.

The grammar lives in one place so dispatch.py (emitter) and
parse_return.py (extractor) agree on slot names, required-vs-
optional, and section ordering.

The DSL is two grammars wired together:

  DISPATCH  — what the orchestrator sends to the sub-agent.
              Required slots: churn, task, report_back.
              Optional slots: files, conformance.

  RETURN    — what the sub-agent sends back.
              Required fields: status, files_changed, if_easier.
              Optional fields: validation, out_of_scope.

The IF field is required-and-load-bearing — it is the
orchestrator's only window into sub-agent friction. Both
emitter and parser refuse to accept a return that lacks it.
"""

# ── Section headers (canonical wording; emitter + parser both pin these) ──

DISPATCH_SECTIONS = {
    "churn": "## Recent churn",
    "task": "## Task",
    "files": "## Files in scope",
    "conformance": "## Validation requirement",
    "report_back": "## Report-back contract",
}

RETURN_FIELDS = {
    "status": "Status",            # required: success | partial | blocked
    "files_changed": "Files changed",  # required
    "validation": "Validation",     # optional
    "if_easier": "IF",              # required: "I could have done this more easily IF..."
    "out_of_scope": "Out-of-scope",  # optional
}

# ── Required-slot enforcement ──

DISPATCH_REQUIRED = {"churn", "task"}
RETURN_REQUIRED = {"status", "files_changed", "if_easier"}

# ── The fixed text of the report-back contract ──

REPORT_BACK_TEMPLATE = """\
Reply with these fields, each on its own line, in this order:

- Status: success | partial | blocked
- Files changed: <comma-separated list, or "none">
- Validation: <output of any tests/checks run, or "none">
- IF: I could have done this more easily IF... <REQUIRED — name the
  single biggest friction you hit, even if small. Tooling gap, doc
  ambiguity, missing context, naming collision — any axis. Do NOT
  omit this field.>
- Out-of-scope: <anything you noticed but did not act on, or "none">"""

CONFORMANCE_TEMPLATE = """\
After implementation, run `ops/check-conformance` from the repo root
and include the green/red result in the Validation field. Do not
report success without running it."""
