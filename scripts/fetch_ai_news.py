#!/usr/bin/env python3
"""AI Daily Digest — RSS fetcher + Gemini summarizer.

Architecture:
  1. Pull RSS feeds directly from each source (feedparser) — no search delay
  2. Dedup against already-saved articles by URL
  3. For each new article, use Gemini to generate Japanese summary + tags
  4. Write to Web記事/AI/YYYY-MM-DD.md grouped by *published date*
"""

import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

import feedparser
import yaml

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
RETRY_DELAY = 5
MAX_ARTICLES_PER_SOURCE = 20  # safety cap

PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCES_FILE = PROJECT_DIR / "sources.yml"
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_DIR", str(PROJECT_DIR)))
ARTICLES_DIR = OUTPUT_ROOT / "Web記事" / "AI"

JST = timezone(timedelta(hours=9))

# Source name → folder name (must match migrate_to_source_folders.py)
SOURCE_TO_FOLDER = {
    "OpenAI Blog": "OpenAI",
    "Anthropic Blog": "Anthropic",
    "Anthropic (X/Twitter)": "Anthropic",
    "Google DeepMind Blog": "DeepMind",
    "Google Gemini (X/Twitter)": "DeepMind",
    "arXiv (cs.AI)": "arXiv",
    "arXiv (cs.LG)": "arXiv",
    "MIT Technology Review": "MIT-TechReview",
}


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

def load_sources() -> list[dict]:
    """Load enabled sources with RSS URLs from sources.yml."""
    if not SOURCES_FILE.exists():
        print("ERROR: sources.yml not found.", file=sys.stderr)
        sys.exit(1)
    data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8")) or {}
    all_sources = data.get("sources", [])
    return [
        s for s in all_sources
        if s.get("enabled", True) and s.get("rss")
    ]


# ---------------------------------------------------------------------------
# RSS fetching
# ---------------------------------------------------------------------------

def _parse_entry_date(entry) -> str | None:
    """Extract YYYY-MM-DD from a feedparser entry."""
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc).astimezone(JST).strftime("%Y-%m-%d")
            except Exception:
                pass
    # Fallback: try parsing raw string
    for attr in ("published", "updated", "created"):
        raw = entry.get(attr) if hasattr(entry, "get") else None
        if raw:
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(JST).strftime("%Y-%m-%d")
            except Exception:
                pass
    return None


def fetch_rss(source: dict) -> list[dict]:
    """Fetch RSS feed and return list of article dicts."""
    rss_url = source["rss"]
    name = source["name"]
    print(f"  📡 {name} — fetching {rss_url}")
    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        print(f"     ERROR: {e}", file=sys.stderr)
        return []

    if feed.bozo and not feed.entries:
        print(f"     WARNING: parse error: {feed.bozo_exception}", file=sys.stderr)
        return []

    entries = feed.entries[:MAX_ARTICLES_PER_SOURCE]
    articles = []
    for e in entries:
        url = e.get("link", "").strip()
        title = e.get("title", "").strip()
        if not url or not title:
            continue
        published = _parse_entry_date(e)
        if not published:
            # If no date, assume today — better than dropping
            published = datetime.now(JST).strftime("%Y-%m-%d")
        articles.append({
            "title_en": title,
            "url": url,
            "source": name,
            "published": published,
        })
    print(f"     → {len(articles)} entries")
    return articles


# ---------------------------------------------------------------------------
# Dedup against existing files
# ---------------------------------------------------------------------------

def load_existing_urls() -> set[str]:
    """Scan all existing .md files (recursively in source folders) and collect article URLs."""
    urls = set()
    if not ARTICLES_DIR.exists():
        return urls
    url_pattern = re.compile(r"\((https?://[^)\s]+)\)")
    for md in ARTICLES_DIR.rglob("*.md"):
        for m in url_pattern.finditer(md.read_text(encoding="utf-8")):
            urls.add(m.group(1))
    return urls


# ---------------------------------------------------------------------------
# Gemini summarization
# ---------------------------------------------------------------------------

def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    return genai.Client(api_key=api_key)


ANALYSIS_PROMPT = """\
You are a professional AI journalist writing for a Japanese audience.
Fetch the article at the URL below and write a detailed summary.

Title: {title}
URL: {url}
Source: {source}
Published: {published}

Return a JSON object with:
- "title_ja": article title in natural, concise Japanese (from the English title above)
- "summary": A 4-6 sentence detailed summary in Japanese (200-400 chars). Include WHAT was announced,
  HOW it works (technical specifics, numbers, benchmarks), and WHY it matters.
  Start with the publication date, e.g. "2026年4月16日、Anthropicは〜を発表した。"
  Avoid vague phrases — include concrete facts, names, numbers.
- "bullet_points": array of exactly 3 specific, factual Japanese takeaways (60-100 chars each).
- "tags": array of 3-5 relevant tags (Japanese or English, short).
- "importance": integer 1-5 (5 = groundbreaking, 1 = minor update).

Return ONLY valid JSON. No markdown fences, no explanation.
"""


