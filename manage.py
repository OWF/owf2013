#!/usr/bin/env python
# coding=utf-8

from datetime import datetime
from dircache import listdir
from os import mkdir, system
import os
from os.path import exists
import csv
import bleach

from flask import current_app as app
from flask.ext.script import Manager

from website.application import create_app, db


DEBUG = True


manager = Manager(create_app)


@manager.shell
def make_shell_context():
  """
  Updates shell. (XXX: not sure what this does).
  """
  return dict(app=app, db=db)


@manager.command
def dump_routes():
  """
  Dump all the routes declared by the application.
  """
  for rule in app.url_map.iter_rules():
    print rule, rule.methods, rule.endpoint


@manager.command
def load_data():
  feedback = csv.reader(open("feedback.csv"))
  for row in feedback:
    row = map(lambda x: unicode(x, "utf8"), row)
    date = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
    reg = Registration(email=row[0],
                       first_name=u"",
                       last_name=row[1],
                       organization=row[2],
                       date=date)
    db.session.add(reg)
  db.session.commit()


@manager.command
def create_db():
  if not exists("data"):
    mkdir("data")

  with app.app_context():
    db.create_all()


@manager.command
def drop_db():
  """
  Drop the DB.
  """
  # TODO: ask for confirmation.
  with app.app_context():
    db.drop_all()


@manager.command
def add_user(email, password):
  from website.security import User2
  user = User2(email=email, password=password, active=True)
  db.session.add(user)
  db.session.commit()
  print "Password updated"


@manager.command
def set_password(email, password):
  from website.security import User2
  user = User2.query.filter(User2.email==email).one()
  user.password = password
  db.session.commit()
  print "Password updated"


@manager.command
def index_content():
  whoosh = app.extensions['whoosh']
  pages = app.extensions['pages']

  for page in pages:
    doc = {}
    doc['path'] = page['path']
    doc['title'] = unicode(page['title'])
    doc['content'] = page.body
    doc['summary'] = bleach.clean(page.html, tags=[], strip=True)
    if len(doc['summary']) > 200:
      doc['summary'] = doc['summary'][0:200] + '...'
    whoosh.add_document(doc)


@manager.command
def build():
  """ Builds this site.
  """
  print("Building website...")
  app.debug = False
  asset_manager = app.extensions['asset_manager']
  asset_manager.config['ASSETS_DEBUG'] = False

  freezer = app.extensions['freezer']
  freezer.freeze()

  system("cp ./static/*.ico ./build/")
  system("cp ./static/*.txt ./build/")
  system("cp ./static/*.xml ./build/")
  print("Done.")


@manager.command
def serve(server='0.0.0.0', port=5002, debug=DEBUG):
  """ Serves this site.
  """
  if not debug:
    import logging

    file_handler = FileHandler("error.log")
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

  asset_manager = app.extensions['asset_manager']
  asset_manager.config['ASSETS_DEBUG'] = debug

  app.debug = debug
  app.run(host=server, port=port, debug=debug)


if __name__ == '__main__':
  manager.run()


