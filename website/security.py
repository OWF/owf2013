# Define models
from abilian.core.extensions import db
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.login import current_user
from flask.ext.security import RoleMixin, UserMixin, SQLAlchemyUserDatastore,\
  Security


roles_users = db.Table(
  'roles_users',
  db.Column('user_id', db.Integer(), db.ForeignKey('user2.id')),
  db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))


class User2(db.Model, UserMixin):
  __tablename__ = 'user2'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(255), unique=True)
  password = db.Column(db.String(255))
  active = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())
  roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users', lazy='dynamic'))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User2, Role)
security = Security()


class SecureModelView(ModelView):
  def is_accessible(self):
    return current_user.is_authenticated()


def register_plugin(app):
  security.init_app(app, user_datastore)
  admin = app.extensions['admin'][0]
  admin.add_view(SecureModelView(User2, db.session))
  admin.add_view(SecureModelView(Role, db.session))

