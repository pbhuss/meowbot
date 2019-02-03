import json
from functools import wraps, lru_cache

import redis
import rq
import yaml
from flask import Response, request
from geopy import Nominatim

import meowbot
from meowbot.models import AccessToken


YAML_CONF_PATH = 'instance/config.yaml'


@lru_cache()
def get_config():
    with open(YAML_CONF_PATH, 'r') as fp:
        return yaml.load(fp)


def get_verification_token():
    return get_config()['slack_verification_token']


def get_cat_api_key():
    return get_config()['cat_api_key']


def get_airnow_api_key():
    return get_config()['airnow_api_key']


def get_petfinder_api_key():
    return get_config()['petfinder_api_key']


def get_darksky_api_key():
    return get_config()['darksky_api_key']


def get_default_zip_code():
    return get_config()['default_zip_code']


def get_location(query):
    redis = get_redis()
    key = 'location:{}'.format(query)
    if redis.exists(key):
        raw_location = json.loads(redis.get(key).decode('utf-8'))
    else:
        geocoder = Nominatim(user_agent='https://github.com/pbhuss/meowbot')
        location = geocoder.geocode(query)
        if location is None:
            return None
        raw_location = location.raw
        redis.set(key, json.dumps(raw_location), ex=30 * 24 * 60 * 60)
    return raw_location


@lru_cache()
def get_redis():
    redis_url = get_config()['redis_url']
    return redis.StrictRedis.from_url(redis_url)


def get_queue():
    return rq.Queue(connection=get_redis())


def requires_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.get_json()['token'] != get_verification_token():
            return Response('Invalid token.', status=400)
        return f(*args, **kwargs)
    return decorated


def quote_user_id(user_id):
    return '<@{}>'.format(user_id)


def get_bot_access_token(team_id):
    row = AccessToken.query.filter_by(
        team_id=team_id,
    ).limit(
        1
    ).one_or_none()
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
    return (
        username == config['admin_username']
        and password == config['admin_password']
    )


def auth_response():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials',
        status=401,
        headers={'WWW-Authenticate': 'Basic realm="Login Required"'}
    )
