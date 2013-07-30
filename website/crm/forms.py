# coding=utf-8

"""

"""

from flask.ext.wtf.form import Form
from wtforms.validators import optional
from wtforms.fields import TextField, TextAreaField, IntegerField, DateTimeField

from abilian.web.forms import required, strip
from abilian.web.widgets import EmailWidget, ListWidget

from .models import Speaker, Room, Track2
from .extensions import Select2Field, QuerySelect2Field


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

  bio = TextAreaField(u'Biography', validators=[optional()])

  website = TextField(u'Web site', filters=(strip,), validators=[optional()])

  twitter_handle = TextField(u'Twitter handle', filters=(strip,), validators=[optional()])

  github_handle = TextField(u'GitHub handle', filters=(strip,), validators=[optional()])

  sourceforge_handle = TextField(u'Sourceforge handle', filters=(strip,), validators=[optional()])

  _groups = [
    ["Speaker", ['title', 'first_name', 'last_name', 'email', 'telephone', 'bio']],
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

  description = TextAreaField(u"Description")

  starts_at = DateTimeField(u"Starts at", validators=[optional()])

  ends_at = DateTimeField(u"End at", validators=[optional()])

  _groups = [
    ["Track", ['name', 'description', 'room', 'starts_at', 'ends_at']]
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

  _groups = [
    ["Talk", ['title', 'speakers', 'track', 'abstract']]
  ]
