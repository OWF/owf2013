from yota import Form, Check
from yota.nodes import *
from yota.validators import RequiredValidator, EmailValidator, \
  MinLengthValidator


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
  speaker_name = EntryNode(title=u"Your name")
  _speaker_name_valid = Check(RequiredValidator(), 'speaker_name')

  speaker_title = EntryNode(title=u"Your title")
  _speaker_title_valid = Check(RequiredValidator(), 'speaker_title')

  speaker_organization = EntryNode(title=u"Your organization")
  _speaker_organization_valid = Check(RequiredValidator(),
                                      'speaker_organization')

  speaker_email = EntryNode(title=u"Your email address")
  _speaker_email_valid = Check(EmailValidator(), 'speaker_email')

  speaker_bio = TextareaNode(title=u"Your bio", columns=60)
  _speaker_bio_valid = Check(RequiredValidator(), 'speaker_bio')

  title = EntryNode(title=u"Your talk title")
  _title_valid = Check(RequiredValidator(), 'title')

  abstract = TextareaNode(title=u"Your talk abstract", rows=15, columns=60)
  _abstract_valid = Check(RequiredValidator(), 'abstract')

  theme = RadioNode(title=u"Choose a theme",
                    buttons=THEMES)
  _theme_valid = Check(RequiredValidator(), 'theme')

  # sub_theme = RadioNode(title=u"Select one or several subthemes")
  # _radio_valid = Check(RequiredValidator(), 'sub_theme')

  submit = SubmitNode(title="Submit")
