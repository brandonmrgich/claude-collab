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

// EssaysDir is the directory for the main /essays collection.
// SteveBaseDir is the parent of Steve's public subdirs (general,
// random, ...); each subdir is served at /users/steve/<subdir>.
// SteveRootDir is the flat private notes dir (claude-steve
// repo), served at /steve/.
// ClaudeClaudeDir is the peer-to-peer Claude-to-Claude exchange
// directory, served at /claude-claude/ in conversation order.
// All set from flags in main(); paths are resolved relative to
// the process's cwd.
var (
	EssaysDir       string
	SteveBaseDir    string
	SteveRootDir    string
	ClaudeClaudeDir string
)

type essayEntry struct {
	Slug    string
	File    string
	Title   string
	ModTime time.Time
}

// HandleEssaysList serves /essays — the published collection.
func HandleEssaysList(w http.ResponseWriter, r *http.Request) {
	renderList(w, EssaysDir, "/essays", "Essays",
		"Published essays. Click any title to read with inline comments.",
		sortByModTimeDesc)
}

// HandleEssayView serves /essays/<filename>.md with inline
// comments enabled — readers (Steve, Brandon, anyone) annotate
// freely. Comment files are sibling JSON.
func HandleEssayView(w http.ResponseWriter, r *http.Request) {
	name := strings.TrimPrefix(r.URL.Path, "/essays/")
	renderView(w, r, EssaysDir, "/essays", name, true)
}

// HandleClaudeClaudeList serves /claude-claude — peer-to-peer
// Claude exchange. Chronological (oldest first) so the
// conversation reads in natural order top-to-bottom.
func HandleClaudeClaudeList(w http.ResponseWriter, r *http.Request) {
	renderList(w, ClaudeClaudeDir, "/claude-claude",
		"Claude ↔ Claude",
		"Peer-to-peer exchanges between Claudes working with different humans. Read top-to-bottom. Annotations enabled.",
		sortByModTimeAsc)
}

// HandleClaudeClaudeView serves /claude-claude/<filename>.md
// with inline comments enabled (so Steve can annotate).
func HandleClaudeClaudeView(w http.ResponseWriter, r *http.Request) {
	name := strings.TrimPrefix(r.URL.Path, "/claude-claude/")
	renderView(w, r, ClaudeClaudeDir, "/claude-claude", name, true)
}

// HandleSteveAny serves any subdir under /users/steve/. URL
// shapes:
//
//	/users/steve/                  → redirect to /users/steve/general
//	/users/steve/<subdir>          → list of *.md files in that subdir
//	/users/steve/<subdir>/         → same as above
//	/users/steve/<subdir>/<name>.md → render that file with inline comments
//
// <subdir> must be a simple identifier (letters, digits, -_);
// `.` and `..` are refused. Subdirs that don't exist on disk
// return 404. No auto-create — subdirs are provisioned by the
// user or a sibling memory convention.
func HandleSteveAny(w http.ResponseWriter, r *http.Request) {
	rest := strings.TrimPrefix(r.URL.Path, "/users/steve/")
	if rest == "" {
		http.Redirect(w, r, "/users/steve/general", http.StatusFound)
		return
	}
	parts := strings.SplitN(rest, "/", 2)
	subdir := parts[0]
	if !isValidSteveSubdir(subdir) {
		http.Error(w, "Invalid subdir", http.StatusBadRequest)
		return
	}
	dir := filepath.Join(SteveBaseDir, subdir)
	if info, err := os.Stat(dir); err != nil || !info.IsDir() {
		http.Error(w, "Subdir not found: "+subdir, http.StatusNotFound)
		return
	}
	urlPrefix := "/users/steve/" + subdir
	if len(parts) == 1 || parts[1] == "" {
		renderList(w, dir, urlPrefix, "Steve — "+subdir,
			"Drafts and working notes in "+subdir+"/. Some of these graduate to /essays; most don't.",
			sortByModTimeDesc)
		return
	}
	renderView(w, r, dir, urlPrefix, parts[1], true)
}

// HandleSteveRootList serves /steve — the list of Steve's
// private flat notes in the claude-steve repo. Inline comments
// enabled on the rendered views (they're Steve's; he annotates
// them).
func HandleSteveRootList(w http.ResponseWriter, r *http.Request) {
	renderList(w, SteveRootDir, "/steve", "Steve — private notes",
		"Day-to-day notes and essays from the claude-steve repo. Not public; annotations enabled.",
		sortByModTimeDesc)
}

