#!/bin/bash
# Build and preview first
invoke preview

# Ask for confirmation
read -p "Ready to publish? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Publish to GitHub Pages
    invoke gh-pages
fi 