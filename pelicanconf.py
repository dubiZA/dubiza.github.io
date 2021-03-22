#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = 'Darius Hall'
SITENAME = 'dariushall.com'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'America/Denver'

# Defaults
DEFAULT_LANG = 'en'
DEFAULT_DATE = 'fs'
DEFAULT_PAGINATION = False
DEFAULT_METADATA = {
    'status': 'draft',
}

FILENAME_METADATA = '(?P<title>.*)'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'https://getpelican.com/'),
         ('Jinja2', 'https://palletsprojects.com/p/jinja/'),)

# Social widget
SOCIAL = (('LinkedIn', 'https://www.linkedin.com/in/dariushall/'),
          ('GitHub', 'https://github.com/dubiZA'),)

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True