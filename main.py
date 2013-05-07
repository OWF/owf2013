#!/usr/bin/env python
# coding=utf-8

from logging import FileHandler

from argh import ArghParser
from fabric.operations import local

from website.application import app, setup
from website.config import DEBUG


setup(app)


def build():
  """ Builds this site.
  """
  print("Building website...")
  app.debug = False
  asset_manager = app.extensions['asset_manager']
  asset_manager.config['ASSETS_DEBUG'] = False

  freezer = app.extensions['freezer']
  freezer.freeze()

  local("cp ./static/*.ico ./build/")
  local("cp ./static/*.txt ./build/")
  local("cp ./static/*.xml ./build/")
  print("Done.")


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


def prod():
  serve(debug=False)


def dump():
  for rule in app.url_map.iter_rules():
    print rule


if __name__ == '__main__':
  parser = ArghParser()
  parser.add_commands([build, serve, prod, dump])
  parser.dispatch()
