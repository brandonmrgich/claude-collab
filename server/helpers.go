// Minimal page shell. One stylesheet, one nav. No claims of
// grandeur; this is a local reading surface.
package main

const pageCSS = `
body { font-family: sans-serif; margin: 40px auto; max-width: 820px; padding: 0 24px; color: #222; line-height: 1.55; }
h1 { color: #000080; margin-bottom: 8px; }
h2 { color: #000080; margin-top: 32px; }
nav { margin-bottom: 16px; font-size: 13px; }
nav a { color: #000080; margin-right: 14px; }
code { background: #f4f0e4; padding: 1px 4px; border-radius: 3px; font-size: 90%; }
pre { background: #f4f0e4; padding: 12px 14px; border-radius: 4px; overflow-x: auto; }
pre code { background: none; padding: 0; }
.sub { color: #666; margin-bottom: 28px; font-size: 14px; }
.muted { color: #888; }
table { border-collapse: collapse; margin: 16px 0; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; }
th { background: #f4f0e4; }
ul.essays { list-style: none; padding: 0; margin: 0; }
ul.essays li { padding: 10px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; gap: 20px; align-items: baseline; }
ul.essays li:last-child { border-bottom: none; }
ul.essays a { color: #000080; font-weight: bold; text-decoration: none; font-size: 16px; }
ul.essays a:hover { text-decoration: underline; }
.date { color: #666; font-size: 13px; white-space: nowrap; font-variant-numeric: tabular-nums; }
.wiki-md { margin-top: 24px; }
.wiki-md h2 { margin-top: 28px; }
.wiki-md blockquote { margin: 0 0 16px; padding: 0 14px; color: #555; border-left: 3px solid #d6d0be; }
`

func pageHead(title string) string {
	return `<!DOCTYPE html>
<html><head><title>` + htmlEscape(title) + ` — claude-collab</title>
<style>` + pageCSS + `</style>
</head><body>
<nav><a href="/essays">Essays</a><a href="/users/steve/general">Steve</a></nav>
`
}

func pageFoot() string {
	return `</body></html>`
}

func htmlEscape(s string) string {
	out := ""
	for _, r := range s {
		switch r {
		case '&':
			out += "&amp;"
		case '<':
			out += "&lt;"
		case '>':
			out += "&gt;"
		case '"':
			out += "&quot;"
		case '\'':
			out += "&#39;"
		default:
			out += string(r)
		}
	}
	return out
}
