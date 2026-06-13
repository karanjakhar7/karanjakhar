---
name: publish-blog-post
description: >
  Publishes a blog post to karanjakhar.net. Use this skill whenever the user
  wants to publish, add, post, or commit a blog post — whether they paste raw
  markdown, give a file path, or describe a post they want to create. Handles
  all the plumbing: frontmatter generation, placing the file in the right
  directory, committing, and optionally deploying. Trigger this skill any time
  the user says things like "publish this post", "add this to my blog", "make
  this a blog post", "convert this markdown to a blog post", "post this to my
  site", or provides a .md file path alongside a blog-related request.
---

# Publish Blog Post

This skill turns markdown content into a properly structured blog post on
karanjakhar.net, commits it, and optionally deploys it.

## Blog project details

- **Repo**: `/Users/karan/karan/projects/blog/karanjakhar`
- **Posts directory**: `content/blog/`
- **Build command**: `uv run python build.py`
- **Deploy script**: `./scripts/deploy.sh`
- **Branch**: `custom-ssg`

## Step 1 — Gather the content

The user's input will be one of:
- **Raw markdown text** (pasted inline)
- **A file path** to a `.md` file

If user mentions a file name, first check the tmp/ dir in the current working dir.
If there are multiple files, ask user which one to publish.
If it's a file path, read the file. If the content is pasted directly, use it as-is.

## Step 2 — Determine frontmatter

Check whether the content already has a YAML frontmatter block (starts with `---`).

**If frontmatter already exists**, extract what's there. Fill in any missing required fields:
- `title`: required — if missing, derive from the first `# Heading` in the content, or ask the user
- `date`: required — if missing, use today's date in `YYYY-MM-DD` format
- `summary`: optional but recommended — if missing and the user didn't mention one, generate a 1-2 sentence summary from the opening paragraph
- `tags`: optional — leave as `[]` if not specified
- `draft`: set to `false` for a live post (this is a publish workflow)

**If no frontmatter**, construct it from scratch:
1. Derive `title` from the first `# Heading` in the content, or ask the user if none exists
2. Set `date` to today (`YYYY-MM-DD`)
3. Generate a short `summary` (≤220 chars) from the opening paragraph
4. Set `tags: []` unless the user specified tags
5. Set `draft: false`

**Frontmatter format:**
```yaml
---
title: "Your Post Title"
date: 2024-06-14
summary: "A brief description of what the post is about, kept under 220 characters."
tags: []
draft: false
---
```

## Step 3 — Generate the slug and file path

Derive the slug from the `title`:
- Lowercase everything
- Replace spaces and any non-alphanumeric characters with hyphens
- Collapse consecutive hyphens into one
- Strip leading/trailing hyphens

Example: `"The Art of Letting Go"` → `the-art-of-letting-go`

Target file path: `content/blog/{slug}.md`

**Check for conflicts**: if a file already exists at that path, tell the user and ask whether to overwrite or use a different slug.

## Step 4 — Write the file

Write the final markdown file to `content/blog/{slug}.md` inside the blog repo. The file should look like:

```markdown
---
title: "Post Title"
date: 2024-06-14
summary: "Brief summary here."
tags: []
draft: false
---

[post content body, with frontmatter stripped if it was embedded in the input]
```

Show the user a brief preview of the frontmatter before writing, so they can confirm the title/date/summary look right.

## Step 5 — Build and serve locally for preview

After committing, build the site and serve it locally so the user can verify the post before pushing live.

```bash
cd /Users/karan/karan/projects/blog/karanjakhar
uv run python build.py && uv run python -m http.server 8000 --directory dist
```

Tell the user: "Built and serving locally at http://localhost:8000 — take a look and let me know when you're ready to deploy, or if anything needs changing."

Wait for the user to respond before proceeding. Keep the server running in the background.

Once the user responds, stop the server. It shouldn't be running forever.

## Step 6 — Commit

From the blog repo directory, stage and commit:

```bash
cd /Users/karan/karan/projects/blog/karanjakhar
git add content/blog/{slug}.md
git commit -m "Add blog post: {title}"
```

Confirm the commit succeeded and show the commit hash.


## Step 7 — Ask about deployment

Only proceed here after the user explicitly says to deploy (e.g. "deploy it", "looks good", "push it").

Run the deploy script from the blog repo directory:
```bash
cd /Users/karan/karan/projects/blog/karanjakhar
./scripts/deploy.sh
```

The script will:
1. Create a `deploy-<timestamp>-<sha>` tag
2. Push the branch and tag to origin
3. GitHub Actions will build and push to GitHub Pages automatically

After it runs, tell the user: "Deployed. GitHub Actions is building the site now — it'll be live at karanjakhar.net in a minute or two."

## Edge cases

- **User pastes markdown without a title heading**: ask for the title before proceeding
- **Slug collision**: tell the user and ask what they want to do
- **Uncommitted changes in the repo already**: the deploy script will refuse — warn the user upfront and handle the commit properly before calling deploy
- **User wants to keep it as a draft**: set `draft: true` and skip the deployment question entirely, explaining that draft posts won't appear in the live build
