#!/usr/bin/env python3
"""Build static HTML files for GitHub Pages from Markdown digests."""

import re
import sys
from pathlib import Path

import markdown
import yaml

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_DIR / "Web記事" / "AI"
DOCS_DIR = PROJECT_DIR / "docs"  # GitHub Pages serves from /docs
SOURCES_FILE = PROJECT_DIR / "sources.yml"

# ---------------------------------------------------------------------------
# Shared styles (same as preview_server.py)
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
.article-link {
  display:flex; align-items:center; padding:12px 16px; border-radius:8px; margin-bottom:6px;
  background:var(--bg); border:1px solid var(--border); color:var(--link);
  text-decoration:none; transition:background 0.15s; font-weight:600;
}
.article-link:hover { background:var(--surface); text-decoration:none; }
.article-count { margin-left:auto; color:var(--text-muted); font-size:0.85em; font-weight:400; }
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
.article-header-meta { display:flex; gap:12px; margin-top:4px; font-size:0.82em; flex-wrap:wrap; }
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _extract_titles(md_path: Path) -> list[dict]:
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


def load_sources() -> list[dict]:
    if not SOURCES_FILE.exists():
        return []
    data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8")) or {}
    return data.get("sources", [])


# ---------------------------------------------------------------------------
# Build functions
# ---------------------------------------------------------------------------

def build_article_page(md_file: Path) -> str:
    """Build HTML for a single article page."""
    md_text = md_file.read_text(encoding="utf-8")
    if md_text.startswith("---"):
        parts = md_text.split("---", 2)
        if len(parts) >= 3:
            md_text = parts[2]

    sections = re.split(r'(?=^## )', md_text, flags=re.MULTILINE)
    titles = _extract_titles(md_file)

    items_html = []
    for section in sections:
        section = section.strip()
        if not section.startswith("## "):
            continue
        rendered = markdown.markdown(section, extensions=["tables", "fenced_code"])
        t = titles[len(items_html)] if len(items_html) < len(titles) else {}
        title = t.get("title", "記事")
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

    date_label = md_file.stem
    body = f"""
    <p style="margin-bottom:20px"><a href="index.html">← ホームに戻る</a></p>
    <h1>📅 {_esc(date_label)}</h1>
    <p style="color:var(--text-muted);margin-bottom:20px">{len(items_html)}件の記事</p>
    {''.join(items_html)}
    """
    return _page(date_label, body)


def build_index_page(md_files: list[Path]) -> str:
    """Build the index (home) HTML page."""
    sources = load_sources()

    # Source list (read-only for static page)
    source_items = []
    for s in sources:
        enabled = s.get("enabled", True)
        cls = "" if enabled else " disabled"
        icon = "✅" if enabled else "☐"
        source_items.append(f"""
        <div class="source-item{cls}">
          <span style="font-size:1.3em">{icon}</span>
          <span class="source-name">{_esc(s.get('name', ''))}</span>
          <span class="badge">{_esc(s.get('category', 'AI'))}</span>
          <span class="source-meta">{s.get('count', 2)}件</span>
          <span class="source-meta">{_esc(s.get('url', ''))}</span>
        </div>""")

    # Article list
    article_items = []
    for f in md_files:
        date_label = f.stem
        titles = _extract_titles(f)
        count = len(titles)
        article_items.append(
            f'<a class="article-link" href="{date_label}.html">📅 {_esc(date_label)}'
            f'<span class="article-count">{count}件</span></a>'
        )

    body = f"""
    <h1>AI Daily Digest</h1>

    <div class="section">
      <div class="section-title">📡 ソース一覧（{len(sources)}サイト）</div>
      {''.join(source_items) or '<p style="color:var(--text-muted)">ソースがありません</p>'}
    </div>

    <div class="section">
      <div class="section-title">📄 記事一覧</div>
      {''.join(article_items) or '<p style="color:var(--text-muted)">まだ記事がありません</p>'}
    </div>
    """
    return _page("AI Daily Digest", body)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    if not SOURCE_DIR.exists():
        print(f"⚠️  ソースディレクトリが見つかりません: {SOURCE_DIR}")
        return

    md_files = sorted(SOURCE_DIR.glob("*.md"), reverse=True)
    print(f"📄 {len(md_files)} 件のMarkdownファイルを検出")

    # Build each article page
    for md_file in md_files:
        html = build_article_page(md_file)
        out = DOCS_DIR / f"{md_file.stem}.html"
        out.write_text(html, encoding="utf-8")
        titles = _extract_titles(md_file)
        print(f"  ✅ {out.name} ({len(titles)}件の記事)")

    # Build index page
    index_html = build_index_page(md_files)
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  ✅ index.html")

    print(f"\n🌐 静的サイトを {DOCS_DIR} に生成しました")


if __name__ == "__main__":
    main()
