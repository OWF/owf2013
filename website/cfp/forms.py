from flask.ext.wtf import Form, required, email
from flask.ext.wtf.html5 import EmailField
from wtforms import StringField, TextAreaField, RadioField


THEMES = [
  # Think
  "THINK : Public Policies",
  "THINK : Collaborative and shared Innovation",
  "THINK : Education & Job",
  "THINK : Massive Open Online Courses (MOOC)",
  "THINK : Foundations and Communities",
  "THINK : Women in Tech",
  "THINK : Successes and Testimonials",
  "THINK : Cloud as a lock-in or an opportunity?",
  "THINK : CIO Summit",
  "THINK : Legal and licensing aspects of open source",
  "THINK : Other",
  # Code
  "CODE : Big Data",
  "CODE : Open Data and dataviz",
  "CODE : Mobile technologies",
  "CODE : Next-gen Web",
  "CODE : Web Accessibility",
  "CODE : Cloud and Infrastructure as Code",
  "CODE : Devops",
  "CODE : Internet of Things",
  "CODE : Cross-distro meetup",
  "CODE : Software Quality",
  "CODE : Other",
]
THEMES = [(x, x) for x in THEMES]


class TalkProposalForm(Form):
  speaker_name = StringField(label=u"Your name",
                             validators=[required()])

  speaker_title = StringField(label=u"Your title",
                              validators=[required()])

  speaker_organization = StringField(label=u"Your organization",
                                     validators=[required()])

  speaker_email = EmailField(label=u"Your email address",
                             validators=[required(), email()])

  speaker_bio = TextAreaField(label=u"Your bio",
                              validators=[required()])

  title = StringField(label=u"Your talk title",
                      validators=[required()])

  abstract = TextAreaField(label=u"Your talk abstract",
                           validators=[required()])

  theme = RadioField(label=u"Choose a theme",
                     choices=THEMES, validators=[required()])

  # sub_theme = RadioNode(title=u"Select one or several subthemes")
  # _radio_valid = Check(RequiredValidator(), 'sub_theme')
