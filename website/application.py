# coding=utf-8

from StringIO import StringIO

import locale
import mimetypes
from os.path import join
import re
import datetime
from PIL import Image
from abilian.core.extensions import Babel

from flask import Flask, render_template, redirect, url_for, make_response, \
    abort, request, g
from flask.ext.frozen import Freezer
from flask.ext.flatpages import FlatPages, Page
from flask.ext.markdown import Markdown
from flask.ext.assets import Environment as AssetManager
from flask.ext.babel import gettext as _

from .config import *
from .content import get_pages
from .views import setup as views_setup


app = Flask(__name__)
app.config.from_object(__name__)

views_setup(app)

pages = FlatPages(app)
app.extensions['pages'] = pages
freezer = Freezer(app)
markdown_manager = Markdown(app)
asset_manager = AssetManager(app)


# Babel (for i18n)
# Additional config for Babel
def get_locale():
  return getattr(g, 'lang', None)

babel = Babel(app)
babel.add_translations('website')
babel.localeselector(get_locale)
#babel.timezoneselector(get_timezone)


#
# Filters
#
@app.template_filter()
def to_rfc2822(dt):
  if not dt:
    return
  current_locale = locale.getlocale(locale.LC_TIME)
  locale.setlocale(locale.LC_TIME, "en_US")
  formatted = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
  locale.setlocale(locale.LC_TIME, current_locale)
  return formatted


#
# Preprocessing
#
def alt_url_for(*args, **kw):
  if isinstance(args[0], Page):
    page = args[0]
    if re.match("../news/", page.path):
      return url_for(".news_item", slug=page.meta['slug'])
    else:
      return url_for(".page", path=page.meta['path'][3:])
  else:
    return url_for(*args, lang=g.lang, **kw)


@app.context_processor
def inject_context_variables():
  return dict(lang=g.lang,
              url_for=alt_url_for)


@app.url_defaults
def add_language_code(endpoint, values):
  values.setdefault('lang', g.lang)


@app.url_value_preprocessor
def pull_lang(endpoint, values):
  m = re.match("/(..)/", request.path)
  if m:
    g.lang = m.group(1)
  else:
    g.lang = 'fr'
  if not g.lang in ALLOWED_LANGS:
    abort(404)


#
# Freezer helper
#
@freezer.register_generator
def url_generator():
  # URLs as strings
  yield '/fr/'


#
# Global (app-level) routes
#
@app.route('/')
def index():
  # TODO: redirecte depending on HTTP headers & cookie
  return redirect(url_for("mod.home", lang='fr'))


@app.route('/image/<path:path>')
def image(path):
  hsize = int(request.args.get("h", 0))
  vsize = int(request.args.get("v", 0))

  if hsize > 1000 or vsize > 1000:
    abort(500)

  if '..' in path:
    abort(500)
  fd = open(join(app.root_path, "images", path))
  data = fd.read()

  if hsize:
    image = Image.open(StringIO(data))
    x, y = image.size

    x1 = hsize
    y1 = int(1.0 * y * hsize / x)
    image.thumbnail((x1, y1), Image.ANTIALIAS)
    output = StringIO()
    image.save(output, "PNG")
    data = output.getvalue()
  if vsize:
    image = Image.open(StringIO(data))
    x, y = image.size

    x1 = int(1.0 * x * vsize / y)
    y1 = vsize
    image.thumbnail((x1, y1), Image.ANTIALIAS)
    output = StringIO()
    image.save(output, "PNG")
    data = output.getvalue()

  response = make_response(data)
  response.headers['content-type'] = mimetypes.guess_type(path)
  return response


@app.route('/feed/')
def global_feed():
  return feed()


@app.route('/sitemap.xml')
def sitemap_xml():
  today = datetime.date.today()
  recently = datetime.date(year=today.year, month=today.month, day=1)
  response = make_response(render_template('sitemap.xml', pages=get_pages(),
                                           today=today, recently=recently))
  response.headers['Content-Type'] = 'text/xml'
  return response


@app.route('/403.html')
def error403():
  return render_template('403.html', page=dict(title="Fordidden"))


@app.route('/404.html')
def error404():
  return render_template('404.html', page=dict(title="Not found"))


@app.route('/500.html')
def error500():
  return render_template('500.html')


@app.errorhandler(404)
def page_not_found(error):
  page = {'title': _("Page not found")}
  return render_template('404.html', page=page), 404


