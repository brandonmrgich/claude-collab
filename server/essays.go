// Essay list + single-essay renderer. The two faces of the
// essay format: scan the collection, drop into one, read with
// inline comments enabled.
package main

import (
	"bufio"
	"fmt"
	"html"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// EssaysDir is the directory scanned for *.md essays. Set from
// the --essays flag in main(); paths are resolved relative to
// the process's cwd.
var EssaysDir string

type essayEntry struct {
	Slug    string
	File    string
	Title   string
	ModTime time.Time
}

// HandleEssaysList serves /essays — the landing list.
func HandleEssaysList(w http.ResponseWriter, r *http.Request) {
	entries := loadEssays(EssaysDir)
	sort.Slice(entries, func(i, j int) bool {
		return entries[i].ModTime.After(entries[j].ModTime)
	})

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	fmt.Fprint(w, pageHead("Essays"))
	fmt.Fprint(w, `<h1>Essays</h1>`)
	fmt.Fprintf(w, `<p class="sub">Reading the files in <code>%s</code>. Click any title to read with inline comments.</p>`,
		html.EscapeString(EssaysDir))
	fmt.Fprint(w, `<ul class="essays">`)
	if len(entries) == 0 {
		fmt.Fprint(w, `<li class="muted">No essays found. Add a *.md file to the essays directory.</li>`)
	}
	for _, e := range entries {
		t := e.ModTime.Local().Format("Jan 2, 2006 · 3:04 PM")
		fmt.Fprintf(w,
			`<li><a href="/essays/%s">%s</a><span class="date">%s</span></li>`,
			html.EscapeString(e.File),
			html.EscapeString(e.Title),
			html.EscapeString(t),
		)
	}
	fmt.Fprint(w, `</ul>`)
	fmt.Fprint(w, pageFoot())
}

// HandleEssayView serves /essays/<filename> — renders one
// markdown file with the inline-comment widget injected.
func HandleEssayView(w http.ResponseWriter, r *http.Request) {
	name := strings.TrimPrefix(r.URL.Path, "/essays/")
	if name == "" {
		http.Redirect(w, r, "/essays", http.StatusFound)
		return
	}
	if !strings.HasSuffix(name, ".md") || strings.Contains(name, "/") || strings.Contains(name, "..") {
		http.Error(w, "Invalid essay name", http.StatusBadRequest)
		return
	}
	abs := filepath.Join(EssaysDir, name)
	body, err := os.ReadFile(abs)
	if err != nil {
		http.Error(w, "Not found: "+name, http.StatusNotFound)
		return
	}

	title := extractTitle(abs)
	if title == "" {
		title = strings.TrimSuffix(name, ".md")
	}

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	fmt.Fprint(w, pageHead(title))
	fmt.Fprintf(w, `<p><a href="/essays">&larr; All essays</a></p>`)
	fmt.Fprint(w, `<div class="wiki-md">`)
	fmt.Fprint(w, renderMarkdown(string(body)))
	fmt.Fprint(w, `</div>`)
	fmt.Fprint(w, ArticleCommentsJS)
	fmt.Fprint(w, pageFoot())
}

func loadEssays(dir string) []essayEntry {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil
	}
	out := make([]essayEntry, 0, len(entries))
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		name := e.Name()
		if !strings.HasSuffix(name, ".md") {
			continue
		}
		info, err := e.Info()
		if err != nil {
			continue
		}
		path := filepath.Join(dir, name)
		title := extractTitle(path)
		if title == "" {
			title = strings.TrimSuffix(name, ".md")
		}
		out = append(out, essayEntry{
			Slug:    strings.TrimSuffix(name, ".md"),
			File:    name,
			Title:   title,
			ModTime: info.ModTime(),
		})
	}
	return out
}

// extractTitle returns the first "# " heading in the file, or
// "" if none is present in the first ~10 lines.
func extractTitle(path string) string {
	f, err := os.Open(path)
	if err != nil {
		return ""
	}
	defer f.Close()
	scanner := bufio.NewScanner(f)
	lines := 0
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if strings.HasPrefix(line, "# ") {
			return strings.TrimSpace(strings.TrimPrefix(line, "# "))
		}
		lines++
		if lines > 10 {
			break
		}
	}
	return ""
}
