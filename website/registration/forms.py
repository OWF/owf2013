from flask.ext.wtf import Form, BooleanField, TextField, TextAreaField, required, email
from flask.ext.wtf.html5 import EmailField
from flask.ext.babel import lazy_gettext as _l

from website.registration.models import Track


__all__ = ['RegistrationForm']


def make_mixin_class():
  class DynamicMixin(object):
    pass

  for track in Track.query.all():
    label = "%s: %s" % (track.theme, track.title)
    name = "track_%d" % track.id
    field = BooleanField(label=label)
    setattr(DynamicMixin, name, field)

  return DynamicMixin


def make_registration_form_class():
  mixin_class = make_mixin_class()

  class RegistrationForm(mixin_class, Form):
    email = EmailField(label=_l(u"Your email address"),
                       validators=[required(), email()])

    coming_on_oct_3 = BooleanField(label=_l(u"Will you come on Oct. 3th? (Thursday)"))
    coming_on_oct_4 = BooleanField(label=_l(u"Will you come on Oct. 4th? (Friday)"))
    coming_on_oct_5 = BooleanField(label=_l(u"Will you come on Oct. 5th? (Saturday)"))

  return RegistrationForm


def make_confirmation_form_class():
  mixin_class = make_mixin_class()

  class ConfirmationForm(mixin_class, Form):
    email = EmailField(label=_l(u"Your email address"),
                       validators=[required(), email()])

    coming_on_oct_3 = BooleanField(label=_l(u"Will you come on Oct. 3th? (Thursday)"))
    coming_on_oct_4 = BooleanField(label=_l(u"Will you come on Oct. 4th? (Friday)"))
    coming_on_oct_5 = BooleanField(label=_l(u"Will you come on Oct. 5th? (Saturday)"))

    first_name = TextField(label=_l("First name"))
    last_name = TextField(label=_l("Last name"))
    organization = TextField(label=_l("Organization"))
    url = TextField(label=_l("URL"))
    url = TextAreaField(label=_l("Biography"))

    # twitter_handle = Column(UnicodeText(100), default="", nullable=False)
    # github_handle = Column(UnicodeText(200), default="", nullable=False)
    # sourceforge_handle = Column(UnicodeText(200), default="", nullable=False)
    # linkedin_url = Column(UnicodeText(200), default="", nullable=False)

  return ConfirmationForm