// HandleSteveRootView serves:
//
//	/steve/<name>.md            → render flat note from claude-steve/
//	/steve/<subdir>/            → list *.md files in claude-steve/<subdir>/
//	/steve/<subdir>/<name>.md   → render that file
//
// <subdir> must be a simple identifier (same rule as
// `/users/steve/<subdir>/`).
func HandleSteveRootView(w http.ResponseWriter, r *http.Request) {
	rest := strings.TrimPrefix(r.URL.Path, "/steve/")
	parts := strings.SplitN(rest, "/", 2)

	// Flat-file case: no slash, render directly from claude-steve/.
	if len(parts) == 1 {
		renderView(w, r, SteveRootDir, "/steve", parts[0], true)
		return
	}

	// Subdir case: validate, look up, list-or-view.
	subdir := parts[0]
	if !isValidSteveSubdir(subdir) {
		http.Error(w, "Invalid subdir", http.StatusBadRequest)
		return
	}
	dir := filepath.Join(SteveRootDir, subdir)
	if info, err := os.Stat(dir); err != nil || !info.IsDir() {
		http.Error(w, "Subdir not found: "+subdir, http.StatusNotFound)
		return
	}
	urlPrefix := "/steve/" + subdir
	if parts[1] == "" {
		renderList(w, dir, urlPrefix, "Steve — "+subdir,
			"Working notes in claude-steve/"+subdir+"/.",
			sortByModTimeDesc)
		return
	}
	renderView(w, r, dir, urlPrefix, parts[1], true)
}

func isValidSteveSubdir(s string) bool {
	if s == "" || s == "." || s == ".." {
		return false
	}
	for _, c := range s {
		switch {
		case c >= 'a' && c <= 'z':
		case c >= 'A' && c <= 'Z':
		case c >= '0' && c <= '9':
		case c == '-' || c == '_':
		default:
			return false
		}
	}
	return true
}

// sortOrder picks the order of a rendered list. ModTimeDesc
// (newest first) is the default for /essays and /steve where
// you scan to find what's recent. ModTimeAsc (oldest first)
// fits a conversation read top-to-bottom — used for
// /claude-claude where letters thread chronologically.
type sortOrder int

const (
	sortByModTimeDesc sortOrder = iota
	sortByModTimeAsc
)

func renderList(w http.ResponseWriter, dir, urlPrefix, heading, sub string, order sortOrder) {
	entries := loadEssays(dir)
	sort.Slice(entries, func(i, j int) bool {
		if order == sortByModTimeAsc {
			return entries[i].ModTime.Before(entries[j].ModTime)
		}
		return entries[i].ModTime.After(entries[j].ModTime)
	})

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	fmt.Fprint(w, pageHead(heading))
	fmt.Fprintf(w, `<h1>%s</h1>`, html.EscapeString(heading))
	fmt.Fprintf(w, `<p class="sub">%s</p>`, html.EscapeString(sub))
	fmt.Fprint(w, `<ul class="essays">`)
	if len(entries) == 0 {
		fmt.Fprint(w, `<li class="muted">No essays found. Add a *.md file to the directory.</li>`)
	}
	for _, e := range entries {
		t := e.ModTime.Local().Format("Jan 2, 2006 · 3:04 PM")
		fmt.Fprintf(w,
			`<li><a href="%s/%s">%s</a><span class="date">%s</span></li>`,
			html.EscapeString(urlPrefix),
			html.EscapeString(e.File),
			html.EscapeString(e.Title),
			html.EscapeString(t),
		)
	}
	fmt.Fprint(w, `</ul>`)
	fmt.Fprint(w, pageFoot())
}

func renderView(w http.ResponseWriter, r *http.Request, dir, urlPrefix, name string, enableComments bool) {
	if name == "" {
		http.Redirect(w, r, urlPrefix, http.StatusFound)
		return
	}
	if !strings.HasSuffix(name, ".md") || strings.Contains(name, "/") || strings.Contains(name, "..") {
		http.Error(w, "Invalid essay name", http.StatusBadRequest)
		return
	}
	abs := filepath.Join(dir, name)
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
	fmt.Fprintf(w, `<p><a href="%s">&larr; Back</a></p>`, html.EscapeString(urlPrefix))
	fmt.Fprint(w, `<div class="wiki-md">`)
	fmt.Fprint(w, renderMarkdown(string(body)))
	fmt.Fprint(w, `</div>`)
	if enableComments {
		fmt.Fprint(w, ArticleCommentsJS)
	}
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
// "" if none is present in the first ~10 lines past any
// optional YAML front-matter block.
func extractTitle(path string) string {
	f, err := os.Open(path)
	if err != nil {
		return ""
	}
	defer f.Close()
	scanner := bufio.NewScanner(f)
	inFrontMatter := false
	sawFirstLine := false
	lines := 0
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if !sawFirstLine {
			sawFirstLine = true
			if line == "---" {
				inFrontMatter = true
				continue
			}
		}
		if inFrontMatter {
			if line == "---" {
				inFrontMatter = false
			}
			continue
		}
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
