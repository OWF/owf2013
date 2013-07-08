from itsdangerous import URLSafeSerializer
from datetime import datetime
from markupsafe import Markup
from flask import Blueprint, render_template, request, flash, redirect, \
    url_for, current_app as app, session
from flask.ext.babel import lazy_gettext as _l, gettext as _
from flask.ext.mail import Message

from abilian.core.extensions import db, mail

from ..util import preferred_language
from .forms import make_registration_form_class, make_confirmation_form_class
from .models import Registration, Track


__all__ = ['registration']

registration = Blueprint('registration', __name__, template_folder='templates',
                         url_prefix='/registration')
route = registration.route


@route('/')
def display_form():
  form = make_registration_form_class()()
  print form['track_1']

  page = dict(title=_l(u"Register as a participant"))
  tracks = Track.query.all()
  return render_template("registration/form.html",
                         page=page, tracks=tracks, form=form)


@route('/', methods=['POST'])
def submit_form():
  if request.form['_action'] == 'cancel':
    return redirect("/")
  tracks = Track.query.all()
  form = make_registration_form_class()(request.form)
  if form.validate():
    email = form.email.data.strip()
    registration = Registration.query.filter(Registration.email == email).first()
    if registration:
      if not email in session.get('email', {}):
        flash(_("This is not your email"), 'error')
        page = dict(title="Submit your proposal")
        return render_template("registration/form.html", page=page, form=form, tracks=tracks)
    else:
      registration = Registration()
      if 'email' in session:
        if isinstance(session['email'], basestring):
          session['email'] = {}
        session['email'][email] = True
      else:
        session['email'] = {email: True}

    form.populate_obj(registration)
    registration.tracks = []
    for field in form:
      if field.name.startswith("track_"):
        if field.data:
          id = int(field.name[len("track_"):])
          registration.tracks.append(Track.query.get(id))
    registration.ip_address = request.remote_addr
    registration.preferred_lang = preferred_language()

    db.session.add(registration)
    db.session.commit()
    msg = Markup(
      _(
        u"Thanks for registering to the OWF. An email has been sent to you "
        u"with further instructions."))
    flash(msg, "success")
    send_confirmation_email(registration)
    return redirect(url_for(".display_form"))

  else:
    page = dict(title="Submit your proposal")
    return render_template("registration/form.html", page=page, form=form)


@route('/confirm/<token>')
def confirmation(token):
  serializer = URLSafeSerializer(app.config['SECRET_KEY'])
  email = serializer.loads(token)
  registration = Registration.query.filter(Registration.email == email).one()
  registration.confirmed_at = datetime.utcnow()
  db.session.commit()
  flash(_("Your registration has been confirmed."), 'success')
  return redirect("/")




# @route('/confirmation/<token>')
# def confirmation_form(token):
#   form = make_confirmation_form_class()()
#   page = dict(title=_l(u"Confirm your participation"))
#   return render_template("registration/confirmation.html", page=page, form=form)
#
#
# @route('/confirmation/', methods=['POST'])
# def confirmation_form_submit():
#   if request.form['_action'] == 'cancel':
#     return redirect("/")
#   form = make_confirmation_form_class()(request.form)
#   if form.validate():
#     registration = Registration()
#     form.populate_obj(registration)
#     db.session.add(registration)
#     db.session.commit()
#     msg = Markup(
#       "Thank you for your submission. <a href='/'>Back to the home page.</a>")
#     flash(msg, "success")
#     return redirect(url_for(".display_form"))
#
#   else:
#     page = dict(title="Submit your proposal")
#     return render_template("registration/form.html", page=page, form=form)


def send_confirmation_email(registration):
  recipients = [registration.email]
  serializer = URLSafeSerializer(app.config['SECRET_KEY'])
  token = serializer.dumps(registration.email)
  body = render_template("registration/email/confirmation_fr.txt",
                         registration=registration, token=token)
  msg = Message(_("Please confirm your participation at the Open World Forum 2013"),
                body=body,
                sender="sf@abilian.com",
                recipients=recipients)
  print msg
  mail.send(msg)
