AUTHOR = "Karan Jakhar"
SITENAME = "karanjakhar.net"
# Comment out the production SITEURL for local development
SITEURL = "https://karanjakhar.net"
# SITEURL = ""

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
RELATIVE_URLS = True

# Sort articles by newest first in indexes
NEWEST_FIRST_ARCHIVES = True

# Also add these settings for consistent sorting across all pages
ARTICLE_ORDER_BY = "reversed-date"
INDEX_ORDER_BY = "reversed-date"

# Add custom CSS to hide footer credits
CUSTOM_CSS = "custom.css"
STATIC_PATHS = ["images", "extra/custom.css"]
EXTRA_PATH_METADATA = {"extra/custom.css": {"path": "custom.css"}}

# Theme settings
THEME = "pelican-fh5co-marble"

# Plugin configuration
PLUGIN_PATHS = ["/Users/karan/pelican-plugins"]
PLUGINS = ["i18n_subsites"]
JINJA_ENVIRONMENT = {"extensions": ["jinja2.ext.i18n"]}
I18N_TEMPLATES_LANG = "en"
LOCALE = "en_US"

# Required for the theme
DIRECT_TEMPLATES = [
    "index",
    "tags",
    "categories",
    "authors",
    "archives",
    "contact",  # needed for the contact form
]

# Hero content configuration
HERO = [
    {
        "image": "/images/hero/background.jpg",
        "title": "Karan Jakhar",
        "text": "You have power over your mind - not outside events. Realize this, and you will find strength.",
        "links": [
            # {
            #     "icon": "icon-code",
            #     "url": "https://github.com/karanjakhar7",
            #     "text": "Github",
            # }
        ],
    }
]

# About section configuration
ABOUT = {
    "image": "/images/about/about.jpg",
    "mail": "",
    "text": "An Engineer passionate about technology and philosophy.",
    "link": "contact.html",
    "address": "India",
    "phone": "",
}

# You may need to install these plugins
# PLUGIN_PATHS = ['/path/to/pelican-plugins']
# PLUGINS = ['i18n_subsites', 'tipue_search']
# JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}
