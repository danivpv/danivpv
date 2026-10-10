#!/usr/bin/env python3
"""
post_x_article.py — Pushes a Markdown blog post as an X Article (or Draft) via X API v2.
Since official Python SDKs (like Tweepy) may not wrap the new June 2026 `/2/articles` 
endpoints immediately, this script uses raw HTTP requests with OAuth 2.0 / OAuth 1.0a.

Endpoint Reference (June 2026):
  POST https://api.x.com/2/articles (or https://api.x.com/2/articles/drafts)

Usage: python series/scripts/post_x_article.py <path-to-blog.md> [--draft]
"""
import argparse
import json
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
    parser = argparse.ArgumentParser(description="Publish markdown post as an X Article (API v2).")
    parser.add_argument("file", help="Path to blog.md file")
    parser.add_argument("--live", action="store_true", help="Publish live directly instead of creating a draft.")
    args = parser.parse_args()

    # X API v2 Articles typically require OAuth 2.0 User Access Token (with `article.write` scope)
    # or OAuth 1.0a User Context.
    bearer_token = os.environ.get("X_BEARER_TOKEN") or os.environ.get("X_ACCESS_TOKEN")
    if not bearer_token:
        print("Error: X_BEARER_TOKEN or X_ACCESS_TOKEN environment variable must be set.", file=sys.stderr)
        sys.exit(1)

    path = Path(args.file)
    if not path.exists():
        print(f"Error: File {path} not found.", file=sys.stderr)
        sys.exit(1)

    raw_content = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw_content)

    title = meta.get("title", path.stem)

    # Determine endpoint: draft vs live
    endpoint = "https://api.x.com/2/articles" if args.live else "https://api.x.com/2/articles/drafts"

    payload = {
        "title": title,
        "content": body,  # X Articles support Markdown syntax
    }

    print(f"Pushing '{title}' to X Articles ({'LIVE' if args.live else 'DRAFT'})...")
    
    # We send raw REST request bypassing SDK lag
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }
    
    resp = requests.post(endpoint, headers=headers, json=payload)

    if resp.status_code in (200, 201):
        data = resp.json().get("data", {})
        article_id = data.get("id", "unknown")
        url = data.get("url", f"https://x.com/compose/articles/{article_id}")
        print(f"Success! X Article created: {url}")
    else:
        print(f"Failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        print("\nNote: If 401/403, verify your app permissions in developer.x.com include 'article.write' scope.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
