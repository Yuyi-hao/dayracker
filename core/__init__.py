import os

from flask import Flask
from dotenv import load_dotenv
from flask_session import Session

from . import db
from .auth import auth_bp
from .day_entry import day_entry_bp
from .habits import habits_bp
from .storage import LocalStorage, ImageKitStorage
from .summary import summary_bp

load_dotenv()
SECRET_KEY=os.getenv('SECRET_KEY')
ENVIRONMENT=os.getenv('ENVIRONMENT')

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
    
    if ENVIRONMENT=="local":
        app.storage = LocalStorage()
    elif ENVIRONMENT=='prod':
        IMAGEKIT_PRIVATE_KEY=os.getenv('IMAGEKIT_PUBLIC')
        IMAGEKIT_PUBLIC_KEY=os.getenv('IMAGEKIT_PRIVATE')
        IMAGEKIT_URL_ENDPOINT=os.getenv('IMAGEKIT_URL')
        app.storage = ImageKitStorage(IMAGEKIT_PRIVATE_KEY, IMAGEKIT_PUBLIC_KEY ,IMAGEKIT_URL_ENDPOINT)

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
    app.register_blueprint(day_entry_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(summary_bp)

    return app

    