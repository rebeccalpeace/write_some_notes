from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'You must be logged in to play.'
login.login_message_category = 'warning'


from app.blueprints.api import api
app.register_blueprint(api)

from . import routes, models
