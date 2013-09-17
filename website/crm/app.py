# coding=utf-8
import StringIO
from datetime import date
from time import strftime, gmtime
from abilian.core.entities import Entity
from abilian.web.forms import ModelFieldList
from flask import g, request, make_response
from flask.ext.login import current_user
from xlwt import Workbook, XFStyle

from abilian.web.search import TextSearchCriterion
from abilian.web.frontend import Module as BaseModule, CRUDApp, expose

from website.cfp.forms import TalkProposalEditForm
from website.cfp.models import TalkProposal

from .forms import SpeakerEditForm, RoomEditForm, TrackEditForm, TalkEditForm
from .models import Speaker, Room, Track2, Talk


def allow_delete():
  return current_user.is_authenticated()


class Module(BaseModule):
  view_options = {'allow_delete': allow_delete}

  @expose("/export_xls")
  def export_to_xls(self):
    # TODO: take care of all the special cases
    wb = Workbook()
    ws = wb.add_sheet("Sheet 1")

    objects = self.ordered_query(request)
    form = self.edit_form_class()

    DATE_STYLE = XFStyle()
    DATE_STYLE.num_format_str = "DD/MM/YYYY"

    col_names = ['id']
    for field in form:
      if isinstance(field, ModelFieldList):
        continue
      if field.name == 'photo':
        continue
      if hasattr(self.managed_class, field.name):
        col_names.append(field.name)

    for c, col_name in enumerate(col_names):
      ws.write(0, c, col_name)

    for r, obj in enumerate(objects):
      for c, col_name in enumerate(col_names):
        style = None
        value = obj.display_value(col_name)

        if isinstance(value, Entity):
          value = value._name
        elif isinstance(value, list):
          if all(isinstance(x, basestring) for x in value):
            value = "; ".join(value)
          elif all(isinstance(x, Entity) for x in value):
            value = "; ".join([x._name for x in value])
          else:
            raise Exception("I don't know how to export column {}".format(col_name))
        elif isinstance(value, date):
          style = DATE_STYLE
        if style:
          ws.write(r+1, c, value, style)
        else:
          ws.write(r+1, c, value)

    fd = StringIO.StringIO()
    wb.save(fd)

    debug = request.args.get('debug_sql')
    if debug:
      # useful only in DEBUG mode, to get the debug toolbar in browser
      return '<html><body>Exported</body></html>'

    response = make_response(fd.getvalue())
    response.headers['content-type'] = 'application/ms-excel'
    filename = "%s-%s.xls" % (self.managed_class.__name__,
                              strftime("%d:%m:%Y-%H:%M:%S", gmtime()))
    response.headers['content-disposition'] = 'attachment;filename="%s"' % filename
    return response


class TalkProposals(Module):
  managed_class = TalkProposal

  icon = 'volume-up'

  list_view_columns = [
    dict(name='speaker_name', width=15),
    dict(name='title', width=50, linkable=True),
    dict(name='theme', width=35),
  ]

  edit_form_class = TalkProposalEditForm

  search_criterions = (
    TextSearchCriterion("name",
                        attributes=('title', 'speaker_name'),
                        search_fmt=[u'%{q}%', u'{q}%']),
  )


class Speakers(Module):
  managed_class = Speaker

  icon = 'user'

  list_view_columns = [
    dict(name='salutation', width=5, linkable=True),
    dict(name='first_name', width=20, linkable=True),
    dict(name='last_name', width=25, linkable=True),
    dict(name='organisation', width=25, linkable=True),
    dict(name='email', width=25),
  ]

  edit_form_class = SpeakerEditForm

  related_views = [
    (u'Talks', 'talks', (
      dict(name='title', linkable=True), 'track', 'starts_at', 'duration')),
  ]

  search_criterions = (
    TextSearchCriterion("name",
                        attributes=('first_name', 'last_name'),
                        search_fmt=[u'{q}%', u'{q}%']),
  )


class Rooms(Module):
  managed_class = Room

  icon = 'home'

  list_view_columns = [
    dict(name='name', width=50, linkable=True),
    dict(name='capacity', width=50),
  ]

  edit_form_class = RoomEditForm

  related_views = [
    (u'Tracks', 'tracks',
     (dict(name='name', linkable=True), 'starts_at', 'ends_at')),
  ]


class Tracks(Module):
  managed_class = Track2

  icon = 'calendar'

  list_view_columns = [
    dict(name='name', width=45, linkable=True),
    dict(name='theme', width=10),
    dict(name='room', width=10),
    dict(name='starts_at', width=18),
    dict(name='ends_at', width=17),
  ]

  edit_form_class = TrackEditForm

  related_views = [
    (u'Talks', 'talks',
     (dict(name='title', linkable=True), 'starts_at', 'duration')),
  ]

  search_criterions = (
    TextSearchCriterion("name",
                        attributes=('name',),
                        search_fmt=[u'%{q}%']),
  )


class Talks(Module):
  managed_class = Talk

  icon = 'volume-up'

  list_view_columns = [
    dict(name='title', width=40, linkable=True),
    dict(name='track', width=30),
    dict(name='starts_at', width=20),
    dict(name='duration', width=10),
  ]

  edit_form_class = TalkEditForm

  related_views = [
    (u'Speakers', 'speakers', ('first_name', 'last_name')),
  ]

  search_criterions = (
    TextSearchCriterion("name",
                        attributes=('title',),
                        search_fmt=[u'%{q}%']),
  )


#
# Main App
#
class CRM(CRUDApp):
  modules = [TalkProposals(), Speakers(), Rooms(), Tracks(), Talks()]
  url = "/crm"
