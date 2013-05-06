"""Manages content objects (aka pages).

"""

import re
from unicodedata import normalize
import bleach
import datetime
from flask import current_app, abort

from flask.ext.flatpages import Page

from .config import ABSTRACT_LENGTH


# Monkey patch
Page__init__orig = Page.__init__


def Page__init__(self, path, meta_yaml, body, html_renderer):
  Page__init__orig(self, path, meta_yaml, body, html_renderer)
  date = self.meta.get('date')

  if not date:
    self.meta['date'] = datetime.date.today()
  elif isinstance(date, str):
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    date = datetime.date(year, month, day)
    self.meta['date'] = date

  if not self.meta.get('slug'):
    dirname, filename = self.path.split('/')[-2:]
    if filename != 'index':
      self.meta['slug'] = filename
    else:
      self.meta['slug'] = dirname

  filename = self.path.split('/')[-1]
  if filename == 'index':
    self.meta['path'] = "/".join(self.path.split('/')[0:-1])
  else:
    self.meta['path'] = self.path

  # Autogenerates abstract if needed
  if not self.meta.get('abstract'):
    abstract = bleach.clean(self.html, tags=[], strip=True)
    if len(abstract) > ABSTRACT_LENGTH:
      abstract = abstract[0:ABSTRACT_LENGTH] + " [...]"
    self.meta['abstract'] = abstract

  if re.match("../news/", self.path):
    self.is_news = True
  else:
    self.is_news = False


Page.__init__ = Page__init__


def get_pages(offset=None, limit=None):
  """
  Retrieves pages matching passed criterias.
  """
  app = current_app
  pages = app.extensions['pages']
  articles = list(pages)
  # assign section value if none was provided in the metas
  for article in articles:
    if not article.meta.get('section'):
      article.meta['section'] = article.path.split('/')[0]

  # filter unpublished article
  if not app.debug:
    articles = [p for p in articles if p.meta.get('published') is True]

  # sort by date
  articles = sorted(articles, reverse=True,
                    key=lambda p: p.meta.get('date', datetime.date.today()))

  if offset and limit:
    return articles[offset:limit]
  elif limit:
    return articles[:limit]
  elif offset:
    return articles[offset:]
  else:
    return articles


def get_page(path):
  app = current_app
  pages = app.extensions['pages']
  return pages.get(path) or pages.get(path + '/index')


def get_page_or_404(path):
  page = get_page(path)
  if not page:
    abort(404)
  return page


def get_years(pages):
  years = list(set([page.meta.get('date').year for page in pages]))
  years.reverse()
  return years


def slugify(text, delim=u'-'):
  """Generates an slightly worse ASCII-only slug."""
  _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
  result = []
  for word in _punct_re.split(text.lower()):
    word = normalize('NFKD', word).encode('ascii', 'ignore')
    if word:
      result.append(word)
  return unicode(delim.join(result))


def get_news(offset=None, limit=None):
  all_pages = get_pages()
  all_news = [page for page in all_pages if page.is_news]
  if offset and len(all_news) > offset:
    all_news = all_news[offset:]
  if limit and len(all_news) > limit:
    all_news = all_news[:limit]
  return all_news
