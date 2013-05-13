"""
Main view (mostly technical views like sitemap or images).
"""

from cStringIO import StringIO
import mimetypes
from os.path import join
from PIL import Image
import datetime

from flask import Blueprint, redirect, url_for, request, abort, make_response, \
    render_template, current_app as app

from ..content import get_pages


__all__ = ['setup']

blueprint = Blueprint('main', __name__, url_prefix='/')


#
# Global (app-level) routes
#
@blueprint.route('/')
def index():
  # TODO: redirect depending on HTTP headers & cookie
  return redirect(url_for("localized.home", lang='fr'))


@blueprint.route('/image/<path:path>')
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


@blueprint.route('/feed/')
def global_feed():
  return redirect("/en/feed/", 301)


@blueprint.route('/sitemap.xml')
def sitemap_xml():
  today = datetime.date.today()
  recently = datetime.date(year=today.year, month=today.month, day=1)
  response = make_response(render_template('sitemap.xml', pages=get_pages(),
                                           today=today, recently=recently))
  response.headers['Content-Type'] = 'text/xml'
  return response


#
# Register blueprint on app
#
def setup(app):
  app.register_blueprint(blueprint)
