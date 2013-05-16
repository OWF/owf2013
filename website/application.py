# coding=utf-8

import locale
from os import mkdir
from os.path import join, dirname, exists
import re

from flask import Flask, abort, request, g
from flask.ext.frozen import Freezer
from flask.ext.flatpages import FlatPages
from flask.ext.markdown import Markdown
from flask.ext.assets import Environment as AssetManager

import abilian
from abilian.core.extensions import Babel, db
from abilian.web.filters import init_filters

from .views import setup as setup_views
from .crm import setup as setup_crm

__all__ = ['create_app', 'create_db']


def create_app(config=None):
  app = Flask(__name__)
  if not config:
    from . import config
  app.config.from_object(config)
  setup(app)
  return app


#
# Setup helpers
#
def setup(app):
  db.init_app(app)

  setup_filters_and_processors(app)

  # Register our own blueprints / apps
  setup_views(app)
  setup_crm(app)

  # Add some extensions
  pages = FlatPages(app)
  app.extensions['pages'] = pages

  setup_freezer(app)
  markdown_manager = Markdown(app)
  asset_manager = AssetManager(app)
  app.extensions['asset_manager'] = asset_manager

  # Setup custome babel config (see below)
  setup_babel(app)

  # Setup hierarchical Jinja2 template loader
  # TODO: should be generic
  setup_template_loader(app)

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


def setup_filters_and_processors(app):

  # Register generic filters from Abilian Core
  init_filters(app)

  @app.template_filter()
  def to_rfc2822(dt):
    if not dt:
      return
    current_locale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, "en_US")
    formatted = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
    locale.setlocale(locale.LC_TIME, current_locale)
    return formatted

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
    if not g.lang in app.config['ALLOWED_LANGS']:
      abort(404)

  @app.context_processor
  def inject_app():
    return dict(app=app)

  @app.before_request
  def before_request():
    # FIXME
    g.user = None
    g.recent_items = []


def setup_freezer(app):
  """FIXME: not used and currently broken."""

  def url_generator():
    # URLs as strings
    yield '/fr/'

  freezer = Freezer(app)
  app.extensions['freezer'] = freezer
  freezer.register_generator(url_generator)
