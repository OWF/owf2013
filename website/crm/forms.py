# coding=utf-8

"""

"""
import imghdr
import PIL
from flask import render_template_string

from flask.ext.babel import gettext as _
from markupsafe import Markup
from wtforms.validators import required, optional, ValidationError
from wtforms.fields import TextField, TextAreaField, IntegerField
from wtforms.widgets import FileInput
from wtforms_alchemy import model_form_factory

from abilian.web.forms import Form
from abilian.web.forms.filters import strip
from abilian.web.forms.widgets import EmailWidget, ListWidget
from abilian.web.forms.fields import Select2Field, QuerySelect2Field, \
  DateTimeField, FileField

from .models import Speaker, Room, Track2


TPL = """\
<input name="{{ field.name }}" type="file"
       {%- for attr, val in attrs.items() %} {{ attr }}="{{ val }}"{%- endfor %}
       />
"""


class ImageWidget(FileInput):
  def __call__(self, field, **kwargs):
    kwargs.setdefault('id', field.id)
    return Markup(render_template_string(TPL, field=field, attrs=kwargs))

  def render_view(self, field, **kwargs):
    if field:
      return "Some photo"
    else:
      return "No photo"


class ImageField(FileField):
  widget = ImageWidget()

  def populate_obj(self, obj, name):
    if self.has_file():
      setattr(obj, name, self.data.read())


ModelForm = model_form_factory(Form)


class SpeakerEditForm(ModelForm):
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

  organisation = TextField(u'Organisation', filters=(strip,),
                           validators=[optional()])

  bio = TextAreaField(u'Biography', validators=[optional()])

  photo = ImageField('Photo', validators=[optional()])

  website = TextField(u'Web site', filters=(strip,), validators=[optional()])

  twitter_handle = TextField(u'Twitter handle', filters=(strip,),
                             validators=[optional()])

  github_handle = TextField(u'GitHub handle', filters=(strip,),
                            validators=[optional()])

  sourceforge_handle = TextField(u'Sourceforge handle', filters=(strip,),
                                 validators=[optional()])

  _groups = [
    ["Speaker",
     ['title', 'first_name', 'last_name', 'email', 'telephone', 'organisation',
      'bio', 'photo']],
    ["Additionnal details",
     ['website', 'twitter_handle', 'github_handle', 'sourceforge_handle']],
  ]

  def validate_photo(self, field):
    if not field.has_file():
      field.data = None
      return

    data = field.data
    filename = data.filename
    valid = any(map(filename.lower().endswith, ('.png', '.jpg', '.jpeg')))

    if not valid:
      raise ValidationError(_(u'Only PNG or JPG image files are accepted'))

    img_type = imghdr.what('ignored', data.read())

    if not img_type in ('png', 'jpeg'):
      raise ValidationError(_(u'Only PNG or JPG image files are accepted'))

    data.stream.seek(0)
    try:
      # check this is actually an image file
      im = PIL.Image.open(data.stream)
      im.load()
    except:
      raise ValidationError(_(u'Could not decode image file'))

    data.stream.seek(0)


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
    validators=[required()])

  name = TextField(u'Name', filters=(strip,), validators=[required()])

  theme = Select2Field(u'Theme',
                       choices=[('THINK', 'THINK'), ('CODE', 'CODE'),
                                ('EXPERIMENT', 'EXPERIMENT')],
                       filters=(strip,),
                       validators=[required()])

  track_leaders = QuerySelect2Field(
    u'Track leader(s)',
    get_label='_name',
    view_widget=ListWidget(),
    query_factory=lambda: Speaker.query.all(),
    multiple=True,
    validators=[optional()])

  description = TextAreaField(u"Description")

  starts_at = DateTimeField(u"Starts at", validators=[required()])

  ends_at = DateTimeField(u"End at", validators=[required()])

  _groups = [
    ["Track",
     ['name', 'theme', 'description', 'track_leaders', 'room', 'starts_at',
      'ends_at']]
  ]


class TalkEditForm(Form):
  title = TextField(u'Name', filters=(strip,), validators=[required()])

  speakers = QuerySelect2Field(
    u'Speakers',
    get_label='_name',
    view_widget=ListWidget(),
    query_factory=lambda: Speaker.query.all(),
    multiple=True,
    validators=[required()])

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
    ["Talk",
     ['title', 'speakers', 'track', 'abstract', 'starts_at', 'duration']]
  ]
