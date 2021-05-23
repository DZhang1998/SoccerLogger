from flask import Flask
import os

# from .db_utils import db

def create_app():
    application = Flask(__name__,static_url_path='', static_folder='static')

    application.config['SECRET_KEY'] = os.urandom(16)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    application.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    application.register_blueprint(main_blueprint)
    return application