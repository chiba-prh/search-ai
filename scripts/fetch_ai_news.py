#!/usr/bin/env python3
"""AI Daily Digest — Fetch AI news using Gemini API with Google Search grounding."""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

import yaml

from google import genai
from google.genai import types
from jinja2 import Environment, FileSystemLoader

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCES_FILE = PROJECT_DIR / "sources.yml"
JST = timezone(timedelta(hours=9))


def load_sources() -> list[dict]:
    """Load enabled sources from sources.yml."""
    if not SOURCES_FILE.exists():
        print("WARNING: sources.yml not found, using defaults.", file=sys.stderr)
        return [
            {"name": "OpenAI Blog", "url": "openai.com/blog", "count": 2},
            {"name": "Anthropic Blog", "url": "anthropic.com/news", "count": 2},
        ]
    data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8")) or {}
    all_sources = data.get("sources", [])
    # Only return enabled sources
    return [s for s in all_sources if s.get("enabled", True)]

# ---------------------------------------------------------------------------
# Gemini client
# ---------------------------------------------------------------------------


def get_client() -> genai.Client:
    """Create Gemini client from env."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    return genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# Fetch helpers
# ---------------------------------------------------------------------------

def build_search_prompt(sources: list[dict]) -> str:
    """Build search prompt dynamically from sources.yml."""
    source_lines = []
    total = 0
    has_all = False
    for i, s in enumerate(sources, 1):
        count_raw = s.get("count", 2)
        # Handle "all" or numeric counts
        if isinstance(count_raw, str) and count_raw.lower() == "all":
            count_label = "all available (10-20+)"
            total += 15  # estimate for prompt sizing
            has_all = True
        else:
            try:
                count_int = int(count_raw)
            except (TypeError, ValueError):
                count_int = 2
            count_label = f"{count_int} articles"
            total += count_int
        source_lines.append(f"{i}. {s['name']} ({s['url']}) — {count_label}")

    target_phrase = f"approximately {total}" if has_all else f"total {total}"
    return f"""\
You are an AI news researcher. Find the most recent articles from EACH of these sources
(fetch ALL articles visible on the top page for sources marked "all available"):

{chr(10).join(source_lines)}

For EACH article ({target_phrase}), return a JSON object with:
- "title": article title translated into Japanese (natural, concise Japanese)
- "title_en": original article title in English
- "url": full URL to the article
- "source": source name (e.g. "{sources[0]['name']}" etc.)
- "published": publication date in YYYY-MM-DD format

Return ONLY a JSON array of {total} objects. No markdown fences, no explanation.
"""

ANALYSIS_PROMPT_TEMPLATE = """\
You are a professional AI journalist writing for a Japanese audience.
Search the web for the full content of this article, then write a detailed summary.

Title: {title}
URL: {url}
Source: {source}
Published: {published}

Return a JSON object with:
- "summary": A detailed 4-6 sentence summary in Japanese (200-400 chars). MUST include:
  1. The publication date (e.g. "2026年4月10日、Anthropicは〜を発表した。")
  2. WHAT specifically was announced or discovered (concrete details, not vague descriptions)
  3. HOW it works or what it does (technical specifics, numbers, benchmarks if available)
  4. WHY it matters and its real-world impact
  Do NOT write generic summaries. Include specific facts, names, numbers, and details from the article.
- "bullet_points": array of exactly 3 key takeaways in Japanese. Each must be specific and factual (60-100 chars). Avoid vague phrases like "AIの安全性向上" — instead write concrete facts like "Claude 4.6はコーディング精度が前世代比15%向上"
- "tags": array of 3-5 relevant tags (English, lowercase, e.g. "llm", "safety", "multimodal")
- "importance": integer 1-5 (5 = groundbreaking, 1 = minor update)

