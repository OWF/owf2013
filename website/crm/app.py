# coding=utf-8

"""
This module sets up the CRM webapp by instanciating and customizing a class
defined in Abilian Core.
"""
from flask.ext.babel import (
  gettext as _, ngettext as _n, lazy_gettext as _l,
  format_datetime, format_date,
  )

from abilian.web.frontend import Module, CRUDApp

from .forms import SpeakerEditForm, RoomEditForm, TrackEditForm, TalkEditForm
from .models import Speaker, Room, Track2, Talk


#
# Partenaires
#
class Speakers(Module):
  managed_class = Speaker

  icon = 'user'

  list_view_columns = [
    dict(name='first_name', width=35),
    dict(name='last_name', width=35),
    dict(name='email', width=3),
  ]

  edit_form_class = SpeakerEditForm

  related_views = [
    (u'Talks', 'talks', ('title', 'track', 'starts_at', 'ends_at')),
  ]


class Rooms(Module):
  managed_class = Room

  icon = 'home'

  list_view_columns = [
    dict(name='name', width=50),
    dict(name='capacity', width=50),
  ]

  edit_form_class = RoomEditForm

  related_views = [
    (u'Tracks', 'tracks', ('name', 'starts_at', 'ends_at')),
  ]


class Tracks(Module):
  managed_class = Track2

  icon = 'calendar'

  list_view_columns = [
    dict(name='name', width=40),
    dict(name='theme', width=30),
    dict(name='starts_at', width=15),
    dict(name='end_at', width=15),
  ]

  edit_form_class = TrackEditForm

  related_views = [
    (u'Talks', 'talks', ('title', 'starts_at', 'ends_at')),
  ]


class Talks(Module):
  managed_class = Talk

  icon = 'volume-up'

  list_view_columns = [
    dict(name='title', width=40),
    dict(name='track', width=30),
    dict(name='starts_at', width=15),
    dict(name='end_at', width=15),
  ]

  edit_form_class = TalkEditForm

  related_views = []


#
# Main App
#
class CRM(CRUDApp):
  modules = [Speakers(), Rooms(), Tracks(), Talks()]
  url = "/crm"
