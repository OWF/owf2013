# coding=utf-8

from StringIO import StringIO

import locale
import mimetypes
from os import mkdir
from os.path import join, dirname, exists
import re
import datetime
from PIL import Image
from abilian.web.filters import init_filters

from flask import Flask, render_template, redirect, url_for, make_response, \
    abort, request, g
from flask.ext.frozen import Freezer
from flask.ext.flatpages import FlatPages
from flask.ext.markdown import Markdown
from flask.ext.assets import Environment as AssetManager

import abilian
from abilian.core.extensions import Babel, db

from . import config
from .content import get_pages
from .views import setup as setup_views
from .crm import setup as setup_crm

__all__ = ['app', 'setup']

app = Flask(__name__)

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
  if not g.lang in config.ALLOWED_LANGS:
    abort(404)


@app.context_processor
def inject_app():
  return dict(app=app)


@app.before_request
def before_request():
  # FIXME
  g.user = None
  g.recent_items = []


#
# Freezer helper
#
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
  return redirect("/en/feed/", 301)


@app.route('/sitemap.xml')
def sitemap_xml():
  today = datetime.date.today()
  recently = datetime.date(year=today.year, month=today.month, day=1)
  response = make_response(render_template('sitemap.xml', pages=get_pages(),
                                           today=today, recently=recently))
  response.headers['Content-Type'] = 'text/xml'
  return response


#
# Setup helpers
#
def setup(app):
  app.config.from_object(config)

  db.init_app(app)

  # Register our own blueprints / apps
  setup_views(app)
  setup_crm(app)

  # Add some extensions
  pages = FlatPages(app)
  app.extensions['pages'] = pages
  freezer = Freezer(app)
  app.extensions['freezer'] = freezer
  freezer.register_generator(url_generator)
  markdown_manager = Markdown(app)
  asset_manager = AssetManager(app)
  app.extensions['asset_manager'] = asset_manager

  # Setup custome babel config (see below)
  setup_babel(app)

  # Setup hierarchical Jinja2 template loader
  # TODO: should be generic
  setup_template_loader(app)

  # Add a few specific template filters
  init_filters(app)

  create_db(app)


def setup_babel(app):
  """
  Setup custom Babel config.
  """
  babel = Babel(app)

  def get_locale():
    return getattr(g, 'lang', 'en')

  babel.add_translations('website')
  babel.localeselector(get_locale)
  #babel.timezoneselector(get_timezone)


def setup_template_loader(app):
  """
  Not really a hack. Makes possible to get templates from several different
  directories, i.e. useful to override template from a library.
  """
  from jinja2 import ChoiceLoader, FileSystemLoader

  abilian_template_dir = join(dirname(abilian.__file__), "templates")
  my_loader = ChoiceLoader([app.jinja_loader,
                            FileSystemLoader(abilian_template_dir)])
  app.jinja_loader = my_loader


def create_db(app):
  if not exists("data"):
    mkdir("data")

  with app.app_context():
    db.create_all()
    for k,v in db.get_binds().items():
      print v, k

    # alembic_ini = join(dirname(__file__), '..', 'alembic.ini')
    # alembic_cfg = flask_alembic.FlaskAlembicConfig(alembic_ini)
    # alembic_cfg.set_main_option('sqlalchemy.url',
    #                             app.config.get('SQLALCHEMY_DATABASE_URI'))
    # alembic.command.stamp(alembic_cfg, "head")

    # if User.query.get(0) is None:
    #   root = User(id=0, last_name=u'SYSTEM', email=u'system@example.com',
    #               can_login=False)
    #   db.session.add(root)
    #   db.session.commit()
