import re
import datetime

from flask import Blueprint, request, render_template, make_response, g
from flask.ext.babel import gettext as _

from website.config import MAIN_MENU, FEED_MAX_LINKS
from website.content import get_news, get_page_or_404, get_pages


mod = Blueprint('mod', __name__, url_prefix='/<lang>')


#
# Menu management
#
class MenuEntry(object):
  def __init__(self, path, label):
    self.path = path
    self.label = label
    self.active = False
    self.css_classes = []

  def __getitem__(self, key):
    if key == 'class':
      return " ".join(self.css_classes)
    raise IndexError


def get_menu():
  menu = []
  for t in MAIN_MENU[g.lang]:
    entry = MenuEntry(t[0], t[1])

    if entry.path == '':
      if re.match("^/../$", request.path):
        entry.active = True
    else:
      if request.path[len("/../"):].startswith(entry.path):
        entry.active = True
    if entry.active:
      entry.css_classes.append("active")
    if len(t) > 2:
      entry.css_classes.append(t[2])
    menu.append(entry)
  return menu


@mod.context_processor
def inject_menu():
  return dict(menu=get_menu())


#
# Deal with language
#
@mod.url_defaults
def add_language_code(endpoint, values):
  values.setdefault('lang', g.lang)


@mod.url_value_preprocessor
def pull_lang(endpoint, values):
  g.lang = values.pop('lang')


#
# Localized (mod-level) routes
#

#
# Localized (mod-level) routes
#
@mod.route('/')
def home():
  template = "index.html"
  page = {'title': 'Open World Forum 2013'}
  news = get_news(limit=6)
  return render_template(template, page=page, news=news)


@mod.route('/<path:path>/')
def page(path=""):
  page = get_page_or_404(g.lang + "/" + path + "/index")
  template = page.meta.get('template', '_page.html')
  return render_template(template, page=page)


@mod.route('/news/')
def news():
  all_news = get_news()
  recent_news = get_news(limit=5)
  page = {'title': _("News") }
  return render_template('news.html', page=page, news=all_news,
                         recent_news=recent_news)


@mod.route('/news/<slug>/')
def news_item(slug):
  page = get_page_or_404(g.lang + "/news/" + slug)
  recent_news = get_news(limit=5)
  return render_template('news_item.html', page=page,
                         recent_news=recent_news)


@mod.route('/feed/')
def feed():
  news_items = get_news(limit=FEED_MAX_LINKS)
  now = datetime.datetime.now()

  response = make_response(render_template('base.rss',
                                           news_items=news_items, build_date=now))
  response.headers['Content-Type'] = 'text/xml'
  return response


@mod.route('/sitemap/')
def sitemap():
  page = {'title': u"Plan du site"}
  pages = get_pages()

  return render_template('sitemap.html', page=page, pages=pages)


#
# Register blueprint on app
#
def setup(app):
  app.register_blueprint(mod)
