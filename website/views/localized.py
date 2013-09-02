"""
Localized view (i.e. language-specific subsites).
"""

from cStringIO import StringIO
from itertools import groupby
import mimetypes
from os.path import join, exists
from pprint import pprint
import random
import re
import datetime
from PIL import Image
from abilian.services.image import crop_and_resize

from flask import Blueprint, request, render_template, make_response, g, url_for, session, redirect
from flask import current_app as app
from flask.ext.babel import gettext as _
from werkzeug.exceptions import NotFound

from ..config import MAIN_MENU, FEED_MAX_LINKS, IMAGE_SIZES
from ..content import Page, get_news, get_page_or_404, get_pages, get_blocks
from ..crm.models import Speaker, Track2, Talk, Room


__all__ = ['setup']

localized = Blueprint('localized', __name__, url_prefix='/<string(length=2):lang>')
route = localized.route

#
# Menu management
#
class MenuEntry(object):
  def __init__(self, path, label):
    self.path = path
    self.label = label
    self.active = False
    self.css_classes = []

  def __getitem__(self, key):
    if key == 'class':
      return " ".join(self.css_classes)
    raise IndexError


def get_menu():
  menu = []
  for t in MAIN_MENU.get(g.lang, ()):
    entry = MenuEntry(t[0], t[1])

    if entry.path == '':
      if re.match("^/../$", request.path):
        entry.active = True
    else:
      if request.path[len("/../"):].startswith(entry.path):
        entry.active = True
    if entry.active:
      entry.css_classes.append("active")
    if len(t) > 2:
      entry.css_classes.append(t[2])
    menu.append(entry)
  return menu


@localized.context_processor
def inject_menu():
  return dict(menu=get_menu())


#
# Deal with language
#
def alt_url_for(obj, *args, **kw):
  if isinstance(obj, Page):
    if re.match("../news/", obj.path):
      return url_for(".news_item", slug=obj.meta['slug'])
    else:
      return url_for(".page", path=obj.meta['path'][3:])
  elif isinstance(obj, Speaker):
    return url_for(".speaker", speaker_id=obj.id)
  elif isinstance(obj, Track2):
    return url_for(".track", track_id=obj.id)
  elif isinstance(obj, Room):
    return url_for(".room", room_id=obj.id)
  elif isinstance(obj, Talk):
    return "%s#talk_%d" % (url_for(".track", track_id=obj.track.id), obj.id)
  elif obj in ('THINK', 'CODE', 'EXPERIMENT'):
    return url_for(".page", path=obj.lower())
  else:
    return url_for(obj, *args, lang=g.lang, **kw)


@localized.context_processor
def inject_context_variables():
  session['lang'] = g.lang
  return dict(lang=g.lang,
              url_for=alt_url_for)


@localized.url_defaults
def add_language_code(endpoint, values):
  values.setdefault('lang', g.lang)


@localized.url_value_preprocessor
def pull_lang(endpoint, values):
  g.lang = values.pop('lang')


#
# Localized routes
#
@route('/')
def home():
  template = "index.html"
  page = {'title': 'Open World Forum 2013'}
  news = get_news(lang=g.lang, limit=6)
  speakers = Speaker.query.all()
  if len(speakers) >= 12:
    speakers = random.sample(speakers, 12)
  else:
    speakers = []
  blocks = get_blocks(g.lang)
  return render_template(template,
                         page=page, news=news, speakers=speakers, blocks=blocks)


@route('/<path:path>/')
def page(path=""):
  page = get_page_or_404(g.lang + "/" + path + "/index")
  template = page.meta.get('template', '_page.html')
  return render_template(template, page=page)


@route('/news/')
def news():
  all_news = get_news(lang=g.lang)
  recent_news = get_news(lang=g.lang, limit=5)
  page = {'title': _("News") }
  return render_template('news.html', page=page, news=all_news,
                         recent_news=recent_news)


