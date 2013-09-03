# coding=utf-8

"""
Data model
==========

Speaker:
– Nom
– Prénom
– Email
– Phone
– Organisation
– Titre
– Bio
– Photo
– Twitter handle
– Github handle
– Sourceforge handle

Tracks:
– Room
– Theme (THINK/CODE/EXPERIMENT)
– Date/Heure de début
– Date/Heure de fin

Talks:
– Speaker
– Track
– Titre
– Abstract

"""
from datetime import timedelta

import logging
from markdown import markdown
from abilian.core.extensions import db
from sqlalchemy.orm import relationship, deferred
from sqlalchemy.schema import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.types import UnicodeText, DateTime, Integer, LargeBinary
from savalidation import ValidationMixin
from abilian.core.entities import Entity


PhoneNumber = UnicodeText
EmailAddress = UnicodeText

logger = logging.getLogger(__package__)

__all__ = ['Speaker'] # + Talk, Track, Session ?


#
# Domain classes
#
class Speaker(Entity, ValidationMixin):
  __tablename__ = 'speaker'

  salutation = Column(UnicodeText, nullable=True,
                      info={'label': u'Salutation'})
  salutation_CHOICES = [('', ''), ('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Dr', 'Dr'),
                        ('Pr', 'Pr')]

  first_name = Column(UnicodeText, nullable=True,
                      info={'searchable': True, 'label': u'First name'})

  last_name = Column(UnicodeText, nullable=True,
                     info={'searchable': True, 'label': u'Last name'})

  organisation = Column(UnicodeText, nullable=True,
                        info={'searchable': True, 'label': u'Organisation'})

  email = Column(EmailAddress,
                 info={'label': 'E-mail'})

  telephone = Column(PhoneNumber, nullable=True,
                     info={'label': u'Telephone'})

  bio = Column(UnicodeText, nullable=True,
               info={'label': u'Biography'})

  website = Column(UnicodeText, nullable=True,
                   info={'label': u'Web site'})

  twitter_handle = Column(UnicodeText, nullable=True,
                          info={'label': u'Twitter handle'})

  github_handle = Column(UnicodeText, nullable=True,
                         info={'label': u'GitHub handle'})

  sourceforge_handle = Column(UnicodeText, nullable=True,
                              info={'label': u'Sourceforge handle'})

  photo = deferred(Column(LargeBinary, nullable=True))

  @property
  def _name(self):
    return '%s %s' % (self.first_name, self.last_name)

  name = _name

  # @property
  # def has_bio(self):
  #   return not not self.bio
  #
  # @property
  # def has_photo(self):
  #   return not not self.photo


class Room(Entity, ValidationMixin):
  __tablename__ = 'room'

  name = Column(UnicodeText, nullable=False,
                info={'label': u'Name'})

  capacity = Column(Integer, nullable=False,
                    info={'label': u'Capacity'})


track_leader_to_track = Table(
  'track_leader_to_track', db.Model.metadata,
  Column('speaker_id', Integer, ForeignKey('speaker.id')),
  Column('track_id', Integer, ForeignKey('track2.id')),
  UniqueConstraint('speaker_id', 'track_id'),
)


class Track2(Entity, ValidationMixin):
  __tablename__ = 'track2'

  room_id = Column(ForeignKey(Room.id), nullable=True)
  room = relationship(Room, backref="tracks")

  name = Column(UnicodeText, nullable=False,
                info={'label': u'name'})

  theme = Column(UnicodeText, nullable=True,
                 info={'label': u'Theme'})

  description = Column(UnicodeText)

  starts_at = Column(DateTime, nullable=True,
                     info={'label': u'Starts at'})

  ends_at = Column(DateTime, nullable=True,
                   info={'label': u'Ends at'})

  track_leaders = relationship(Speaker, secondary=track_leader_to_track,
                               backref='leads_tracks')

  @property
  def abstract(self):
    return self.description


speaker_to_talk = Table(
  'speaker_to_talk', db.Model.metadata,
  Column('speaker_id', Integer, ForeignKey('speaker.id')),
  Column('talk_id', Integer, ForeignKey('talk.id')),
  UniqueConstraint('speaker_id', 'talk_id'),
)


class Talk(Entity, ValidationMixin):
  __tablename__ = 'talk'

  track_id = Column(ForeignKey(Track2.id), nullable=False)
  track = relationship(Track2, backref="talks")

  speakers = relationship(Speaker, secondary=speaker_to_talk,
                          backref='talks')

  title = Column(UnicodeText(200), nullable=False)

  abstract = Column(UnicodeText(2000), nullable=False)

  starts_at = Column(DateTime, nullable=True,
                     info={'label': u'Starts at'})

  duration = Column(Integer, nullable=True,
                    info={'label': u'Duration'})

  @property
  def ends_at(self):
    if not self.duration:
      return self.starts_at
    else:
      return self.starts_at + timedelta(minutes=self.duration)

  @property
  def abstract_rendered(self):
    return markdown(self.abstract)
