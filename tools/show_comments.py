#!/usr/bin/env python3
"""
show_comments.py — render a claude-collab essay with inline reader notes.

Usage:
    python show_comments.py random037
    python show_comments.py random037.md
    python show_comments.py /full/path/to/random037.md

Paragraph indices are determined by fetching the rendered HTML from the
claude-collab server (localhost:9100) and replicating the browser widget's
counting rule: collect all <p> and <li> elements inside .wiki-md, then
skip any <li> that directly contains a <p> child (loose lists).  This is
the same querySelectorAll('p, li') + filter the JS widget uses, so index
N in this tool matches index N in the browser.

Falls back to a raw-markdown split on \n\n if the server is unreachable
(indices may diverge for code blocks, list items, etc.).
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from html.parser import HTMLParser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_timestamp(ts):
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


# ---------------------------------------------------------------------------
# Path → URL mapping
# ---------------------------------------------------------------------------

STEVE_ROOT = os.path.expanduser("~/showell_repos/claude-steve")
ESSAYS_DIR = os.path.expanduser("~/showell_repos/claude-collab/essays")
STEVE_BASE = os.path.expanduser("~/showell_repos/claude-collab/users/steve")
SERVER = "http://localhost:9100"


def path_to_url(abs_path):
    """Return the server URL path for abs_path, or None if unmapped."""
    name = os.path.basename(abs_path)
    if not name.endswith(".md"):
        return None

    parent = os.path.dirname(abs_path)

    if os.path.realpath(parent) == os.path.realpath(STEVE_ROOT):
        return f"/steve/{name}"

    if os.path.realpath(parent) == os.path.realpath(ESSAYS_DIR):
        return f"/essays/{name}"

    # /users/steve/<subdir>/<name>.md
    try:
        rel = os.path.relpath(parent, STEVE_BASE)
        if not rel.startswith(".."):
            parts = rel.split(os.sep)
            if len(parts) == 1:
                return f"/users/steve/{parts[0]}/{name}"
    except ValueError:
        pass

    return None


# ---------------------------------------------------------------------------
# HTML parser: replicate the browser widget's paragraph list
# ---------------------------------------------------------------------------

class WikiMDParser(HTMLParser):
    """
    Collect <p> and <li> elements inside .wiki-md, in document order.
    Tracks which <li> elements have a direct <p> child so they can be
    excluded (matching the JS: if el.tagName === 'LI' &&
    el.querySelector(':scope > p')) return;).

    Each element is stored as a dict:
        tag   — 'p' or 'li'
        depth — nesting depth at open tag (used to identify direct children)
        text  — concatenated text content
    """

    def __init__(self):
        super().__init__()
        self.in_wiki_md = False
        self.wiki_md_depth = 0
        self.depth = 0
        # (tag, element_index | None)
        self.tag_stack = []
        # list of {tag, depth, text}
        self.elements = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "div" and attrs_dict.get("class") == "wiki-md":
            self.in_wiki_md = True
            self.wiki_md_depth = self.depth

        self.depth += 1

        if self.in_wiki_md and tag in ("p", "li"):
            idx = len(self.elements)
            self.elements.append({"tag": tag, "depth": self.depth, "text": ""})
            self.tag_stack.append((tag, idx))
        else:
            self.tag_stack.append((tag, None))

    def handle_endtag(self, tag):
        self.depth -= 1
        if self.tag_stack:
            self.tag_stack.pop()
        if self.in_wiki_md and self.depth <= self.wiki_md_depth:
            self.in_wiki_md = False

    def handle_data(self, data):
        if not self.in_wiki_md:
            return
        # Accumulate text into the nearest p/li ancestor.
        for t, idx in reversed(self.tag_stack):
            if idx is not None:
                self.elements[idx]["text"] += data
                break

    def handle_entityref(self, name):
        # Named entities like &mdash; — treat as a space for display.
        self.handle_data(" ")

    def handle_charref(self, name):
        # Numeric character references.
        try:
            if name.startswith("x"):
                ch = chr(int(name[1:], 16))
            else:
                ch = chr(int(name))
            self.handle_data(ch)
        except (ValueError, OverflowError):
            self.handle_data("?")


def paragraphs_from_html(html):
    """
    Return a list of text strings, one per browser-counted paragraph.
    Index i in the returned list == para_index i in the browser widget.
    """
    parser = WikiMDParser()
    parser.feed(html)

    # Identify <li> elements that have a direct <p> child.
    # "Direct" means the <p>'s depth == li's depth + 1.
    li_with_direct_p = set()
    for elem in parser.elements:
        if elem["tag"] == "p" and elem["depth"] > 1:
            # Walk back up the element list to find the nearest enclosing li.
            for prev in reversed(parser.elements[: parser.elements.index(elem)]):
                if prev["tag"] == "li" and prev["depth"] == elem["depth"] - 1:
                    li_with_direct_p.add(parser.elements.index(prev))
                    break
                if prev["depth"] < elem["depth"] - 1:
                    break  # left the subtree without finding an li parent

    paras = []
    for i, elem in enumerate(parser.elements):
        if elem["tag"] == "li" and i in li_with_direct_p:
            continue
        paras.append(elem["text"].strip())

    return paras


# ---------------------------------------------------------------------------
# Fallback: raw markdown split
# ---------------------------------------------------------------------------

def paragraphs_from_markdown(content):
    """
    Rough fallback when the server is unreachable.  Indices will diverge
    for list items and fenced code blocks.
    """
    raw = content.split("\n\n")
    return [p.rstrip("\n") for p in raw]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print("Usage: show_comments.py <path-to-md-file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    if not path.endswith(".md"):
        path = path + ".md"

    if not os.path.isabs(path):
        essays_dir = os.path.expanduser("~/showell_repos/claude-steve")
        path = os.path.join(essays_dir, path)

    if not os.path.exists(path):
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Load comments.
    comments_path = path + ".comments.json"
    comments_by_para = {}
    if os.path.exists(comments_path):
        with open(comments_path) as f:
            data = json.load(f)
        for c in data.get("comments", []):
            idx = c["para_index"]
            comments_by_para.setdefault(idx, []).append(c)

    # Try to get paragraph list from server-rendered HTML.
    url_path = path_to_url(path)
    paragraphs = None
    using_fallback = False

    if url_path:
        url = SERVER + url_path
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            paragraphs = paragraphs_from_html(html)
        except (urllib.error.URLError, OSError):
            pass

    if paragraphs is None:
        using_fallback = True
        with open(path) as f:
            content = f.read()
        paragraphs = paragraphs_from_markdown(content)

    if using_fallback:
        print(
            "WARNING: localhost:9100 not reachable — using raw-markdown fallback.\n"
            "Paragraph indices may not match the browser widget for documents\n"
            "with code blocks, list items, or horizontal rules.\n",
            file=sys.stderr,
        )

    # Render.
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
