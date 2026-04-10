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

from google import genai
from google.genai import types
from jinja2 import Environment, FileSystemLoader

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SOURCES = [
    {"name": "OpenAI Blog", "site": "openai.com/blog"},
    {"name": "Anthropic Blog", "site": "anthropic.com/news"},
    {"name": "Google DeepMind Blog", "site": "deepmind.google/discover/blog"},
    {"name": "arXiv (cs.AI / cs.LG)", "site": "arxiv.org"},
    {"name": "MIT Technology Review", "site": "technologyreview.com/topic/artificial-intelligence"},
]

ARTICLES_PER_SOURCE = 2
JST = timezone(timedelta(hours=9))

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

SEARCH_PROMPT_TEMPLATE = """\
You are an AI news researcher. Find the {count} most recent articles from {source} ({site}).

For EACH article, return a JSON object with these fields:
- "title": article title
- "url": full URL to the article
- "source": "{source}"
- "published": publication date in YYYY-MM-DD format (best guess if not exact)

Return ONLY a JSON array of objects. No markdown fences, no explanation.
"""

ANALYSIS_PROMPT_TEMPLATE = """\
Analyze this AI article and return a JSON object:

Title: {title}
URL: {url}
Source: {source}

Return JSON with:
- "summary": one-sentence summary in Japanese (concise, under 80 chars)
- "bullet_points": array of exactly 3 key points in Japanese (each under 60 chars)
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


def fetch_articles_for_source(
    client: genai.Client, source_name: str, site: str, count: int
) -> list[dict]:
    """Use Gemini + Google Search grounding to find recent articles."""
    prompt = SEARCH_PROMPT_TEMPLATE.format(count=count, source=source_name, site=site)
    google_search_tool = types.Tool(google_search=types.GoogleSearch())

    try:
        text = _call_gemini(client, "gemini-2.0-flash", prompt, tools=[google_search_tool])
    except Exception as e:
        print(f"  ERROR: Failed to fetch from {source_name}: {e}", file=sys.stderr)
        return []

    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    try:
        articles = json.loads(text)
    except json.JSONDecodeError:
        print(f"  WARNING: Could not parse JSON for {source_name}: {text[:200]}", file=sys.stderr)
        return []

    if not isinstance(articles, list):
        articles = [articles]

    return articles[:count]


def analyze_article(client: genai.Client, article: dict) -> dict:
    """Use Gemini to generate summary, bullet points, tags, importance."""
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        title=article.get("title", ""),
        url=article.get("url", ""),
        source=article.get("source", ""),
    )

    try:
        text = _call_gemini(client, "gemini-2.0-flash", prompt)
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
    client = get_client()

    all_articles: list[dict] = []

    # Phase 1: Fetch articles from each source
    for src in SOURCES:
        print(f"\n📡 Fetching from {src['name']}...")
        articles = fetch_articles_for_source(
            client, src["name"], src["site"], ARTICLES_PER_SOURCE
        )
        print(f"   Found {len(articles)} articles")
        all_articles.extend(articles)

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
