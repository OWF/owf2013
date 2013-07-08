#
# Register blueprint on app
#
def register_plugin(app):
  from .views import registration
  app.register_blueprint(registration)

  from .admin import register_plugin
  register_plugin(app)
