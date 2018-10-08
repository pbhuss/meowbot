from flask import Flask
from flask.logging import create_logger
from flask_sqlalchemy import SQLAlchemy

__version__ = '0.0.4'

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

import meowbot.views    # noqa
import meowbot.models   # noqa

db.create_all()

log = create_logger(app)
