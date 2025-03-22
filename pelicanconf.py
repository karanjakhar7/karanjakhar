AUTHOR = "Karan Jakhar"
SITENAME = "karanjakhar.net"
SITEURL = "https://karanjakhar.net"

PATH = "content"

TIMEZONE = "Asia/Kolkata"

DEFAULT_LANG = "en"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
# LINKS = (("Pelican", "https://getpelican.com/"),)

# Social widget
SOCIAL = (
    ("Linkedin", "https://www.linkedin.com/in/karanjakhar7"),
    ("Github", "https://www.github.com/karanjakhar7"),
)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# Sort articles by newest first in indexes
NEWEST_FIRST_ARCHIVES = True

# Also add these settings for consistent sorting across all pages
ARTICLE_ORDER_BY = "reversed-date"
INDEX_ORDER_BY = "reversed-date"

# Add custom CSS to hide footer credits
CUSTOM_CSS = "custom.css"
STATIC_PATHS = ["images", "extra/custom.css"]
EXTRA_PATH_METADATA = {"extra/custom.css": {"path": "custom.css"}}
