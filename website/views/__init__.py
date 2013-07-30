#
# Register blueprints on app
#
def register_plugin(app):
  from .localized import localized
  app.register_blueprint(localized)

  from .main import main
  app.register_blueprint(main)
