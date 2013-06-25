from markupsafe import Markup
from werkzeug.datastructures import MultiDict
from flask import Blueprint, render_template, request, flash, redirect, \
  url_for, current_app as app
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
  page = dict(title="Submit your proposal")
  return render_template("cfp/form.html", page=page, form=form)


@route('/', methods=['POST'])
def submit_form():
  if request.form['_action'] == 'cancel':
    return redirect("/")
  form = TalkProposalForm(request.form)
  if form.validate():
    proposal = TalkProposal()
    form.populate_obj(proposal)
    send_proposal_by_email(proposal)
    db.session.add(proposal)
    db.session.commit()
    msg = Markup(
      "Thank you for your submission. <a href='/'>Back to the home page.</a>")
    flash(msg, "success")
    return redirect(url_for(".display_form"))

  else:
    page = dict(title="Submit your proposal")
    return render_template("cfp/form.html", page=page, form=form)


def send_proposal_by_email(proposal):
  if app.config.get('TESTING'):
    recipients = ["sf@fermigier.com"]
  else:
    recipients = ["sf@fermigier.com", "program@openworldforum.org"]

  body = render_template("cfp/email.txt", proposal=proposal)
  msg = Message("New talk proposal for OWF 2013",
                body=body,
                sender="sf@abilian.com",
                recipients=recipients)
  mail.send(msg)
