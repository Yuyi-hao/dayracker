import os

from flask import Flask
from dotenv import load_dotenv
from flask_session import Session

from . import db
from .auth import auth_bp

load_dotenv()
SECRET_KEY=os.getenv('SECRET_KEY')


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        DATABASE=os.path.join(app.instance_path, 'core.sqlite3')
    )
    # Configure session to use filesystem (instead of signed cookies)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except:
        pass

    db.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp)

    return app

    