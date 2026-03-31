#!/bin/bash
# Build and preview first
uv run invoke preview

# Ask for confirmation
read -p "Ready to publish? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Publish to GitHub Pages
    uv run invoke gh-pages
fi 