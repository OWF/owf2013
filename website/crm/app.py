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

from .forms import SpeakerEditForm
from .models import Speaker


#
# Partenaires
#
class Speakers(Module):
  managed_class = Speaker

  list_view_columns = [
    dict(name='_name', width=35),
    dict(name='site_web', label="Web", width=25),
    dict(name='type_cotisation', width=20),
    dict(name='type_organisation', label="Type", width=15),
    dict(name='updated_at', label=_l(u'last modification',),
         display_fmt=format_datetime, width=15),
  ]

  edit_form_class = SpeakerEditForm

  related_views = []


#
# Main App
#
class CRM(CRUDApp):
  modules = [Speakers()]
  url = "/crm"
