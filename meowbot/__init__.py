from flask import Flask
from flask.logging import create_logger

__version__ = '0.0.2'

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

import meowbot.views    # noqa

log = create_logger(app)
