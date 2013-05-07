# coding=utf-8

"""

"""

from flask.ext.wtf.form import Form
from wtforms.validators import optional
from wtforms.fields import TextField, TextAreaField

from abilian.web.forms import required, strip
from abilian.web.widgets import EmailWidget

from .extensions import Select2Field


class SpeakerEditForm(Form):

  title = Select2Field(u'Title',
                       choices=[('', ''), ('M', 'M'), ('Mme', 'Mme'), ('Dr', 'Dr'), ('Pr', 'Pr')],
                       filters=(strip,),
                       validators=[optional()])

  first_name = TextField(u'First name', filters=(strip,), validators=[optional()])

  last_name = TextField(u'Last name', filters=(strip,), validators=[required()])

  email = TextField(u'E-mail', view_widget=EmailWidget(), filters=(strip,), validators=[required()])

  telephone = TextField(u'Telephone', filters=(strip,), validators=[optional()])

  bio = TextAreaField(u'Biography', validators=[optional()])

  _groups = [
    ['Main', ['title', 'first_name', 'last_name', 'email', 'telephone', 'bio']],
  ]
