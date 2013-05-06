#
# Localized (mod-level) routes
#
@mod.route('/')
def home():
  template = "index.html"
  page = {'title': 'Open World Forum 2013'}
  news = get_news(limit=6)
  return render_template(template, page=page, news=news)


@mod.route('/<path:path>/')
def page(path=""):
  page = get_page_or_404(g.lang + "/" + path + "/index")
  template = page.meta.get('template', '_page.html')
  return render_template(template, page=page)


@mod.route('/news/')
def news():
  all_news = get_news()
  recent_news = get_news(limit=5)
  page = {'title': _("News") }
  return render_template('news.html', page=page, news=all_news,
                         recent_news=recent_news)


@mod.route('/news/<slug>/')
def news_item(slug):
  page = get_page_or_404(g.lang + "/news/" + slug)
  recent_news = get_news(limit=5)
  return render_template('news_item.html', page=page,
                         recent_news=recent_news)


@mod.route('/feed/')
def feed():
  news_items = get_news(limit=FEED_MAX_LINKS)
  now = datetime.datetime.now()

  response = make_response(render_template('base.rss',
                                           news_items=news_items, build_date=now))
  response.headers['Content-Type'] = 'text/xml'
  return response


@mod.route('/sitemap/')
def sitemap():
  page = {'title': u"Plan du site"}
  pages = get_pages()

  return render_template('sitemap.html', page=page, pages=pages)

