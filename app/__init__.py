from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os, secrets

db = SQLAlchemy()

def createApp():
    app = Flask(__name__, template_folder='templates')

    app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

    app.config['SQLALCHEMY_DATABASE_URI'] = Config.connectionString
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"implicit_returning": False}

    db.init_app(app)

    from app.routes import mainRoutes
    app.register_blueprint(mainRoutes)

    return app
