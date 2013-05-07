# Import blueprint
from .app import CRM


def setup(app):
  crm = CRM(app)
