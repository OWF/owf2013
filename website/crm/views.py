from abilian.services.security import security
from flask import Blueprint, abort, render_template
from flask.ext.login import current_user


crm = Blueprint("crm", __name__,
                template_folder='templates',
                url_prefix="/crm")


# @crm.before_request
# def check_security():
#   # FIXME: this is too tricky.
#   user = current_user._get_current_object()
#   if security.has_role(user, "crm:user"):
#     return
#   else:
#     abort(403)


# Hackish home page for the CRM apps. TODO: redefine & refactor.
@crm.route("/")
def crm_home():
  return render_template('crm/home.html', breadcrumbs=[("", "")])
