from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.login import current_user
from abilian.core.extensions import db

from .models import TalkProposal


class TalkProposalView(ModelView):
  column_list = ['speaker_name', 'speaker_organization', 'title', 'theme']

  def is_accessible(self):
    return current_user.is_authenticated()


def register_plugin(app):
  admin = app.extensions['admin'][0]
  admin.add_view(TalkProposalView(TalkProposal, db.session))

