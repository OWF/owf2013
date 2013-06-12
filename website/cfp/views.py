
from markupsafe import Markup
from werkzeug.datastructures import MultiDict
from flask import Blueprint, render_template, request, flash, redirect, \
  url_for, current_app
from flask.ext.mail import Message

from abilian.core.extensions import db, mail

from .forms import TalkProposalForm
from .models import TalkProposal


__all__ = ['cfp']

cfp = Blueprint('cfp', __name__, template_folder='templates', url_prefix='/cfp')
route = cfp.route


@route('/')
def display_form():
  form = TalkProposalForm()
  rendered_form = form.render()
  page = dict(title="Submit your proposal")
  return render_template("cfp/form.html", page=page, form=rendered_form)


@route('/', methods=['POST'])
def submit_form():
  form = TalkProposalForm()
  data = request.form
  if not 'theme' in request.form:
    data = MultiDict(request.form)
    data['theme'] = ''
  validation = form.validate_render(data)

  if validation is True:
    proposal = TalkProposal()
    for k, v in data.items():
      setattr(proposal, k, v)
    send_proposal_by_email(proposal)
    db.session.add(proposal)
    db.session.commit()
    msg = Markup(
      "Thank you for your submission. <a href='/'>Back to the home page.</a>")
    flash(msg, "success")
    return redirect(url_for(".display_form"))

  else:
    page = dict(title="Submit your proposal")
    return render_template("cfp/form.html", page=page, form=validation)


def send_proposal_by_email(proposal):
  body = render_template("cfp/email.txt", proposal=proposal)
  msg = Message("New talk proposal for OWF 2013",
                body=body,
                sender="sf@abilian.com",
                recipients=["sf@fermigier.com", "program@openworldforum.org"])
  mail.send(msg)
