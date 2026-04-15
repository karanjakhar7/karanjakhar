#!/usr/bin/env bash

set -euo pipefail

tag_prefix="deploy"
timestamp="$(date -u +%Y%m%d-%H%M%S)"
short_sha="$(git rev-parse --short HEAD)"
tag="${tag_prefix}-${timestamp}-${short_sha}"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Refusing to deploy with uncommitted changes."
  echo "Commit or stash your work, then run this script again."
  exit 1
fi

current_branch="$(git rev-parse --abbrev-ref HEAD)"

echo "Creating deploy tag ${tag} from ${current_branch}..."
git tag "${tag}"

echo "Pushing ${current_branch} and ${tag} to origin..."
git push origin "${current_branch}" "${tag}"

echo "Deployment requested."
echo "GitHub Actions will publish this commit when the tag push is received."
