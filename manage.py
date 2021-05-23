import os
from LeagueLogger import create_app
from .db_utils import db

from flask.ext.script import Manager, Shell

application = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(application)