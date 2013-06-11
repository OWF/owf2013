#
# Register blueprint on app
#
def register_plugin(app):
  from .views import cfp
  app.register_blueprint(cfp)

  from .admin import register_plugin
  register_plugin(app)
