#!/usr/bin/env python3
"""
publish_medium.py — Pushes a Markdown blog post as a draft to Medium via API.
Usage: python series/scripts/publish_medium.py <path-to-blog.md>
"""
import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

import requests


def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    # Simple YAML key-value parser to avoid external dependencies
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


def markdown_to_medium_html(body: str) -> str:
    """
    Converts Markdown into Medium-friendly HTML (`contentFormat: "html"`) with exact Medium
    `graf` CSS classes, preserving fenced code blocks and converting tables cleanly without dependencies.
    """
    code_blocks = []
    def replace_code_block(match):
        lang = match.group(1) or ""
        code = match.group(2)
        escaped_code = html.escape(code)
        block_html = f'<pre class="graf graf--pre"><code class="markup--code markup--pre-code">{escaped_code}</code></pre>'
        code_blocks.append(block_html)
        return f"<!--CODE_BLOCK_{len(code_blocks)-1}-->"

    body = re.sub(r'```([a-zA-Z0-9_-]*)\n(.*?)\n```', replace_code_block, body, flags=re.DOTALL)

    # Convert Markdown tables into structured key-value lists so Medium preserves columns
    def process_tables(text: str) -> str:
        lines = text.splitlines()
        output_lines = []
        in_table = False
        headers = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("|") and stripped.endswith("|"):
                cells = [c.strip() for c in stripped[1:-1].split("|")]
                if not in_table:
                    in_table = True
                    headers = cells
                    output_lines.append('<ul class="graf graf--ul">')
                else:
                    if all(re.match(r'^[-:]+$', c) for c in cells):
                        continue
                    row_parts = []
                    for idx, cell in enumerate(cells):
                        h = headers[idx] if idx < len(headers) else f"Col {idx+1}"
                        if h and cell:
                            row_parts.append(f'<strong class="markup--strong markup--li-strong">{h}:</strong> {cell}')
                        elif cell:
                            row_parts.append(cell)
                    if row_parts:
                        output_lines.append(f'  <li class="graf graf--li">{" — ".join(row_parts)}</li>')
            else:
                if in_table:
                    in_table = False
                    output_lines.append('</ul>')
                output_lines.append(line)
        if in_table:
            output_lines.append('</ul>')
        return "\n".join(output_lines)

    body = process_tables(body)

    lines = body.splitlines()
    html_lines = []
    in_ul = False
    in_ol = False

    for line in lines:
        stripped = line.strip()
        if in_ul and not (stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith('<li class="graf graf--li">') or stripped == '</ul>'):
            html_lines.append('</ul>')
            in_ul = False
        if in_ol and not re.match(r'^\d+\.\s+', stripped):
            html_lines.append('</ol>')
            in_ol = False

        if not stripped:
            continue
        elif stripped.startswith("<!--CODE_BLOCK_"):
            html_lines.append(stripped)
        elif stripped.startswith('<ul class="graf graf--ul">') or stripped.startswith('  <li class="graf graf--li">') or stripped == '</ul>':
            html_lines.append(stripped)
        elif stripped.startswith("# ") or stripped.startswith("## ") or stripped.startswith("### ") or stripped.startswith("#### "):
            level = len(stripped.split()[0])
            text = stripped.lstrip("#").strip()
            graf_level = min(level, 3)
            html_lines.append(f'<h{graf_level} class="graf graf--h{graf_level}">{text}</h{graf_level}>')
        elif stripped.startswith("> "):
            text = stripped[2:].strip()
            html_lines.append(f'<blockquote class="graf graf--blockquote">{text}</blockquote>')
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_ul:
                html_lines.append('<ul class="graf graf--ul">')
                in_ul = True
            text = stripped[2:].strip()
            html_lines.append(f'  <li class="graf graf--li">{text}</li>')
        elif re.match(r'^\d+\.\s+', stripped):
            if not in_ol:
                html_lines.append('<ol class="graf graf--ol">')
                in_ol = True
            text = re.sub(r'^\d+\.\s+', '', stripped).strip()
            html_lines.append(f'  <li class="graf graf--li">{text}</li>')
        elif stripped == "---":
            html_lines.append('<hr class="graf graf--hr" />')
        else:
            html_lines.append(f'<p class="graf graf--p">{stripped}</p>')

    if in_ul:
        html_lines.append('</ul>')
    if in_ol:
        html_lines.append('</ol>')

    html_body = "\n".join(html_lines)

    # Inline formatting (bold, italic, inline code, links)
    html_body = re.sub(r'\*\*(.*?)\*\*', r'<strong class="markup--strong markup--p-strong">\1</strong>', html_body)
    html_body = re.sub(r'__(.*?)__', r'<strong class="markup--strong markup--p-strong">\1</strong>', html_body)
    html_body = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em class="markup--em markup--p-em">\1</em>', html_body)
    html_body = re.sub(r'`(.*?)`', r'<code class="markup--code markup--p-code">\1</code>', html_body)
    html_body = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" class="markup--anchor markup--p-anchor">\1</a>', html_body)

    for idx, block in enumerate(code_blocks):
        html_body = html_body.replace(f"<!--CODE_BLOCK_{idx}-->", block)

    return html_body


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish markdown draft to Medium.")
    parser.add_argument("file", help="Path to blog.md file")
    args = parser.parse_args()

    token = os.environ.get("MEDIUM_TOKEN")
    user_id = os.environ.get("MEDIUM_USER_ID")
    if not token or not user_id:
        print("Error: MEDIUM_TOKEN and MEDIUM_USER_ID environment variables must be set.", file=sys.stderr)
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

    html_content = markdown_to_medium_html(body)

    payload = {
        "title": title,
        "contentFormat": "html",
        "content": html_content,
        "publishStatus": "draft",
        "tags": tags[:5],  # Medium allows up to 5 tags
    }
    if canonical_url and canonical_url.startswith("http"):
        payload["canonicalUrl"] = canonical_url

    print(f"Pushing draft '{title}' to Medium...")
    resp = requests.post(
        f"https://api.medium.com/v1/users/{user_id}/posts",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
    )

    if resp.status_code in (200, 201):
        data = resp.json().get("data", {})
        print(f"Success! Draft created: {data.get('url')}")
    else:
        print(f"Failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
