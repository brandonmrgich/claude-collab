// claude-collab server: a minimal web app that renders your
// markdown essays with paragraph-anchored inline comments.
//
// Runs on localhost. No auth. Comments are stored as sibling
// JSON files (foo.md → foo.md.comments.json). No database.
//
// Usage:
//
//	go run .
//
// Then visit http://localhost:9100.
package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
)

func main() {
	var port int
	var essaysDir, steveDir string
	flag.IntVar(&port, "port", 9100, "HTTP port")
	flag.StringVar(&essaysDir, "essays", "../essays", "published essays dir (relative paths resolved from cwd)")
	flag.StringVar(&steveDir, "steve", "../users/steve/general", "Steve's real-time essays dir")
	flag.Parse()

	EssaysDir = essaysDir
	SteveDir = steveDir

	mux := http.NewServeMux()
	mux.HandleFunc("/", handleRoot)
	mux.HandleFunc("/essays", HandleEssaysList)
	mux.HandleFunc("/essays/", HandleEssayView)
	mux.HandleFunc("/users/steve/general", HandleSteveList)
	mux.HandleFunc("/users/steve/general/", HandleSteveView)
	mux.HandleFunc("/article-comments", HandleArticleComments)

	addr := fmt.Sprintf("localhost:%d", port)
	log.Printf("claude-collab: serving http://%s  (essays: %s, steve: %s)", addr, essaysDir, steveDir)
	log.Fatal(http.ListenAndServe(addr, mux))
}

func handleRoot(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	http.Redirect(w, r, "/essays", http.StatusFound)
}
