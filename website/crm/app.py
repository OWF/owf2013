# coding=utf-8

from abilian.web.frontend import Module, CRUDApp

from .forms import SpeakerEditForm, RoomEditForm, TrackEditForm, TalkEditForm
from .models import Speaker, Room, Track2, Talk
from website.cfp.forms import TalkProposalEditForm
from website.cfp.models import TalkProposal


class TalkProposals(Module):
  managed_class = TalkProposal

  icon = 'volume-up'

  list_view_columns = [
    dict(name='speaker_name', width=15),
    dict(name='title', width=50, linkable=True),
    dict(name='theme', width=35),
  ]

  edit_form_class = TalkProposalEditForm



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
    dict(name='name', width=45, linkable=True),
    dict(name='theme', width=15),
    dict(name='starts_at', width=20),
    dict(name='ends_at', width=20),
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
    dict(name='starts_at', width=20),
    dict(name='duration', width=10),
  ]

  edit_form_class = TalkEditForm

  related_views = [
    (u'Speakers', 'speakers', ('first_name', 'last_name')),
  ]


#
# Main App
#
class CRM(CRUDApp):
  modules = [TalkProposals(), Speakers(), Rooms(), Tracks(), Talks()]
  url = "/crm"
