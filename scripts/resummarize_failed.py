#!/usr/bin/env python3
"""Re-summarize articles that previously failed (marked '要約の取得に失敗しました')."""

import json
import os
import re
import sys
import time
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from google import genai
from google.genai import types

PROJECT_DIR = Path(__file__).resolve().parent.parent
ARTICLES_DIR = PROJECT_DIR / "Web記事" / "AI"

MAX_RETRIES = 3
RETRY_DELAY = 10
INTER_CALL_DELAY = 3  # seconds between successful calls
SKIP_ARXIV = os.environ.get("SKIP_ARXIV", "false").lower() == "true"


ANALYSIS_PROMPT = """\
You are a professional AI journalist writing for a Japanese audience.
Fetch the article at the URL below and write a detailed summary.

Title: {title_en}
URL: {url}
Source: {source}
Published: {published}

Return a JSON object with:
- "title_ja": article title in natural, concise Japanese
- "summary": A 4-6 sentence detailed summary in Japanese (200-400 chars). Include WHAT, HOW, WHY with specific facts/numbers.
- "bullet_points": array of exactly 3 specific Japanese takeaways (60-100 chars each).
- "tags": array of 3-5 relevant short tags.
- "importance": integer 1-5 (5 = groundbreaking, 1 = minor).

Return ONLY valid JSON. No markdown fences, no explanation.
"""


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return genai.Client(api_key=api_key)


def call_gemini(client, prompt):
    tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(tools=[tool], temperature=0.1)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=config,
            )
            return resp.text.strip()
        except Exception as e:
            err = str(e)
            if ("429" in err or "503" in err or "quota" in err.lower()) and attempt < MAX_RETRIES:
                wait = RETRY_DELAY * attempt
                print(f"     ⏳ Retry {attempt}/{MAX_RETRIES} in {wait}s")
                time.sleep(wait)
            else:
                raise


def parse_json(text):
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def stars(n):
    n = max(1, min(5, int(n)))
    return "★" * n + "☆" * (5 - n)


def rebuild_block(index, article):
    title = article.get("title_ja") or article.get("title_en") or "無題"
    url = article["url"]
    source = article["source"]
    published = article["published"]
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
        f"| **Importance** | {stars(importance)} ({importance}/5) |",
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


def extract_article_info(block):
    """Parse an existing article block to extract metadata."""
    title_m = re.match(r"^## \d+\.\s*(.+)", block)
    url_m = re.search(r"\*\*URL\*\*\s*\|\s*\[.*?\]\((https?://[^)]+)\)", block)
    source_m = re.search(r"\*\*Source\*\*\s*\|\s*(.+?)\s*\|", block)
    pub_m = re.search(r"\*\*Published\*\*\s*\|\s*(\d{4}-\d{2}-\d{2})", block)
    if not (url_m and source_m and pub_m):
        return None
    return {
        "title_en": title_m.group(1).strip() if title_m else "",
        "url": url_m.group(1),
        "source": source_m.group(1).strip(),
        "published": pub_m.group(1),
    }


def main():
    client = get_client()
    files = sorted(ARTICLES_DIR.rglob("*.md"), reverse=True)
    total_failed = 0
    total_fixed = 0

    for md_path in files:
        text = md_path.read_text(encoding="utf-8")
        if "要約の取得に失敗しました" not in text:
            continue

        # Split by article sections
        sections = re.split(r"(?=^## \d+\.)", text, flags=re.MULTILINE)
        header = sections[0]  # YAML front matter
        articles_out = []
        changed = False

        article_idx = 0
        for section in sections[1:]:
            article_idx += 1
            if "要約の取得に失敗しました" not in section:
                # Keep as-is but renumber later
                # Parse existing section to keep its content
                articles_out.append(("keep", section))
                continue

            info = extract_article_info(section)
            if not info:
                articles_out.append(("keep", section))
                continue

            # Optionally skip arXiv (research papers, lower priority)
            if SKIP_ARXIV and "arXiv" in info.get("source", ""):
                articles_out.append(("keep", section))
                continue

            total_failed += 1
            print(f"[{md_path.parent.name}/{md_path.stem}] Re-summarizing: {info['title_en'][:60]}")
            prompt = ANALYSIS_PROMPT.format(**info)
            try:
                text_resp = call_gemini(client, prompt)
                analysis = parse_json(text_resp)
                article = {**info, **analysis}
                articles_out.append(("rebuild", article))
                total_fixed += 1
                changed = True
                time.sleep(INTER_CALL_DELAY)
            except Exception as e:
                err_str = str(e)
                print(f"   ERROR: {err_str[:200]}")
                articles_out.append(("keep", section))
                # Stop entirely if quota is exhausted — no point continuing
                if "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    print("\n🛑 Gemini quota exhausted — stopping. Re-run after reset.")
                    if changed:
                        # save progress before exiting
                        new_text = header.rstrip() + "\n\n"
                        for j, (kind, item) in enumerate(articles_out, 1):
                            if kind == "rebuild":
                                new_text += rebuild_block(j, item) + "\n\n"
                            else:
                                renumbered = re.sub(r"^## \d+\.", f"## {j}.", item, count=1)
                                new_text += renumbered.rstrip() + "\n\n"
                        md_path.write_text(new_text, encoding="utf-8")
                        print(f"   💾 Saved partial progress to {md_path.name}")
                    print(f"\nDone (partial): {total_fixed}/{total_failed} re-summarized")
                    sys.exit(0)

        if not changed:
            continue

        # Rebuild file with renumbered articles
        new_text = header.rstrip() + "\n\n"
        for i, (kind, item) in enumerate(articles_out, 1):
            if kind == "rebuild":
                new_text += rebuild_block(i, item) + "\n\n"
            else:
                # Renumber existing block
                renumbered = re.sub(r"^## \d+\.", f"## {i}.", item, count=1)
                new_text += renumbered.rstrip() + "\n\n"

        md_path.write_text(new_text, encoding="utf-8")
        print(f"   ✅ Saved {md_path.name}")

    print(f"\nDone: {total_fixed}/{total_failed} re-summarized")


if __name__ == "__main__":
    main()
