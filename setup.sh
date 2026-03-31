#!/bin/bash
echo "Downloading necessary Pelican dependencies..."

# Download the theme
mkdir -p themes
if [ ! -d "themes/pelican-fh5co-marble" ]; then
    echo "Cloning pelican-fh5co-marble theme..."
    git clone https://github.com/claudio-walser/pelican-fh5co-marble.git themes/pelican-fh5co-marble
else
    echo "Theme already exists."
fi

# Download the plugins
if [ ! -d "plugins" ]; then
    echo "Cloning pelican-plugins..."
    git clone https://github.com/getpelican/pelican-plugins.git plugins
else
    echo "Plugins already exist."
fi

echo "Setup complete! You can now run the project locally using: uv run invoke reserve"
