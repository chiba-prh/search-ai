#!/usr/bin/env python3
"""Preview server — Markdown viewer + source management UI."""

import http.server
import json
import os
import sys
import urllib.parse
from pathlib import Path

import markdown
import yaml

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

PORT = int(os.environ.get("PORT", 9090))
PROJECT_DIR = Path(__file__).resolve().parent.parent
SERVE_DIR = (PROJECT_DIR / os.environ.get("OUTPUT_DIR", "output")).resolve()
SOURCES_FILE = PROJECT_DIR / "sources.yml"

# ---------------------------------------------------------------------------
# Sources helpers
# ---------------------------------------------------------------------------

def load_sources() -> list[dict]:
    if not SOURCES_FILE.exists():
        return []
    data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8")) or {}
    return data.get("sources", [])


def save_sources(sources: list[dict]):
    SOURCES_FILE.write_text(
        yaml.dump({"sources": sources}, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# HTML templates
# ---------------------------------------------------------------------------

PAGE_STYLE = """\
:root {
  --bg: #1e1e2e; --surface: #262637; --text: #cdd6f4; --text-muted: #a6adc8;
  --accent: #f5c2e7; --link: #89b4fa; --border: #45475a; --star: #f9e2af;
  --tag-bg: #313244; --quote-border: #89b4fa; --green: #a6e3a1; --red: #f38ba8;
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
  background:var(--bg); color:var(--text);
  font-family:'Segoe UI','Hiragino Sans','Meiryo',sans-serif;
  line-height:1.8; padding:40px 20px; max-width:900px; margin:0 auto;
}
h1 { font-size:1.8em; color:var(--accent); border-bottom:2px solid var(--border); padding-bottom:12px; margin-bottom:24px; }
h2 { font-size:1.3em; color:#cba6f7; margin-top:36px; margin-bottom:8px; }
h2+p em { color:var(--text-muted); font-size:0.9em; }
table { border-collapse:collapse; margin:16px 0; font-size:0.92em; width:100%; }
th,td { border:1px solid var(--border); padding:8px 14px; text-align:left; }
th { background:var(--surface); color:var(--accent); font-weight:600; }
td { background:var(--bg); }
a { color:var(--link); text-decoration:none; } a:hover { text-decoration:underline; }
blockquote { background:var(--surface); border-left:4px solid var(--quote-border); padding:12px 20px; margin:16px 0; border-radius:0 8px 8px 0; color:var(--text-muted); font-style:italic; }
ul { margin:12px 0; padding-left:24px; } li { margin:6px 0; line-height:1.7; }
code { background:var(--tag-bg); padding:2px 8px; border-radius:4px; font-size:0.88em; color:var(--star); }
hr { border:none; border-top:1px solid var(--border); margin:32px 0; }
p { margin:10px 0; } strong { color:#f5e0dc; }
/* Source management */
.section { background:var(--surface); border-radius:12px; padding:20px 24px; margin-bottom:24px; }
.section-title { font-size:1.1em; color:var(--accent); margin-bottom:16px; display:flex; align-items:center; gap:8px; }
.source-item {
  display:flex; align-items:center; gap:12px; padding:10px 14px;
  border-radius:8px; margin-bottom:8px; background:var(--bg); border:1px solid var(--border);
}
.source-item.disabled { opacity:0.5; }
.source-name { flex:1; font-weight:600; }
.source-meta { color:var(--text-muted); font-size:0.85em; }
.badge { background:var(--tag-bg); color:var(--star); padding:2px 10px; border-radius:12px; font-size:0.8em; }
.toggle { cursor:pointer; font-size:1.3em; user-select:none; }
.btn-del { cursor:pointer; color:var(--red); background:none; border:none; font-size:1.1em; }
.btn-del:hover { color:#fff; }
/* Add form */
.add-form { display:none; margin-top:16px; }
.add-form.open { display:block; }
.add-btn { background:var(--link); color:#1e1e2e; border:none; padding:8px 20px; border-radius:8px; cursor:pointer; font-weight:600; font-size:0.95em; }
.add-btn:hover { opacity:0.85; }
.form-row { display:flex; gap:10px; margin-bottom:10px; flex-wrap:wrap; }
.form-row input, .form-row select {
  background:var(--bg); color:var(--text); border:1px solid var(--border);
  padding:8px 12px; border-radius:6px; font-size:0.95em;
}
.form-row input { flex:1; min-width:120px; }
.form-row select { min-width:80px; }
/* Article list */
/* Article link on home */
.article-link {
  display:flex; align-items:center; padding:12px 16px; border-radius:8px; margin-bottom:6px;
  background:var(--bg); border:1px solid var(--border); color:var(--link);
  text-decoration:none; transition:background 0.15s; font-weight:600;
}
.article-link:hover { background:var(--surface); text-decoration:none; }
.article-count { margin-left:auto; color:var(--text-muted); font-size:0.85em; font-weight:400; }
/* Article page — toggle items */
.article-item { margin-bottom:8px; }
.article-header {
  display:flex; align-items:flex-start; gap:10px; padding:14px 16px;
  background:var(--bg); border:1px solid var(--border); border-radius:8px;
  cursor:pointer; user-select:none; transition:background 0.15s;
}
.article-header:hover { background:var(--surface); }
.acc-arrow { font-size:0.7em; transition:transform 0.2s; display:inline-block; margin-top:6px; }
.article-item.open .acc-arrow { transform:rotate(90deg); }
.article-header-text { flex:1; }
.article-header-title { font-weight:600; font-size:1em; line-height:1.5; }
.article-header-meta { display:flex; gap:12px; margin-top:4px; font-size:0.82em; }
.meta-source { color:var(--star); background:var(--tag-bg); padding:1px 8px; border-radius:10px; }
.meta-date { color:var(--text-muted); }
.article-detail {
  display:none; padding:16px 20px; margin:0 0 4px 0;
  background:var(--surface); border:1px solid var(--border);
  border-top:none; border-radius:0 0 8px 8px;
}
.article-item.open .article-detail { display:block; }
.article-item.open .article-header { border-radius:8px 8px 0 0; }
"""

HOME_JS = """\
function toggleSource(idx) {
  fetch('/api/sources', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action: 'toggle', index: idx})
  }).then(() => location.reload());
}
function deleteSource(idx, name) {
  if (!confirm('「' + name + '」を削除しますか？\\nこの操作は元に戻せません。')) return;
  fetch('/api/sources', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action: 'delete', index: idx})
  }).then(() => location.reload());
}
function showAddForm() {
  document.getElementById('add-form').classList.toggle('open');
}
function addSource(e) {
  e.preventDefault();
  const f = e.target;
  fetch('/api/sources', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      action: 'add',
      name: f.name_.value,
      url: f.url_.value,
      count: parseInt(f.count_.value) || 2,
      category: f.category_.value || 'AI'
    })
  }).then(() => location.reload());
}
"""


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------

class AppHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        path = urllib.parse.unquote(self.path)

        if path == "/" or path == "":
            self._serve_home()
        elif path == "/api/sources":
            self._api_get_sources()
        elif path.startswith("/view/") and path.endswith(".md"):
            # ASCII-safe alias: /view/AI/2026-04-13.md -> Web記事/AI/2026-04-13.md
            rest = path[len("/view/"):]
            for d in sorted(SERVE_DIR.iterdir()):
                if d.is_dir():
                    candidate = d / rest
                    if candidate.is_file():
                        self._serve_markdown(candidate)
                        return
            self.send_error(404)
        elif path.endswith(".md"):
            file_path = SERVE_DIR / path.lstrip("/")
            if file_path.is_file():
                self._serve_markdown(file_path)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def do_POST(self):
        path = urllib.parse.unquote(self.path)
        if path == "/api/sources":
            self._api_post_sources()
        else:
            self.send_error(404)

    # --- Home ---
    def _serve_home(self):
        sources = load_sources()
        md_files = sorted(SERVE_DIR.rglob("*.md"), reverse=True)

        # Build source list HTML
        source_items = []
        for i, s in enumerate(sources):
            enabled = s.get("enabled", True)
            cls = "" if enabled else " disabled"
            icon = "✅" if enabled else "☐"
            source_items.append(f"""
            <div class="source-item{cls}">
              <span class="toggle" onclick="toggleSource({i})">{icon}</span>
              <span class="source-name">{_esc(s.get('name',''))}</span>
              <span class="badge">{_esc(s.get('category','AI'))}</span>
              <span class="source-meta">{s.get('count',2)}件</span>
              <span class="source-meta">{_esc(s.get('url',''))}</span>
              <button class="btn-del" onclick="deleteSource({i},'{_esc(s.get('name',''))}')">✕</button>
            </div>""")

        # Build article list HTML — simple links
        article_items = []
        for f in md_files:
            # Use ASCII-safe /view/ path to avoid Japanese URL issues
            category = f.parent.name  # e.g. "AI"
            date_label = f.stem
            view_path = f"/view/{category}/{f.name}"
            titles = _extract_titles(f)
            count = len(titles)
            article_items.append(
                f'<a class="article-link" href="{view_path}">📅 {_esc(date_label)}<span class="article-count">{count}件</span></a>'
            )

        body = f"""
        <h1>AI Daily Digest</h1>

        <div class="section">
          <div class="section-title">📡 ソース管理</div>
          {''.join(source_items) or '<p style="color:var(--text-muted)">ソースがありません</p>'}
          <div style="margin-top:12px">
            <button class="add-btn" onclick="showAddForm()">＋ ソースを追加</button>
          </div>
          <div id="add-form" class="add-form">
            <form onsubmit="addSource(event)">
              <div class="form-row">
                <input name="name_" placeholder="サイト名 (例: TechCrunch)" required>
                <input name="url_" placeholder="URL (例: techcrunch.com/category/ai)" required>
              </div>
              <div class="form-row">
                <input name="count_" type="number" value="2" min="1" max="10" style="max-width:80px" title="取得件数">
                <input name="category_" placeholder="カテゴリ (例: AI, Tech)" value="AI">
                <button class="add-btn" type="submit">追加</button>
              </div>
            </form>
          </div>
        </div>

        <div class="section">
          <div class="section-title">📄 記事一覧</div>
          {''.join(article_items) or '<p style="color:var(--text-muted)">まだ記事がありません</p>'}
        </div>

        """

        html = _page("AI Daily Digest", body, HOME_JS)
        self._send_html(html)

    # --- API ---
    def _api_get_sources(self):
        data = json.dumps(load_sources(), ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _api_post_sources(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        sources = load_sources()
        action = body.get("action")

        if action == "add":
            sources.append({
                "name": body["name"],
                "url": body["url"],
                "count": body.get("count", 2),
                "category": body.get("category", "AI"),
                "enabled": True,
            })
        elif action == "toggle":
            idx = body["index"]
            if 0 <= idx < len(sources):
                sources[idx]["enabled"] = not sources[idx].get("enabled", True)
        elif action == "delete":
            idx = body["index"]
            if 0 <= idx < len(sources):
                sources.pop(idx)

        save_sources(sources)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    # --- Article page — title list with toggle detail ---
    def _serve_markdown(self, file_path: Path):
        md_text = file_path.read_text(encoding="utf-8")
        if md_text.startswith("---"):
            parts = md_text.split("---", 2)
            if len(parts) >= 3:
                md_text = parts[2]

        # Split markdown into per-article sections (split on ## )
        sections = re.split(r'(?=^## )', md_text, flags=re.MULTILINE)
        titles = _extract_titles(file_path)

        items_html = []
        for i, section in enumerate(sections):
            section = section.strip()
            if not section.startswith("## "):
                continue  # skip header / preamble
            # Render this section
            rendered = markdown.markdown(section, extensions=["tables", "fenced_code"])
            t = titles[len(items_html)] if len(items_html) < len(titles) else {}
            title = t.get("title", "記事")
            url = t.get("url", "")
            source = t.get("source", "")
            published = t.get("published", "")

            items_html.append(f"""
            <div class="article-item">
              <div class="article-header" onclick="this.parentElement.classList.toggle('open')">
                <span class="acc-arrow">▶</span>
                <div class="article-header-text">
                  <div class="article-header-title">{_esc(title)}</div>
                  <div class="article-header-meta">
                    {'<span class="meta-source">' + _esc(source) + '</span>' if source else ''}
                    {'<span class="meta-date">' + _esc(published) + '</span>' if published else ''}
                  </div>
                </div>
              </div>
              <div class="article-detail">{rendered}</div>
            </div>""")

        date_label = file_path.stem
        body = f"""
        <p style="margin-bottom:20px"><a href="/">← ホームに戻る</a></p>
        <h1>📅 {_esc(date_label)}</h1>
        <p style="color:var(--text-muted);margin-bottom:20px">{len(items_html)}件の記事</p>
        {''.join(items_html)}
        """

        js = """
        // Open article if hash matches
        if (location.hash) {
          const idx = parseInt(location.hash.slice(1));
          const items = document.querySelectorAll('.article-item');
          if (items[idx]) items[idx].classList.add('open');
        }
        """
        html = _page(date_label, body, js)
        self._send_html(html)

    # --- Helpers ---
    def _send_html(self, html: str):
        data = html.encode("utf-8")
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass  # client disconnected — ignore

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            self.close_connection = True

    def log_message(self, fmt, *args):
        pass  # suppress request logs


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

import re

def _extract_titles(md_path: Path) -> list[dict]:
    """Extract h2 titles, URLs, sources, and dates from a markdown file."""
    text = md_path.read_text(encoding="utf-8")
    titles = []
    current = None
    for line in text.split("\n"):
        if line.startswith("## "):
            title = re.sub(r"^## \d+\.\s*", "", line).strip()
            current = {"title": title, "url": "", "source": "", "published": ""}
            titles.append(current)
        elif current:
            if "**URL**" in line:
                m = re.search(r'\[https?://[^\]]+\]\((https?://[^)]+)\)', line)
                if m:
                    current["url"] = m.group(1)
            elif "**Source**" in line:
                m = re.search(r'\*\*Source\*\*\s*\|\s*(.+?)\s*\|', line)
                if m:
                    current["source"] = m.group(1).strip()
            elif "**Published**" in line:
                m = re.search(r'\*\*Published\*\*\s*\|\s*(.+?)\s*\|', line)
                if m:
                    current["published"] = m.group(1).strip()
    return titles


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _page(title: str, body: str, extra_js: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<style>{PAGE_STYLE}</style>
</head>
<body>
{body}
<script>{extra_js}</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    SERVE_DIR.mkdir(parents=True, exist_ok=True)
    server = http.server.HTTPServer(("0.0.0.0", PORT), AppHandler)
    print(f"🌐 Preview server running at http://localhost:{PORT}")
    print(f"   Serving files from: {SERVE_DIR}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
