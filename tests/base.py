# Don't remove
import fix_path

import os
import requests
from os.path import join

from flask.ext.testing import TestCase

from abilian.core.extensions import db
from abilian.core.subjects import User

from website.application import create_app
from website import config


BASEDIR = os.path.dirname(__file__)

VALIDATOR_URL = 'http://html5.validator.nu/'

TEST_EMAIL = u"joe@example.com"
TEST_PASSWORD = "tototiti"


class TestConfig(object):
  def __init__(self):
    for k, v in vars(config).items():
      setattr(self, k, v)

    self.DEBUG = False
    self.TESTING = True
    self.CSRF_ENABLED = False
    self.SECRET_KEY = "tototiti"

    self.CELERY_ALWAYS_EAGER = True # run tasks locally, no async
    self.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

    self.SQLALCHEMY_DATABASE_URI = "sqlite://"
    self.SQLALCHEMY_ECHO = False

    self.WHOOSH_BASE = "whoosh"
    self.LOGGING_CONFIG_FILE = 'logging.yml'
    self.LOGGING_CONFIG_FILE = join(BASEDIR, self.LOGGING_CONFIG_FILE)

    self.VALIDATE = False

    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    if db_uri:
      self.SQLALCHEMY_DATABASE_URI = db_uri


def init_user():
  user = User(first_name=u"Joe", last_name=u"User", email=TEST_EMAIL,
              password=TEST_PASSWORD)
  db.session.add(user)
  db.session.flush()


class IntegrationTestCase(TestCase):

  #: set to True to load some (minimal) dummy data before each test
  init_data = False

  #: set to True to disable security
  no_login = False

  def create_app(self):
    config = TestConfig()
    config.NO_LOGIN = self.no_login
    self.app = create_app(config)

    return self.app

  def setUp(self):
    #self.app.create_db()
    self.session = db.session

    if self.init_data:
      init_user()
      #user = User.query.first()
      #login_user(user)
    #self.app.start_services()

  def tearDown(self):
    #self.app.stop_services()
    db.session.remove()
    db.drop_all()
    db.engine.dispose() # ensure we close all db connections

  def log_in_as_regular_user(self):
    d = dict(email=TEST_EMAIL, password=TEST_PASSWORD)
    response = self.client.post("/login/", data=d)
    self.assertEquals(response.status_code, 302)

  def assert_302(self, response):
    self.assert_status(response, 302)

  def assert_204(self, response):
    self.assert_status(response, 204)

  def get(self, url, validate=True):
    response = self.client.get(url)
    content_type = response.headers['Content-Type']
    if validate and self.app.config.get('VALIDATE') \
       and response.status_code == 200 \
       and content_type.split(';')[0].strip() == 'text/html':
      self.validate(url, response.data, content_type)
    return response

  def validate(self, url, content, content_type):
    response = requests.post(VALIDATOR_URL + '?out=json', content,
                             headers={'Content-Type': content_type})

    body = response.json

    for message in body['messages']:
      if message['type'] == 'error':
        detail = u'on line %s [%s]\n%s' % (
          message['lastLine'],
          message['extract'],
          message['message'])
        self.fail((u'Got a validation error for %r:\n%s' %
                   (url, detail)).encode('utf-8'))
