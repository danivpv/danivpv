#!/usr/bin/env python3
"""
publish_devto.py — Pushes a Markdown blog post as a draft to dev.to via API.
Usage: python series/scripts/publish_devto.py <path-to-blog.md>
"""
import argparse
import os
import sys
from pathlib import Path

import requests


def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    meta = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip('"\'')
        if val.startswith("[") and val.endswith("]"):
            val = [item.strip().strip('"\'') for item in val[1:-1].split(",") if item.strip()]
        meta[key] = val
    return meta, parts[2].strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish markdown draft to dev.to.")
    parser.add_argument("file", help="Path to blog.md file")
    args = parser.parse_args()

    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("Error: DEVTO_API_KEY environment variable must be set.", file=sys.stderr)
        sys.exit(1)

    path = Path(args.file)
    if not path.exists():
        print(f"Error: File {path} not found.", file=sys.stderr)
        sys.exit(1)

    raw_content = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw_content)

    title = meta.get("title", path.stem)
    tags = meta.get("tags", ["engineering"]) if isinstance(meta.get("tags"), list) else [meta.get("tags", "engineering")]
    canonical_url = meta.get("canonical_url", "")

    article_data = {
        "title": title,
        "body_markdown": body,
        "published": False,  # Always draft first
        "tags": tags[:4],    # dev.to allows up to 4 tags
    }
    if canonical_url and canonical_url.startswith("http"):
        article_data["canonical_url"] = canonical_url

    print(f"Pushing draft '{title}' to dev.to...")
    resp = requests.post(
        "https://dev.to/api/articles",
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
        },
        json={"article": article_data},
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"Success! Draft created: {data.get('url')}")
    else:
        print(f"Failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
