from __future__ import annotations

import argparse
import email.utils
import html
import http.server
import math
import os
import re
import shutil
import socketserver
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pygments.formatters import HtmlFormatter


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"
CONTENT_ROOT = ROOT / "content"
BLOG_ROOT = CONTENT_ROOT / "blog"
PAGES_ROOT = CONTENT_ROOT / "pages"
CNAME_PATH = ROOT / "CNAME"
REDIRECT_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Redirecting...</title>
  <meta http-equiv="refresh" content="0; url={target}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="noindex">
  <script>location.replace({target_json});</script>
</head>
<body>
  <p>Redirecting to <a href="{target}">{target}</a>.</p>
</body>
</html>
"""


@dataclass
class ContentItem:
    title: str
    slug: str
    content_type: str
    source_path: Path
    output_rel_path: str
    url: str
    legacy_paths: list[str]
    summary: str
    tags: list[str]
    draft: bool
    html_body: str
    raw_body: str
    date_value: date | None = None
    date_display: str | None = None
    reading_time: int | None = None
    show_in_nav: bool = False
    nav_order: int = 9999

    @property
    def canonical_url(self) -> str:
        return self.url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the karanjakhar.net static site.")
    parser.add_argument("--serve", action="store_true", help="Serve the output directory on :8000 after building.")
    parser.add_argument("--drafts", action="store_true", help="Include draft content.")
    parser.add_argument("--clean", action="store_true", help="Delete the output directory before building.")
    return parser.parse_args()


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    required_sections = ("site", "hero", "about", "social", "build", "theme")
    for key in required_sections:
        if key not in config:
            raise ValueError(f"Missing required config section: {key}")

    site_required = ("title", "author", "description", "base_url", "language", "timezone")
    for key in site_required:
        if key not in config["site"]:
            raise ValueError(f"Missing required site config value: site.{key}")

    if "output_dir" not in config["build"]:
        raise ValueError("Missing required build config value: build.output_dir")

    return config


def parse_frontmatter(text: str, source_path: Path) -> tuple[dict[str, Any], str]:
    normalized = text.lstrip("\ufeff")
    if not normalized.startswith("---\n"):
        raise ValueError(f"{source_path} is missing YAML frontmatter.")

    parts = normalized.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError(f"{source_path} has malformed YAML frontmatter.")

    metadata = yaml.safe_load(parts[0][4:]) or {}
    body = parts[1].lstrip("\n")
    return metadata, body


def parse_date(value: Any, source_path: Path) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for candidate in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, candidate).date()
            except ValueError:
                continue
    raise ValueError(f"Unsupported date value in {source_path}: {value!r}")


def markdown_to_html(body: str) -> str:
    renderer = markdown.Markdown(
        extensions=["fenced_code", "codehilite", "tables", "smarty", "toc"],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
            "toc": {"permalink": False},
        },
        output_format="html5",
    )
    return renderer.convert(body)


def build_summary(body: str, fallback: str = "") -> str:
    paragraphs = [segment.strip() for segment in re.split(r"\n\s*\n", body) if segment.strip()]
    candidate = ""
    for paragraph in paragraphs:
        cleaned = re.sub(r"^#+\s*", "", paragraph)
        cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", cleaned)
        cleaned = re.sub(r"\[[^\]]+\]\([^)]+\)", lambda match: match.group(0).split("](")[0][1:], cleaned)
        cleaned = re.sub(r"[*_>`#-]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned:
            candidate = cleaned
            break
    if not candidate:
        candidate = fallback.strip()
    if len(candidate) <= 220:
        return candidate
    trimmed = candidate[:220].rsplit(" ", 1)[0].strip()
    return f"{trimmed}..."


def reading_time_for_body(body: str) -> int:
    words = re.findall(r"\b\w+\b", body)
    return max(1, math.ceil(len(words) / 200))


def coerce_tags(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(tag).strip() for tag in value if str(tag).strip()]
    if isinstance(value, str):
        return [tag.strip() for tag in value.split(",") if tag.strip()]
    raise ValueError(f"Unsupported tags value: {value!r}")


def load_content(directory: Path, content_type: str, include_drafts: bool) -> list[ContentItem]:
    items: list[ContentItem] = []
    for path in sorted(directory.glob("*.md")):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"), path)
        title = str(metadata.get("title", "")).strip()
        if not title:
            raise ValueError(f"Missing title in {path}")

        slug = str(metadata.get("slug") or path.stem).strip()
        if not slug:
            raise ValueError(f"Missing slug for {path}")

        draft = bool(metadata.get("draft", False))
        if draft and not include_drafts:
            continue

        html_body = markdown_to_html(body)
        summary = str(metadata.get("summary") or build_summary(body, fallback=title))
        tags = coerce_tags(metadata.get("tags"))

        if content_type == "post":
            item_date = parse_date(metadata.get("date"), path)
            url = f"/blog/{slug}/"
            output_rel_path = f"blog/{slug}/index.html"
            legacy_paths = [f"{path.stem}.html"]
            item = ContentItem(
                title=title,
                slug=slug,
                content_type=content_type,
                source_path=path,
                output_rel_path=output_rel_path,
                url=url,
                legacy_paths=legacy_paths,
                summary=summary,
                tags=tags,
                draft=draft,
                html_body=html_body,
                raw_body=body,
                date_value=item_date,
                date_display=item_date.strftime("%B %-d, %Y") if os.name != "nt" else item_date.strftime("%B %#d, %Y"),
                reading_time=reading_time_for_body(body),
            )
        else:
            url = f"/{slug}/"
            output_rel_path = f"{slug}/index.html"
            legacy_paths = [f"pages/{slug}.html"]
            item = ContentItem(
                title=title,
                slug=slug,
                content_type=content_type,
                source_path=path,
                output_rel_path=output_rel_path,
                url=url,
                legacy_paths=legacy_paths,
                summary=summary,
                tags=tags,
                draft=draft,
                html_body=html_body,
                raw_body=body,
                show_in_nav=bool(metadata.get("show_in_nav", False)),
                nav_order=int(metadata.get("nav_order", 9999)),
            )

        items.append(item)

    if content_type == "post":
        items.sort(key=lambda item: item.date_value or date.min, reverse=True)

    return items


def build_navigation(pages: list[ContentItem]) -> list[dict[str, Any]]:
    nav_pages = [page for page in pages if getattr(page, "show_in_nav", False)]
    nav_pages.sort(key=lambda page: (getattr(page, "nav_order", 9999), page.title.lower()))
    navigation = [
        {"title": "Home", "url": "/"},
        {"title": "Blog", "url": "/blog/"},
    ]
    navigation.extend({"title": page.title, "url": page.url} for page in nav_pages)
    return navigation


def build_tag_map(posts: list[ContentItem]) -> dict[str, list[ContentItem]]:
    tag_map: dict[str, list[ContentItem]] = {}
    for post in posts:
        for tag in post.tags:
            tag_map.setdefault(tag, []).append(post)
    return dict(sorted(tag_map.items(), key=lambda item: item[0].lower()))


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, value: str) -> None:
    ensure_dir(path)
    path.write_text(value, encoding="utf-8")


def copy_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def build_meta(site: dict[str, Any], title: str, description: str, url: str) -> dict[str, str]:
    canonical = f"{site['base_url'].rstrip('/')}{url}"
    return {
        "title": title,
        "description": description,
        "canonical_url": canonical,
        "og_title": title,
        "og_description": description,
        "og_url": canonical,
    }


def render_template(environment: Environment, template_name: str, destination: Path, **context: Any) -> None:
    template = environment.get_template(template_name)
    write_text(destination, template.render(**context))


def generate_redirect(output_dir: Path, old_path: str, new_url: str, canonical_url: str) -> None:
    target = html.escape(new_url, quote=True)
    canonical = html.escape(canonical_url, quote=True)
    target_json = '"' + new_url.replace("\\", "\\\\").replace('"', '\\"') + '"'
    write_text(
        output_dir / old_path,
        REDIRECT_TEMPLATE.format(target=target, canonical=canonical, target_json=target_json),
    )


def generate_feed(site: dict[str, Any], posts: list[ContentItem], output_dir: Path) -> None:
    updated = datetime.combine(posts[0].date_value, datetime.min.time()) if posts else datetime.utcnow()
    items: list[str] = []
    for post in posts[:20]:
        absolute_url = f"{site['base_url'].rstrip('/')}{post.url}"
        published = email.utils.format_datetime(datetime.combine(post.date_value, datetime.min.time()))
        description = html.escape(post.summary)
        items.append(
            "\n".join(
                [
                    "  <item>",
                    f"    <title>{html.escape(post.title)}</title>",
                    f"    <link>{html.escape(absolute_url)}</link>",
                    f"    <guid>{html.escape(absolute_url)}</guid>",
                    f"    <pubDate>{published}</pubDate>",
                    f"    <description>{description}</description>",
                    "  </item>",
                ]
            )
        )

    feed = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            "  <channel>",
            f"    <title>{html.escape(site['title'])}</title>",
            f"    <link>{html.escape(site['base_url'])}</link>",
            f"    <description>{html.escape(site['description'])}</description>",
            f"    <lastBuildDate>{email.utils.format_datetime(updated)}</lastBuildDate>",
            *items,
            "  </channel>",
            "</rss>",
        ]
    )
    write_text(output_dir / "feed.xml", feed)


def generate_sitemap(site: dict[str, Any], output_dir: Path, urls: list[str]) -> None:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        absolute = f"{site['base_url'].rstrip('/')}{url}"
        lines.extend(["  <url>", f"    <loc>{html.escape(absolute)}</loc>", "  </url>"])
    lines.append("</urlset>")
    write_text(output_dir / "sitemap.xml", "\n".join(lines))


def render_site(config: dict[str, Any], posts: list[ContentItem], pages: list[ContentItem], output_dir: Path) -> int:
    theme_root = ROOT / "themes" / config["theme"]
    templates_dir = theme_root / "templates"
    static_dir = theme_root / "static"

    if not templates_dir.exists():
        raise ValueError(f"Theme templates directory does not exist: {templates_dir}")

    environment = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    navigation = build_navigation(pages)
    tags = build_tag_map(posts)
    global_context = {
        "site": config["site"],
        "social": config["social"],
        "hero": config["hero"],
        "about": config["about"],
        "navigation": navigation,
        "posts": posts,
        "tags": tags,
        "current_year": datetime.now().year,
    }
    rendered_files = 0
    urls_for_sitemap = ["/", "/blog/"]

    for post in posts:
        meta = build_meta(config["site"], f"{post.title} | {config['site']['title']}", post.summary, post.url)
        render_template(
            environment,
            "blog_post.html",
            output_dir / post.output_rel_path,
            **global_context,
            post=post,
            page_title=meta["title"],
            page_description=meta["description"],
            canonical_url=meta["canonical_url"],
            og_title=meta["og_title"],
            og_description=meta["og_description"],
            og_url=meta["og_url"],
            active_url=post.url,
            body_class="blog-post-page",
        )
        rendered_files += 1
        urls_for_sitemap.append(post.url)
        for legacy_path in post.legacy_paths:
            generate_redirect(output_dir, legacy_path, post.url, meta["canonical_url"])
            rendered_files += 1

    for page in pages:
        meta = build_meta(config["site"], f"{page.title} | {config['site']['title']}", page.summary, page.url)
        render_template(
            environment,
            "page.html",
            output_dir / page.output_rel_path,
            **global_context,
            page=page,
            page_title=meta["title"],
            page_description=meta["description"],
            canonical_url=meta["canonical_url"],
            og_title=meta["og_title"],
            og_description=meta["og_description"],
            og_url=meta["og_url"],
            active_url=page.url,
            body_class="page",
        )
        rendered_files += 1
        urls_for_sitemap.append(page.url)
        for legacy_path in page.legacy_paths:
            generate_redirect(output_dir, legacy_path, page.url, meta["canonical_url"])
            rendered_files += 1

    blog_meta = build_meta(
        config["site"],
        f"Blog | {config['site']['title']}",
        "Essays on technology, systems, and ideas.",
        "/blog/",
    )
    render_template(
        environment,
        "blog_index.html",
        output_dir / "blog/index.html",
        **global_context,
        page_title=blog_meta["title"],
        page_description=blog_meta["description"],
        canonical_url=blog_meta["canonical_url"],
        og_title=blog_meta["og_title"],
        og_description=blog_meta["og_description"],
        og_url=blog_meta["og_url"],
        active_url="/blog/",
        body_class="blog-index-page",
    )
    rendered_files += 1

    home_meta = build_meta(config["site"], config["site"]["title"], config["site"]["description"], "/")
    render_template(
        environment,
        "index.html",
        output_dir / "index.html",
        **global_context,
        recent_posts=posts[:3],
        page_title=home_meta["title"],
        page_description=home_meta["description"],
        canonical_url=home_meta["canonical_url"],
        og_title=home_meta["og_title"],
        og_description=home_meta["og_description"],
        og_url=home_meta["og_url"],
        active_url="/",
        body_class="home-page",
    )
    rendered_files += 1

    not_found_meta = build_meta(config["site"], f"Page Not Found | {config['site']['title']}", "The page you requested could not be found.", "/404.html")
    render_template(
        environment,
        "404.html",
        output_dir / "404.html",
        **global_context,
        page_title=not_found_meta["title"],
        page_description=not_found_meta["description"],
        canonical_url=not_found_meta["canonical_url"],
        og_title=not_found_meta["og_title"],
        og_description=not_found_meta["og_description"],
        og_url=not_found_meta["og_url"],
        active_url="",
        body_class="not-found-page",
    )
    rendered_files += 1

    for old_path, target in {
        "category/blog.html": "/blog/",
        "archives.html": "/blog/",
        "tags.html": "/blog/",
        "authors.html": "/blog/",
        "contact.html": "/",
    }.items():
        generate_redirect(output_dir, old_path, target, f"{config['site']['base_url'].rstrip('/')}{target}")
        rendered_files += 1

    generate_feed(config["site"], posts, output_dir)
    rendered_files += 1
    generate_sitemap(config["site"], output_dir, urls_for_sitemap)
    rendered_files += 1

    if CNAME_PATH.exists():
        shutil.copy2(CNAME_PATH, output_dir / "CNAME")
        rendered_files += 1

    copy_tree(static_dir, output_dir / "static")
    if (CONTENT_ROOT / "assets").exists():
        copy_tree(CONTENT_ROOT / "assets", output_dir / "assets")
    write_text(output_dir / "static/pygments.css", HtmlFormatter(style="friendly").get_style_defs(".codehilite"))
    rendered_files += 1

    return rendered_files


def serve_output(output_dir: Path) -> None:
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    handler = http.server.SimpleHTTPRequestHandler
    os.chdir(output_dir)
    with ReusableTCPServer(("", 8000), handler) as httpd:
        print("Serving output at http://localhost:8000")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server.")


def main() -> None:
    args = parse_args()
    config = load_config()
    output_dir = ROOT / config["build"]["output_dir"]

    if args.clean and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    posts = load_content(BLOG_ROOT, "post", args.drafts)
    pages = load_content(PAGES_ROOT, "page", args.drafts)
    rendered_files = render_site(config, posts, pages, output_dir)

    page_label = "page" if len(pages) == 1 else "pages"
    post_label = "post" if len(posts) == 1 else "posts"
    print(
        f"Built {len(posts)} {post_label}, {len(pages)} {page_label}, "
        f"{rendered_files} files total -> {output_dir.relative_to(ROOT)}"
    )

    if args.serve:
        serve_output(output_dir)


if __name__ == "__main__":
    main()
