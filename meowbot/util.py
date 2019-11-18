import hmac
import json
import time
from functools import wraps, lru_cache

import redis
import rq
import yaml
from flask import Response, request
from geopy import Nominatim

import meowbot
from instance.config import REDIS_URL
from meowbot.models import AccessToken


YAML_CONF_PATH = "instance/config.yaml"


@lru_cache(maxsize=1)
def get_config():
    with open(YAML_CONF_PATH, "r") as fp:
        return yaml.safe_load(fp)


def get_signing_secret():
    return get_config()["signing_secret"].encode("utf-8")


def get_cat_api_key():
    return get_config()["cat_api_key"]


def get_airnow_api_key():
    return get_config()["airnow_api_key"]


def get_petfinder_api_key():
    return get_config()["petfinder_api_key"]


def get_darksky_api_key():
    return get_config()["darksky_api_key"]


def get_strava_client_id():
    return get_config()["strava_client_id"]


def get_strava_client_secret():
    return get_config()["strava_client_secret"]


def get_default_zip_code():
    return get_config()["default_zip_code"]


def get_admin_user_id():
    return get_config()["admin_user_id"]


def get_location(query):
    redis = get_redis()
    key = f"location:{query}"
    if redis.exists(key):
        raw_location = json.loads(redis.get(key).decode("utf-8"))
    else:
        geocoder = Nominatim(user_agent="https://github.com/pbhuss/meowbot")
        location = geocoder.geocode(query)
        if location is None:
            return None
        raw_location = location.raw
        redis.set(key, json.dumps(raw_location), ex=30 * 24 * 60 * 60)
    return raw_location


@lru_cache(maxsize=1)
def get_redis():
    return redis.StrictRedis.from_url(REDIS_URL)


def get_queue():
    return rq.Queue(connection=get_redis())


def get_channels():
    with open("instance/channels.json", "r", encoding="utf-8") as fp:
        return json.load(fp)


def restore_default_tv_channel():
    channels = get_channels()
    default_channel = get_config()["default_tv_channel"]
    url = channels[default_channel]["url"]
    r = get_redis()
    r.incr("tvid")
    r.set("tvchannel", url)
    return url


def verify_signature(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if (
            "X-Slack-Request-Timestamp" not in request.headers
            or "X-Slack-Signature" not in request.headers
        ):
            meowbot.log.warning("Request missing expected headers!")
            return Response(status=400)

        if (
            abs(
                time.time() - request.headers.get("X-Slack-Request-Timestamp", type=int)
            )
            > 60 * 5
        ):
            # The request timestamp is more than five minutes from local time.
            # It could be a replay attack, so let's ignore it.
            meowbot.log.warning("Request is possible replay attack!")
            return Response(status=400)

        msg = b":".join(
            (
                b"v0",
                request.headers.get("X-Slack-Request-Timestamp", as_bytes=True),
                request.get_data(),
            )
        )
        digest = hmac.new(get_signing_secret(), msg, "sha256").hexdigest()
        signature = request.headers["X-Slack-Signature"]
        if not hmac.compare_digest(f"v0={digest}", signature):
            meowbot.log.warning("Request failed signature check!")
            return Response(status=400)
        return f(*args, **kwargs)

    return decorated


def quote_user_id(user_id):
    return f"<@{user_id}>"


def get_bot_access_token(team_id):
    row = AccessToken.query.filter_by(team_id=team_id,).limit(1).one_or_none()
    if row:
        return row.bot_access_token
    return None


def with_app_context(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        with meowbot.app.app_context():
            return f(*args, **kwargs)

    return decorated


def check_auth(username, password):
    config = get_config()
    return username == config["admin_username"] and password == config["admin_password"]


def auth_response():
    """Sends a 401 response that enables basic auth"""
    return Response(
        "Could not verify your access level for that URL.\n"
        "You have to login with proper credentials",
        status=401,
        headers={"WWW-Authenticate": 'Basic realm="Login Required"'},
    )
