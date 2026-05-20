#!/usr/bin/env python3
import sys
import re
from datetime import datetime
from pathlib import Path

def slugify(text):
    # Convert to lowercase, replace non-alphanumeric with hyphens, strip trailing/leading hyphens
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def main():
    if len(sys.argv) > 1:
        title = " ".join(sys.argv[1:])
    else:
        try:
            title = input("Enter post title: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)

    if not title:
        print("Error: Post title cannot be empty.")
        sys.exit(1)

    slug = slugify(title)
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{slug}.md"
    blog_dir = Path(__file__).parent.parent / "content" / "blog"
    post_path = blog_dir / filename

    if post_path.exists():
        print(f"Error: A post already exists at {post_path}")
        sys.exit(1)

    frontmatter = f"""---
title: "{title}"
date: {today}
summary: "A brief summary of your post."
tags: []
draft: true
---

Start writing your post here...
"""

    post_path.write_text(frontmatter, encoding="utf-8")
    print(f"Success! Created new blog post:")
    print(f"  Title: {title}")
    print(f"  Path:  {post_path.relative_to(Path.cwd())}")

if __name__ == "__main__":
    main()
