# coding=utf-8

# Configuration
SITE_URL = 'http://www.openworldforum.org/'
SITE_TITLE = 'Open World Forum 2013'
SITE_DESCRIPTION = "TODO"

ABSTRACT_LENGTH = 350

DEBUG = True
ASSETS_DEBUG = DEBUG
# FIXME later
#ASSETS_DEBUG = True
FLATPAGES_AUTO_RELOAD = True
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = '../pages'

# App configuration
FEED_MAX_LINKS = 25
SECTION_MAX_LINKS = 12

ALLOWED_LANGS = ['fr', 'en']

MAIN_MENU = {'fr': [('', u'Accueil'),
                    ('a-propos/', u'A propos'),
                    ('speakers/', u"Intervenants"),
                    ('programme/', u'Programe'),
                    ('lieu/', u'Lieu'),
                    ('news/', u'Actualités'),
                    ('registration/', u'Inscription', 'menu-registration')],
             'en': [('', u'Home'),
                    ('about/', u'About'),
                    ('speakers/', u"Speakers"),
                    ('program/', u'Program'),
                    ('venue/', u'Venue'),
                    ('news/', u'News'),
                    ('registration/', u'Registration', 'menu-registration')]}

