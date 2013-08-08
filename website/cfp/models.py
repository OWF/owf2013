from abilian.core.entities import Entity
from sqlalchemy import UnicodeText, Column


class TalkProposal(Entity):

  title = Column(UnicodeText, nullable=False)
  abstract = Column(UnicodeText, nullable=False)
  theme = Column(UnicodeText, nullable=False)
  sub_theme = Column(UnicodeText) # Not used currently

  speaker_name = Column(UnicodeText, nullable=False)
  speaker_title = Column(UnicodeText, nullable=False)
  speaker_organization = Column(UnicodeText, nullable=False)
  speaker_email = Column(UnicodeText, nullable=False)
  speaker_bio = Column(UnicodeText, nullable=False)

  #status = Column(UnicodeText)

  @property
  def _name(self):
    return self.title

