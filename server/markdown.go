// Markdown rendering for claude-collab essays. Plain goldmark
// with CommonMark + GFM extensions, no Zulip-style mentions or
// channel links (those live in angry-gopher's version).
package main

import (
	"bytes"

	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/extension"
	"github.com/yuin/goldmark/renderer/html"
)

var md = goldmark.New(
	goldmark.WithRendererOptions(html.WithUnsafe()),
	goldmark.WithExtensions(extension.GFM),
)

func renderMarkdown(source string) string {
	var buf bytes.Buffer
	if err := md.Convert([]byte(source), &buf); err != nil {
		return "<pre>" + source + "</pre>"
	}
	return buf.String()
}
