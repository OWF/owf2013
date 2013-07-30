# Import blueprint
from flask import request, abort
from flask.ext.login import current_user


def register_plugin(app):
  from .app import CRM
  CRM(app)

  from .views import crm
  app.register_blueprint(crm)

  @app.context_processor
  def inject_crm_modules():
    """
    Injects the CRM modules so that the CRM submenu can be set accordingly.

    This is defined at the (main) app level, not at the CRM blueprint level,
    because there are several blueprints in the CRM app.
    """
    modules = CRM.modules
    return dict(modules=modules)

  @app.before_request
  def check_permissions():
    if request.path.startswith("/crm/"):
      if not current_user.is_authenticated():
        abort(403)

