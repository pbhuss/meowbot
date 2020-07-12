import os

SERVER_NAME = os.environ["MEOWBOT_HOST"]
PREFERRED_URL_SCHEME = "https"
TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_DATABASE_URI = "sqlite:///../instance/meowbot.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
REDIS_URL = "redis://redis:6379/0"
