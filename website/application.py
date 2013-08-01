# coding=utf-8

import locale
from os import mkdir
from os.path import join, dirname, exists
import re
from abilian.services import audit_service, index_service, activity_service

from flask import Flask, abort, request, g, session
from flask.ext.admin import Admin
from flask.ext.bootstrap import Bootstrap
from flask.ext.frozen import Freezer
from flask.ext.flatpages import FlatPages
from flask.ext.markdown import Markdown
from flask.ext.assets import Environment as AssetManager

import abilian
from abilian.application import PluginManager
from abilian.core.extensions import Babel, db, mail
from abilian.web.filters import init_filters

from .registration.models import Track
from .tracks import TRACKS
from .util import preferred_language
from .whoosh import Whoosh


__all__ = ['create_app', 'create_db']


class Application(Flask, PluginManager):
  pass


def create_app(config=None):
  app = Application(__name__)
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
  mail.init_app(app)
  admin = Admin(app)
  bootstrap = Bootstrap(app)
  setup_filters_and_processors(app)

  #app.load_plugins()
  app.register_plugin("website.views")
  app.register_plugin("website.cfp")
  app.register_plugin("website.security")
  app.register_plugin("website.registration")
  app.register_plugin("website.crm")

  # Add some extensions
  whoosh = Whoosh(app)

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
  load_tracks(app)

  if not app.config.get('TESTING'):
    audit_service.init_app(app)
    audit_service.start()
    #index_service.init_app(app)
    #index_service.start()
    activity_service.init_app(app)
    activity_service.start()


def setup_babel(app):
  """
  Setup custom Babel config.
  """
  babel = Babel(app)

  def get_locale():
    lang = getattr(g, 'lang')
    if not lang:
      lang = session.get('lang')
    if not lang:
      lang = preferred_language()
    return lang

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


def load_tracks(app):
  with app.app_context():
    if Track.query.count() == 0:
      for track_id, track_title, track_theme, track_day in TRACKS:
        track = Track(title=track_title, theme=track_theme, day=track_day)
        db.session.add(track)
      db.session.commit()


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
      g.lang = ''
    if g.lang and not g.lang in app.config['ALLOWED_LANGS']:
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