def _call_gemini(client: genai.Client, prompt: str, use_search: bool = True) -> str:
    tools = [types.Tool(google_search=types.GoogleSearch())] if use_search else []
    config = types.GenerateContentConfig(tools=tools, temperature=0.1)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=config,
            )
            return response.text.strip()
        except Exception as e:
            err = str(e)
            if ("429" in err or "503" in err) and attempt < MAX_RETRIES:
                wait = RETRY_DELAY * attempt
                print(f"     ⏳ Rate limit, retry in {wait}s ({attempt}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                raise


def analyze_article(client: genai.Client, article: dict) -> dict:
    """Generate Japanese summary for a single article via Gemini."""
    prompt = ANALYSIS_PROMPT.format(
        title=article.get("title_en", ""),
        url=article.get("url", ""),
        source=article.get("source", ""),
        published=article.get("published", "不明"),
    )
    try:
        text = _call_gemini(client, prompt, use_search=True)
    except Exception as e:
        print(f"     ERROR: {e}", file=sys.stderr)
        return _fallback_analysis(article)

    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]

    try:
        analysis = json.loads(text)
    except json.JSONDecodeError:
        print(f"     WARNING: JSON parse failed", file=sys.stderr)
        return _fallback_analysis(article)

    return {**article, **analysis}


def _fallback_analysis(article: dict) -> dict:
    return {
        **article,
        "title_ja": article.get("title_en", ""),
        "summary": "要約の取得に失敗しました。",
        "bullet_points": ["N/A", "N/A", "N/A"],
        "tags": ["ai"],
        "importance": 1,
    }


# ---------------------------------------------------------------------------
# Markdown writing (append to date-based files)
# ---------------------------------------------------------------------------

def _stars(n: int) -> str:
    n = max(1, min(5, int(n)))
    return "★" * n + "☆" * (5 - n)


def format_article_block(index: int, article: dict) -> str:
    title = article.get("title_ja") or article.get("title_en") or "無題"
    url = article.get("url", "")
    source = article.get("source", "")
    published = article.get("published", "")
    importance = article.get("importance", 3)
    summary = article.get("summary", "")
    bullets = article.get("bullet_points") or []
    tags = article.get("tags") or []

    tag_line = " ".join(f"`{t}`" for t in tags)

    lines = [
        f"## {index}. {title}",
        "",
        f"| **URL** | [{url}]({url}) |",
        f"| **Source** | {source} |",
        f"| **Published** | {published} |",
        f"| **Importance** | {_stars(importance)} ({importance}/5) |",
        "",
        f"> {summary}",
        "",
        "**重要ポイント:**",
    ]
    for b in bullets:
        lines.append(f"- {b}")
    lines.append("")
    if tag_line:
        lines.append(tag_line)
        lines.append("")
    lines.append("---")
    return "\n".join(lines)


def append_to_source_date_file(folder: str, date: str, articles: list[dict]) -> int:
    """Append articles to Web記事/AI/{folder}/{date}.md, renumbering sequentially."""
    folder_path = ARTICLES_DIR / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    md_path = folder_path / f"{date}.md"

    if md_path.exists():
        existing = md_path.read_text(encoding="utf-8")
        existing_count = len(re.findall(r"^## \d+\.", existing, flags=re.MULTILINE))
        body = existing.rstrip() + "\n\n"
    else:
        existing_count = 0
        body = f"---\ndate: {date}\nsource: {folder}\n---\n\n"

    for i, art in enumerate(articles, start=existing_count + 1):
        body += format_article_block(i, art) + "\n\n"

    md_path.write_text(body, encoding="utf-8")
    return len(articles)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    now = datetime.now(JST)
    print(f"=== AI Daily Digest — {now.strftime('%Y-%m-%d %H:%M JST')} ===\n")

    sources = load_sources()
    if not sources:
        print("ERROR: No enabled sources with RSS found", file=sys.stderr)
        sys.exit(1)
    print(f"Loaded {len(sources)} RSS-enabled sources\n")

    # Phase 1: Fetch all RSS feeds
    print("📡 Phase 1: Fetching RSS feeds...")
    all_articles: list[dict] = []
    for s in sources:
        all_articles.extend(fetch_rss(s))
    print(f"\nTotal RSS entries: {len(all_articles)}")

    # Phase 2: Dedup against existing articles
    print("\n🔎 Phase 2: Deduplication...")
    existing_urls = load_existing_urls()
    print(f"  {len(existing_urls)} URLs already saved")
    new_articles = [a for a in all_articles if a["url"] not in existing_urls]
    print(f"  {len(new_articles)} new articles to process")

    if not new_articles:
        print("\n✨ Nothing new to summarize. Exiting cleanly.")
        return

    # Phase 3: Summarize each new article with Gemini
    print(f"\n🧠 Phase 3: Summarizing {len(new_articles)} articles via Gemini...")
    client = get_client()
    analyzed: list[dict] = []
    for i, art in enumerate(new_articles, 1):
        title = art.get("title_en", "?")
        print(f"  [{i}/{len(new_articles)}] {art.get('source','?')} — {title[:60]}")
        analyzed.append(analyze_article(client, art))

    # Phase 4: Group by (source-folder, published date) and write
    print(f"\n💾 Phase 4: Writing to {ARTICLES_DIR} (by source folder)")
    by_folder_date: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for a in analyzed:
        folder = SOURCE_TO_FOLDER.get(a.get("source", ""), "Other")
        by_folder_date[(folder, a["published"])].append(a)

    total_added = 0
    for (folder, date) in sorted(by_folder_date.keys()):
        n = append_to_source_date_file(folder, date, by_folder_date[(folder, date)])
        total_added += n
        print(f"  {folder}/{date}: +{n} articles")

    print(f"\n✅ Done. Added {total_added} new articles across {len(by_folder_date)} source-date buckets.")


if __name__ == "__main__":
    main()