@route('/news/<slug>/')
def news_item(slug):
  page = get_page_or_404(g.lang + "/news/" + slug)
  recent_news = get_news(lang=g.lang, limit=5)
  return render_template('news_item.html', page=page,
                         recent_news=recent_news)


@route('/news/<slug>/image')
def image_for_news(slug):
  assert not '/' in slug
  size = request.args.get('size', 'large')

  file_path = join(app.root_path, "..", "pages", g.lang, "news", slug, "image.png")
  if not exists(file_path):
    file_path = join(app.root_path, "..", "pages", g.lang, "news", slug, "image.jpg")

  if not exists(file_path):
    file_path = join(app.root_path, "static", "pictures", "actu.png")

  img = Image.open(file_path)
  x, y = img.size
  x1, y1 = IMAGE_SIZES[size]
  r = float(x) / y
  r1 = float(x1) / y1
  if r > r1:
    y2 = y1
    x2 = int(float(x) * y1 / y)
    assert x2 >= x1
    img1 = img.resize((x2, y2), Image.ANTIALIAS)
    x3 = (x2-x1)/2
    img2 = img1.crop((x3, 0, x1+x3, y1))
  else:
    x2 = x1
    y2 = int(float(y) * x1 / x)
    assert y2 >= y1
    img1 = img.resize((x2, y2), Image.ANTIALIAS)
    y3 = (y2-y1)/2
    img2 = img1.crop((0, y3, x1, y1+y3))

  assert img2.size == (x1, y1)

  output = StringIO()
  if file_path.endswith(".jpg"):
    img2.save(output, "JPEG")
  else:
    img2.save(output, "PNG")
  data = output.getvalue()

  response = make_response(data)
  response.headers['content-type'] = mimetypes.guess_type(file_path)
  return response


@route('/feed/')
def feed():
  news_items = get_news(lang=g.lang, limit=FEED_MAX_LINKS)
  now = datetime.datetime.now()

  response = make_response(render_template('base.rss',
                                           news_items=news_items, build_date=now))
  response.headers['Content-Type'] = 'text/xml'
  return response


@route('/sitemap/')
def sitemap():
  page = {'title': _(u"Site map")}
  pages = get_pages()
  pages = [ p for p in pages if p.path.startswith(g.lang) ]

  return render_template('sitemap.html', page=page, pages=pages)


@route('/search')
def search():
  page = {'title': _(u"Search results")}
  qs = request.args.get('qs', '')
  whoosh = app.extensions['whoosh']
  results = whoosh.search(qs)
  results = [ r for r in results if r['path'].startswith(g.lang) ]
  return render_template("search.html", page=page, results=results)


@route('/program/')
def program():
  tracks = Track2.query.order_by(Track2.starts_at).all()
  tracks = [ t for t in tracks if t.starts_at]
  days = groupby(tracks, lambda t: t.starts_at.date())
  days = [(day, list(tracks)) for day, tracks in days]
  page = dict(title=_(u"Program"))
  return render_template("program.html", page=page, days=days)


@route('/tracks/')
def tracks():
  q = Track2.query.order_by(Track2.starts_at)
  theme = request.args.get('theme')
  if theme:
    theme = theme.upper()
    q = q.filter(Track2.theme == theme)
  tracks = q.all()
  tracks = [ t for t in tracks if t.starts_at]
  days = groupby(tracks, lambda t: t.starts_at.date())
  days = [(day, list(tracks)) for day, tracks in days]
  if theme:
    title = _(u"Program for theme %(theme)s", theme=theme)
  else:
    title = _(u"Program")
  page = dict(title=title)
  return render_template("program.html", page=page, days=days)


@route('/talks/')
def tracks():
  talks = Talk.query.order_by(Talk.starts_at).all()
  talks = [ t for t in talks if t.starts_at]
  days = groupby(talks, lambda t: t.starts_at.date())
  days = [(day, list(talks)) for day, talks in days]
  page = dict(title=_(u"Talks"))
  return render_template("talks.html", page=page, days=days)


