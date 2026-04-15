## karanjakhar.net

A custom static site generator for [karanjakhar.net](https://karanjakhar.net), built in plain Python with Jinja templates and Markdown content.

### Stack

- Python 3.11+
- `uv`
- `markdown`
- `pyyaml`
- `jinja2`
- `Pygments`

### Local development

Install dependencies:

```bash
uv sync
```

Build the site:

```bash
uv run python build.py
```

Build from a clean output directory:

```bash
uv run python build.py --clean
```

Include draft content:

```bash
uv run python build.py --drafts
```

Serve a local preview on `http://localhost:8000`:

```bash
uv run python build.py --serve
```

### Project structure

- `config.yaml` contains site metadata and theme selection.
- `content/blog/` stores blog posts with YAML frontmatter.
- `content/pages/` stores standalone pages.
- `content/assets/` stores images and other static content assets.
- `themes/minimal/` contains the tracked custom theme.
- `build.py` generates the static site into `output/`.
- `pyproject.toml` and `uv.lock` manage the Python environment.

### Deployment

GitHub Actions runs the regular build check on pushes and PRs, but production deployment now happens only when you push a `deploy-*` tag. The root `CNAME` file remains the source of truth for the custom domain and is copied into the build output during generation.

Trigger a deployment with one command:

```bash
./scripts/deploy.sh
```

The script creates a unique deploy tag for the current `HEAD` and pushes both your current branch and the tag to `origin`.
