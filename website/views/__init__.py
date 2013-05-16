
from .localized import register_plugin as setup_localized
from .main import register_plugin as setup_main


def setup(app):
  setup_localized(app)
  setup_main(app)