@route('/rooms/')
def rooms():
  tracks = Track2.query.order_by(Track2.room_id).all()
  rooms = groupby(tracks, lambda t: t.room)
  rooms = [(room, sorted(list(tracks), key=lambda t: t.starts_at)) for room, tracks in rooms]
  rooms.sort(key=lambda r: -r[0].capacity)
  page = dict(title=_(u"Rooms"))
  return render_template("rooms.html", page=page, rooms=rooms)


@route('/rooms/<int:room_id>')
def room(room_id):
  room = Room.query.get_or_404(room_id)
  if not room:
    raise NotFound()

  tracks = Track2.query.order_by(Track2.starts_at).filter(Track2.room == room).all()
  tracks = [ t for t in tracks if t.starts_at]
  days = groupby(tracks, lambda t: t.starts_at.date())
  days = [(day, list(tracks)) for day, tracks in days]

  page = dict(title=_(u"Program for room %(room)s", room=room.name))
  return render_template("program.html", page=page, days=days)


@route('/tracks/<int:track_id>')
def track(track_id):
  track = Track2.query.get_or_404(track_id)
  page = {'title': track.name}
  return render_template("track.html", page=page, track=track)


@route('/speakers/')
def speakers():
  speakers = Speaker.query.order_by(Speaker.last_name).all()
  page = dict(title=_("Speakers"))
  return render_template("speakers.html", page=page, speakers=speakers)


@route('/speakers/<int:speaker_id>/')
def speaker(speaker_id):
  speaker = Speaker.query.get(speaker_id)
  if not speaker:
    raise NotFound()

  page = dict(title=speaker._name)
  return render_template("speaker.html", page=page, speaker=speaker)


@route('/speakers/<int:speaker_id>/photo')
def photo(speaker_id):
  size = int(request.args.get('s', 55))
  if size > 500:
    raise ValueError("Error, size = %d" % size)

  speaker = Speaker.query.get(speaker_id)
  if not speaker:
    raise NotFound()

  if speaker.photo:
    data = speaker.photo
  else:
    return redirect("/static/images/silhouette_unknown.png")

  # TODO: caching

  if size:
    data = crop_and_resize(data, size)

  response = make_response(data)
  response.headers['content-type'] = 'image/jpeg'
  return response

@route("/schedule/")
@route("/schedule/<int:day>/")
def schedule(day=None):
  if not day:
    return redirect(url_for(".schedule", day=1))

  if day == 1:
    track = Track2.query.get(8)
    talks = sorted(track.talks, key=lambda x: x.starts_at)
    page = dict(title=_(u"Day 1 - Plenary session"))
    summit = Track2.query.get(6)
    openstack = Track2.query.get(30)
    return render_template("day1.html", day=day, page=page, talks=talks,
                           summit=summit, openstack=openstack)

  else:
    talks_by_room = []
    rooms = Room.query.order_by(Room.capacity.desc()).all()
    for room in rooms:
      talks = talks_for_room_and_day(room, None)
      talks_by_room.append([room, talks])

    time_table = []
    for room in rooms:
      column = []
      talks = talks_for_room_and_day(room, None)
      t = datetime.datetime(2013, 10, 2+day, 9, 0)
      dt = datetime.timedelta(minutes=60)
      while t < datetime.datetime(2013, 10, 2+day, 20, 0):
        talks_for_slot = [ talk for talk in talks if t <= talk.starts_at < t+dt]
        column.append(talks_for_slot)
        t += dt
      time_table.append(column)

    time_table = zip(*time_table)

    page = dict(title=_(u"Day %(day)d - At a glance", day=day))
    return render_template("day23.html", day=day, page=page, rooms=rooms, time_table=time_table)


@localized.errorhandler(404)
def page_not_found(error):
  page = {'title': _(u"Page not found")}
  return render_template('404.html', page=page), 404


def talks_for_room_and_day(room, day):
  tracks = room.tracks
  talks = sum([track.talks for track in tracks], [])
  talks = [ talk for talk in talks if talk.starts_at ]
  return talks