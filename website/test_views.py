from .application import create_app


#class TestConfig(object):
#  SQLALCHEMY_DATABASE_URI = "sqlite://"


def test_home():
  app = create_app()
  client = app.test_client()

  with app.test_request_context():
    #db.create_all()

    response = client.get("/fr/")
    assert response.status_code == 200

    response = client.get("/en/")
    assert response.status_code == 200
