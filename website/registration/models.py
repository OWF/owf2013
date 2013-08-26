from abilian.core.entities import Entity
from abilian.core.sqlalchemy import JSONList
from sqlalchemy import UnicodeText, Column, Boolean, String, ForeignKey, \
  UniqueConstraint, DateTime
from sqlalchemy.orm import relationship


class Registration(Entity):

  email = Column(UnicodeText, unique=True, nullable=False)

  confirmed_at = Column(DateTime)

  coming_on_oct_3 = Column(Boolean, nullable=False)
  coming_on_oct_4 = Column(Boolean, nullable=False)
  coming_on_oct_5 = Column(Boolean, nullable=False)

  ip_address = Column(String(20))
  preferred_lang = Column(String(5))

  first_name = Column(UnicodeText(100), default=u"", nullable=False)
  last_name = Column(UnicodeText(100), default=u"", nullable=False)
  organization = Column(UnicodeText(200), default=u"", nullable=False)
  biography = Column(UnicodeText(2000), default=u"", nullable=False)
  url = Column(UnicodeText(200), default=u"", nullable=False)

  twitter_handle = Column(UnicodeText(100), default=u"", nullable=False)
  github_handle = Column(UnicodeText(200), default=u"", nullable=False)
  sourceforge_handle = Column(UnicodeText(200), default=u"", nullable=False)
  linkedin_url = Column(UnicodeText(200), default=u"", nullable=False)

  #tracks = Column(JSONList(unique_sorted=True))

  @property
  def _name(self):
    if self.first_name:
      return self.first_name + " " + self.last_name
    else:
      return self.email

  def __getattr__(self, key):
    if key.startswith("track_"):
      if key in self.tracks:
        return True
      else:
        return False
    else:
      raise AttributeError("Not such attribute: %s" % key)


class Track(Entity):
  title = Column(UnicodeText(200), nullable=False)
  theme = Column(String(20), nullable=False)
  day = Column(String(3), nullable=False)
  description = Column(UnicodeText, nullable=False, default=u"")

  participants = relationship(Registration, secondary='participation',
                              backref='tracks')


class Participation(Entity):
  registration_id = Column(ForeignKey(Registration.id))
  registration = relationship(Registration)

  track_id = Column(ForeignKey(Track.id))
  track = relationship(Track)

  __table_args__ = (UniqueConstraint('registration_id', 'track_id'),)

