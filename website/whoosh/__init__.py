"""

    Whoosh flask extension
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 Stefane Fermigier / Abilian SAS

"""

import os
import whoosh.index
from whoosh.qparser import QueryParser
from whoosh import fields


DEFAULT_WHOOSH_INDEX_NAME = 'whoosh_index'

WHOOSH_SCHEMA = fields.Schema(title=fields.TEXT(stored=True),
                              content=fields.TEXT(stored=True),
                              summary=fields.TEXT(stored=True),
                              path=fields.ID(stored=True, unique=True))


class Whoosh(object):
  def __init__(self, app=None):
    if app:
      self.init_app(app)

  def init_app(self, app):
    self.schema = WHOOSH_SCHEMA
    wi = DEFAULT_WHOOSH_INDEX_NAME # TODO
    if whoosh.index.exists_in(wi):
      self.index = whoosh.index.open_dir(wi)
    else:
      if not os.path.exists(wi):
        os.makedirs(wi)
      self.index = whoosh.index.create_in(wi, self.schema)
    app.extensions['whoosh'] = self

  def add_document(self, doc):
    writer = self.index.writer()
    writer.add_document(**doc)
    writer.commit()

  def search(self, qs, max=50):
    with self.index.searcher() as searcher:
      parser = QueryParser("content", self.schema)
      query = parser.parse(qs)
      results = searcher.search(query)

      results = [{'title': r['title'],
                  'path': r['path'],
                  'summary': r['summary']}
                 for r in results]
      return results
