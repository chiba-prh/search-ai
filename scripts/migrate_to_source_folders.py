#!/usr/bin/env python3
"""Migrate date-based files (Web記事/AI/YYYY-MM-DD.md) to source-based folders
(Web記事/AI/{source}/YYYY-MM-DD.md). One-time migration script."""

import re
import sys
from collections import defaultdict
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_DIR = Path(__file__).resolve().parent.parent
AI_DIR = PROJECT_DIR / "Web記事" / "AI"

# Source name → folder name
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


def extract_articles(text: str) -> list[tuple[str, str]]:
    """Return list of (source, full_block_text) for each article in the file."""
    out = []
    sections = re.split(r"(?=^## \d+\.)", text, flags=re.MULTILINE)
    for section in sections[1:]:
        m = re.search(r"\*\*Source\*\*\s*\|\s*(.+?)\s*\|", section)
        if not m:
            continue
        source = m.group(1).strip()
        out.append((source, section))
    return out


def main():
    if not AI_DIR.exists():
        print(f"ERROR: {AI_DIR} not found")
        sys.exit(1)

    # Collect all date-based files (top level only)
    date_files = sorted(AI_DIR.glob("*.md"))
    if not date_files:
        print("No date-based .md files found in top level")
        return

    # source -> date -> list of article blocks
    by_source_date: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for md in date_files:
        date = md.stem
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            continue
        text = md.read_text(encoding="utf-8")
        for source, block in extract_articles(text):
            folder = SOURCE_TO_FOLDER.get(source)
            if not folder:
                print(f"  WARN: unknown source '{source}' (skipped)")
                continue
            by_source_date[folder][date].append(block.strip())

    # Write to source folders
    total = 0
    for folder, dates in sorted(by_source_date.items()):
        folder_path = AI_DIR / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        for date, blocks in sorted(dates.items()):
            out_path = folder_path / f"{date}.md"
            lines = [f"---", f"date: {date}", f"source: {folder}", f"---", ""]
            for i, block in enumerate(blocks, 1):
                # Renumber: replace "## N." with sequential number within this file
                renumbered = re.sub(r"^## \d+\.", f"## {i}.", block, count=1)
                lines.append(renumbered.rstrip())
                lines.append("")
            out_path.write_text("\n".join(lines), encoding="utf-8")
            total += len(blocks)
            print(f"  ✅ {folder}/{date}.md ({len(blocks)} articles)")

    # Delete original date-based files
    print("\n🗑️  Removing old date-based files...")
    for md in date_files:
        md.unlink()
        print(f"  removed: {md.name}")

    print(f"\n✨ Migration complete: {total} articles across {len(by_source_date)} sources")


if __name__ == "__main__":
    main()