Return ONLY valid JSON. No markdown fences.
"""


def _call_gemini(client: genai.Client, model: str, prompt: str, tools=None) -> str:
    """Call Gemini with retry logic for rate limits."""
    config = types.GenerateContentConfig(
        tools=tools or [],
        temperature=0.1,
    )
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model, contents=prompt, config=config,
            )
            return response.text.strip()
        except Exception as e:
            err_str = str(e)
            if ("429" in err_str or "503" in err_str) and attempt < MAX_RETRIES:
                wait = RETRY_DELAY * attempt
                print(f"  ⏳ Rate limit hit, retrying in {wait}s... (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                raise


def fetch_all_articles(client: genai.Client, sources: list[dict]) -> list[dict]:
    """Fetch all articles from all sources in a single grounded request."""
    prompt = build_search_prompt(sources)
    google_search_tool = types.Tool(google_search=types.GoogleSearch())

    try:
        text = _call_gemini(client, "gemini-3-flash-preview", prompt, tools=[google_search_tool])
    except Exception as e:
        print(f"  ERROR: Failed to fetch articles: {e}", file=sys.stderr)
        return []

    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    try:
        articles = json.loads(text)
    except json.JSONDecodeError:
        print(f"  WARNING: Could not parse JSON: {text[:200]}", file=sys.stderr)
        return []

    if not isinstance(articles, list):
        articles = [articles]

    return articles


def analyze_article(client: genai.Client, article: dict) -> dict:
    """Use Gemini + Google Search grounding to generate detailed summary."""
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        title=article.get("title", ""),
        url=article.get("url", ""),
        source=article.get("source", ""),
        published=article.get("published", "不明"),
    )

    try:
        text = _call_gemini(client, "gemini-3-flash-preview", prompt)
    except Exception as e:
        print(f"  ERROR: Analysis failed for {article.get('title', '?')}: {e}", file=sys.stderr)
        return {
            **article,
            "summary": "要約の取得に失敗しました",
            "bullet_points": ["N/A", "N/A", "N/A"],
            "tags": ["ai"],
            "importance": 1,
        }

    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    try:
        analysis = json.loads(text)
    except json.JSONDecodeError:
        print(f"  WARNING: Could not parse analysis for {article.get('title', '?')}", file=sys.stderr)
        analysis = {
            "summary": "要約の取得に失敗しました",
            "bullet_points": ["N/A", "N/A", "N/A"],
            "tags": ["ai"],
            "importance": 1,
        }

    return {**article, **analysis}


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------


def render_markdown(articles: list[dict], date_str: str) -> str:
    """Render articles into Obsidian markdown via Jinja2 template."""
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("daily_digest.md.j2")

    sources = list({a.get("source", "Unknown") for a in articles})

    return template.render(
        date=date_str,
        articles=articles,
        sources=sources,
        generated_at=datetime.now(JST).strftime("%Y-%m-%d %H:%M JST"),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    today = datetime.now(JST)
    date_str = today.strftime("%Y-%m-%d")

    output_dir = Path(os.environ.get("OUTPUT_DIR", "output")) / "Web記事" / "AI"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{date_str}.md"

    print(f"=== AI Daily Digest — {date_str} ===")

    sources = load_sources()
    if not sources:
        print("ERROR: No enabled sources found in sources.yml", file=sys.stderr)
        sys.exit(1)
    print(f"   Loaded {len(sources)} sources from sources.yml")

    client = get_client()

    # Phase 1: Fetch all articles in one grounded request
    print("\n📡 Fetching articles from all sources (single batch)...")
    all_articles = fetch_all_articles(client, sources)
    print(f"   Found {len(all_articles)} articles")

    # Phase 2: Analyze each article
    print(f"\n🔍 Analyzing {len(all_articles)} articles...")
    analyzed: list[dict] = []
    for i, article in enumerate(all_articles, 1):
        print(f"   [{i}/{len(all_articles)}] {article.get('title', '?')[:60]}")
        analyzed.append(analyze_article(client, article))

    # Sort by importance (descending)
    analyzed.sort(key=lambda a: a.get("importance", 0), reverse=True)

    # Phase 3: Render markdown
    md_content = render_markdown(analyzed, date_str)
    output_file.write_text(md_content, encoding="utf-8")
    print(f"\n✅ Saved to {output_file}")
    print(f"   Total articles: {len(analyzed)}")


if __name__ == "__main__":
    main()
