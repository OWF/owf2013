# coding=utf-8

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
    dict(name='first_name', width=35, linkable=True),
    dict(name='last_name', width=35, linkable=True),
    dict(name='email', width=3),
  ]

  edit_form_class = SpeakerEditForm

  related_views = [
    (u'Talks', 'talks', ('title', 'track', 'starts_at', 'duration')),
  ]


class Rooms(Module):
  managed_class = Room

  icon = 'home'

  list_view_columns = [
    dict(name='name', width=50, linkable=True),
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
    dict(name='name', width=40, linkable=True),
    dict(name='theme', width=30),
    dict(name='starts_at', width=15),
    dict(name='ends_at', width=15),
  ]

  edit_form_class = TrackEditForm

  related_views = [
    (u'Talks', 'talks', ('title', 'starts_at', 'duration')),
  ]


class Talks(Module):
  managed_class = Talk

  icon = 'volume-up'

  list_view_columns = [
    dict(name='title', width=40, linkable=True),
    dict(name='track', width=30),
    dict(name='starts_at', width=15),
    dict(name='duration', width=15),
  ]

  edit_form_class = TalkEditForm

  related_views = [
    (u'Speakers', 'speakers', ('first_name', 'last_name')),
  ]


#
# Main App
#
class CRM(CRUDApp):
  modules = [Speakers(), Rooms(), Tracks(), Talks()]
  url = "/crm"
