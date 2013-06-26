from flask import render_template
from flask.ext.admin import BaseView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.login import current_user
from abilian.core.extensions import db
import itertools

from .models import TalkProposal
from .forms import THEMES


class TalkProposalView(ModelView):
  column_list = ['speaker_name', 'speaker_organization', 'title', 'theme']

  def is_accessible(self):
    return current_user.is_authenticated()


class AllTalksAdminView(BaseView):

  def is_accessible(self):
    return current_user.is_authenticated()

  @expose("/")
  def index(self):
    proposals = TalkProposal.query.order_by(TalkProposal.theme).all()
    proposals = itertools.groupby(proposals, lambda p: p.theme)

    themes = []
    for t, _ in THEMES:
      count = TalkProposal.query.filter(TalkProposal.theme == t).count()
      themes.append(dict(name=t, count=count))

    return render_template("cfp/alltalks.html",
                           themes=themes, proposals=proposals)


def register_plugin(app):
  admin = app.extensions['admin'][0]
  admin.add_view(AllTalksAdminView(name="AllTalks", endpoint="alltalks"))
  admin.add_view(TalkProposalView(TalkProposal, db.session))

