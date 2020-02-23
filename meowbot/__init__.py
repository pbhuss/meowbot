import rq_dashboard

from flask import Flask, request
from flask.logging import create_logger

from instance.config import REDIS_URL
from meowbot.models import db
from meowbot.util import auth_response, check_auth
from meowbot.views import main


__version__ = "2.2.0"


def create_app(config_filename):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)

    db.init_app(app)

    app.register_blueprint(main)
    register_rq_dashboard(app)

    with app.app_context():
        db.create_all()

    return app


def register_rq_dashboard(app):
    app.config.from_object(rq_dashboard.default_settings)
    app.config["RQ_DASHBOARD_REDIS_URL"] = REDIS_URL

    @rq_dashboard.blueprint.before_request
    def requires_auth():
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return auth_response()

    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")


app = create_app("config.py")
log = create_logger(app)
