"""
Main view (mostly technical views like sitemap or images).
"""

from cStringIO import StringIO
from itertools import groupby
import mimetypes
from os.path import join
from PIL import Image
import datetime
from abilian.services.image import crop_and_resize

from flask import Blueprint, redirect, url_for, request, abort, make_response, \
    render_template, current_app as app, session

from ..content import get_pages
from website.crm.models import Talk, Speaker
from website.util import preferred_language


__all__ = ['setup']

main = Blueprint('main', __name__, url_prefix='/')

ROOT = 'http://www.openworldforum.org'
REDIRECTS = [
  ('en/program/', '/en/schedule/'),
  ('en/Schedule', '/en/schedule/'),
  ('programme/', '/fr/programme/'),
  ('Programme/', '/fr/programme/'),
  ('Register', '/registration/'),
  ('en/register/', '/registration/'),
  ('join_form', '/registration/'),
  ('fre', '/fr/'),
  ('en/Sponsors', '/en/'),
  ('fr/accueil', '/fr/'),
  ('en/News', '/en/news/'),
  ('News', '/fr/news/'),
  ('open-innovation-summit-fr', '/'),
  ('connect/', '/'),
  ('awards/', '/'),
  ('Univers/Think/', '/fr/think/'),
  ('Univers/Code/', '/fr/code/'),
  ('Univers/Experiment/', '/fr/experiment/'),
  ('Univers/', '/fr/'),
  ('Conferences/', '/fr/programme/'),
  ('News/', '/fr/news/'),
  ('rss/feed/news', '/en/feed/'),
  ('rss/RSS', '/en/feed/'),
  ('fr/press/', '/fr/presse/'),
  ('fr/inscription/', '/fr/registration/'),
  ('fr/venue/', '/fr/lieu/'),
  ('fr/about/', '/fr/a-propos/'),
  ('2010/', '/fr/'),
  ('Articles/', '/fr/news/'),
  ('Conferences/', '/fr/programme/'),
  ('News/', '/fr/news/'),
  ('fr/News/', '/fr/news/'),
  ('Partenaires-presse/', '/fr/presse/'),
  ('Sponsors/', '/fr/sponsors/'),
  ('Tracks/', '/fr/programme/'),
  ('Univers/Schedule/', '/fr/programme/'),
  ('Users/', '/fr/'),
  ('attend/', '/fr/lieu/'),
  ('en/News/', '/en/news/'),
  ('en/Sponsors/', '/en/sponsors/'),
  ('en/Users/', '/en/'),
  ('eng/Univers/Code', '/en/code/'),
  ('press/', '/fr/presse/'),
  ('fre/', '/fr/'),
  ('eng/', '/en/'),
  ('index.php/', '/fr/'),
]

#
# Global (app-level) routes
#
@main.route('')
def index():
  lang = session.get('lang')
  if not lang:
    lang = preferred_language()
  if lang == 'fr':
    return redirect(url_for("localized.home", lang='fr'))
  else:
    return redirect(url_for("localized.home", lang='en'))


@main.route('robots.txt')
def robots_txt():
  return ""


@main.route('<path:path>')
def catch_all(path):
  for source, target in REDIRECTS:
    if path.startswith(source):
      return redirect(ROOT + target)

  abort(404)


@main.route('image/<path:path>')
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


@main.route('feed/')
def global_feed():
  return redirect("/en/feed/", 301)


@main.route('sitemap.xml')
def sitemap_xml():
  today = datetime.date.today()
  recently = datetime.date(year=today.year, month=today.month, day=1)
  response = make_response(render_template('sitemap.xml', pages=get_pages(),
                                           today=today, recently=recently))
  response.headers['Content-Type'] = 'text/xml'
  return response


@main.route('program')
def program():
  talks = Talk.query.order_by(Talk.track_id).all()
  data = groupby(talks, lambda t: t.track)
  page = dict(title="Program")
  return render_template("program.html", page=page, data=data)


@main.route('photo/<int:speaker_id>')
def photo(speaker_id):
  size = int(request.args.get('s', 55))
  if size > 500:
    raise ValueError("Error, size = %d" % size)

  speaker = Speaker.query.get(speaker_id)
  if not speaker:
    abort(404)

  if speaker.photo:
    data = speaker.photo
  else:
    data = DEFAULT_USER_MUGSHOT

  etag = None

  # TODO: caching
  if size:
    data = crop_and_resize(data, size)

  response = make_response(data)
  response.headers['content-type'] = 'image/jpeg'
  return response


#
# Register blueprint on app
#
def register_plugin(app):
  app.register_blueprint(main)
