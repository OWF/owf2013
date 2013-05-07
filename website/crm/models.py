# coding=utf-8

"""
Entity objects for the CRM applications.

Part of the code is generated (imported from the `generated` module), part
is hand-crafted.

The goal is to have everything generated someday.
"""

import logging

from sqlalchemy.schema import Column
from sqlalchemy.types import UnicodeText

from savalidation import ValidationMixin
from flaskext.babel import gettext as _

from abilian.core.entities import Entity

from .extensions import EmailAddress, PhoneNumber


logger = logging.getLogger(__package__)

__all__ = ['Speaker'] # + Talk, Track, Session ?


#
# Domain classes
#
class Speaker(Entity, ValidationMixin):
  __tablename__ = 'speaker'

  title = Column(UnicodeText, nullable=True,
                 info={'label': u'Title'})
  title_CHOICES = [('', ''), ('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Dr', 'Dr'), ('Pr', 'Pr')]

  first_name = Column(UnicodeText, nullable=True,
                      info={'searchable': True, 'label': u'First name'})

  last_name = Column(UnicodeText, nullable=True,
                     info={'searchable': True, 'label': u'Last name'})

  email = Column(EmailAddress,
                 info={'label': 'E-mail'})

  telephone = Column(PhoneNumber, nullable=True,
                     info={'label': u'Telephone'})

  bio = Column(UnicodeText, nullable=True,
               info={'label': u'Biography'})

  @property
  def _name(self):
    return '%s %s' % (self.first_name, self.last_name)
