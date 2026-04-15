# AGENTS.md

## Overview

`karanjakhar.net` is a custom Python static site generator. The source of truth is this branch, and the generated site is written to `output/` and deployed to `gh-pages`.

## Project Structure

- `build.py`: the SSG entrypoint. Handles content loading, markdown rendering, templates, redirects, feed, sitemap, asset copying, and local serving.
- `config.yaml`: site metadata, theme selection, hero/about content, social links, and build settings.
- `content/blog/`: blog posts with YAML frontmatter.
- `content/pages/`: standalone pages with YAML frontmatter.
- `content/assets/`: static content assets copied to `/assets/` in the build output.
- `themes/minimal/`: tracked theme templates and CSS.
- `.github/workflows/deploy.yml`: CI build and deploy workflow.
- `CNAME`: custom domain, copied into `output/` during builds.
- `pyproject.toml` and `uv.lock`: Python dependency management via `uv`.

## Common Commands

- `uv sync`: install/update the environment.
- `uv run python build.py`: build the site.
- `uv run python build.py --clean`: rebuild from an empty `output/`.
- `uv run python build.py --drafts`: include draft content.
- `uv run python build.py --serve`: build and serve locally on port `8000`.

## Deployment

- Production deployment is handled by GitHub Actions in `.github/workflows/deploy.yml`.
- Deploys run only on `workflow_dispatch` or when a `deploy-*` tag is pushed.
- The workflow syncs dependencies with `uv sync --frozen`, builds with `uv run python build.py --clean`, and publishes `output/` to the `gh-pages` branch.
- The simplest deployment path is `./scripts/deploy.sh`.
- `./scripts/deploy.sh` requires a clean git worktree, creates a unique `deploy-<timestamp>-<sha>` tag from the current `HEAD`, and pushes both the current branch and the deploy tag to `origin`.
- Manual deploy flow, if needed:
  1. Commit the changes you want to publish.
  2. Run `uv run python build.py --clean` locally if you want to sanity-check the build before deploying.
  3. Create a tag matching `deploy-*`.
  4. Push your branch and the tag to `origin`.
  5. Wait for the GitHub Actions deploy workflow to publish the generated site to `gh-pages`.

## Content Conventions

- Blog posts use canonical URLs at `/blog/{slug}/`.
- Pages use canonical URLs at `/{slug}/`.
- Legacy Pelican URLs are still generated as redirect files.
- Frontmatter should stay YAML-based and concise.
- `summary` is explicit content, not auto-generated at template time.

## Editing Notes

- Keep the site static and JS-free unless there is a clear need.
- Use root-relative links in templates for normal navigation.
- Use `site.base_url` only for canonical/meta/feed/sitemap output.
- `output/` is generated and should not be edited by hand.
