from flask import Flask
from app.utils.secrets_loader import SecretsLoader
from app.routes import route


def create_flask_app():
    app = Flask(__name__, static_folder="templates/assets")
    secrets = SecretsLoader()
    route(app=app)
    app.config.update(dict(SECRET_KEY=secrets.flask_app_secret_key))

    return app
