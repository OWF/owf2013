# coding=utf-8

"""

"""

from flask.ext.wtf.form import Form
from wtforms.validators import optional
from wtforms.fields import TextField, TextAreaField, IntegerField

from abilian.web.forms.validators import required
from abilian.web.forms.filters import strip
from abilian.web.forms.widgets import EmailWidget, ListWidget
from abilian.web.forms.fields import Select2Field, QuerySelect2Field, DateTimeField

from .models import Speaker, Room, Track2


class SpeakerEditForm(Form):
  title = Select2Field(u'Title',
                       choices=[('', ''), ('M', 'M'), ('Mme', 'Mme'),
                                ('Dr', 'Dr'), ('Pr', 'Pr')],
                       filters=(strip,),
                       validators=[optional()])

  first_name = TextField(u'First name', filters=(strip,),
                         validators=[optional()])

  last_name = TextField(u'Last name', filters=(strip,), validators=[required()])

  email = TextField(u'E-mail', view_widget=EmailWidget(), filters=(strip,),
                    validators=[required()])

  telephone = TextField(u'Telephone', filters=(strip,), validators=[optional()])

  organisation = TextField(u'Organisation', filters=(strip,), validators=[optional()])

  bio = TextAreaField(u'Biography', validators=[optional()])

  website = TextField(u'Web site', filters=(strip,), validators=[optional()])

  twitter_handle = TextField(u'Twitter handle', filters=(strip,), validators=[optional()])

  github_handle = TextField(u'GitHub handle', filters=(strip,), validators=[optional()])

  sourceforge_handle = TextField(u'Sourceforge handle', filters=(strip,), validators=[optional()])

  _groups = [
    ["Speaker", ['title', 'first_name', 'last_name', 'email', 'telephone', 'organisation', 'bio']],
    ["Additionnal details", ['website', 'twitter_handle', 'github_handle', 'sourceforge_handle']],
  ]


class RoomEditForm(Form):
  name = TextField(u'Name', filters=(strip,), validators=[required()])

  capacity = IntegerField(u'Capacity', validators=[required()])

  _groups = [
    ["Room", ['name', 'capacity']]
  ]


class TrackEditForm(Form):
  room = QuerySelect2Field(
    u'Room',
    get_label='name',
    view_widget=ListWidget(),
    query_factory=lambda: Room.query.all(),
    multiple=False,
    validators=[optional()])

  name = TextField(u'Name', filters=(strip,), validators=[required()])

  # theme = Column(UnicodeText, nullable=True,
  #                info={'label': u'Theme'})

  track_leaders = QuerySelect2Field(
    u'Track leader(s)',
    get_label='_name',
    view_widget=ListWidget(),
    query_factory=lambda: Speaker.query.all(),
    multiple=True,
    validators=[optional()])

  description = TextAreaField(u"Description")

  starts_at = DateTimeField(u"Starts at", validators=[optional()])

  ends_at = DateTimeField(u"End at", validators=[optional()])

  _groups = [
    ["Track", ['name', 'description', 'track_leaders', 'room', 'starts_at', 'ends_at']]
  ]


class TalkEditForm(Form):
  title = TextField(u'Name', filters=(strip,), validators=[required()])

  speakers = QuerySelect2Field(
    u'Speakers',
    get_label='_name',
    view_widget=ListWidget(),
    query_factory=lambda: Speaker.query.all(),
    multiple=True,
    validators=[optional()])

  track = QuerySelect2Field(
    u'Track',
    get_label='name',
    view_widget=ListWidget(),
    query_factory=lambda: Track2.query.all(),
    multiple=False,
    validators=[required()])

  abstract = TextAreaField(u"Abstract")

  starts_at = DateTimeField(u"Starts at", validators=[optional()])

  duration = IntegerField(u"Duration (min)", validators=[optional()])

  _groups = [
    ["Talk", ['title', 'speakers', 'track', 'abstract', 'starts_at', 'duration']]
  ]
