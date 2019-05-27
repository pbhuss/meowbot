import json
from itertools import groupby

import requests

import meowbot

from flask import jsonify, request, Response, Blueprint
from flask import render_template

from meowbot.models import AccessToken, Cat
from meowbot.util import (
    verify_signature,
    get_queue,
    get_config,
    get_redis,
    restore_default_tv_channel)
from meowbot.worker import process_request


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html', version=meowbot.__version__)


@main.route('/meow', methods=['POST'])
@verify_signature
def meow():
    data = request.get_json()
    meowbot.log.debug(data)

    # Slack URL verification check
    if data['type'] == 'url_verification':
        return jsonify(
            {"challenge": data['challenge']}
        )

    get_queue().enqueue(process_request, data=data)

    return Response(status=200)


@main.route('/authorize')
def authorize():
    r = requests.post(
        'https://slack.com/api/oauth.access',
        data={
            'client_id': get_config()['client_id'],
            'client_secret': get_config()['client_secret'],
            'code': request.args.get('code'),
            'redirect_uri': request.args.get('redirect_uri'),
        }
    )
    parsed = json.loads(r.text)
    if parsed['ok']:
        row = AccessToken(
            access_token=parsed['access_token'],
            scope=parsed['scope'],
            user_id=parsed['user_id'],
            team_name=parsed['team_name'],
            team_id=parsed['team_id'],
            bot_user_id=parsed['bot']['bot_user_id'],
            bot_access_token=parsed['bot']['bot_access_token']
        )
        meowbot.db.session.add(row)
        meowbot.db.session.commit()
        return 'Success!'
    else:
        meowbot.log.error(r.text)
        return f"Failure :(<br/>{parsed['error']}"


@main.route('/cats')
def cats():
    cats = Cat.query.order_by(Cat.name).all()
    grouped_cats = groupby(cats, lambda cat: cat.name)
    return render_template('cats.html', cats=grouped_cats, enumerate=enumerate)


@main.route('/tv/channel')
def tv_channel():
    redis = get_redis()
    channel = redis.get('tvchannel')
    if channel is None:
        channel = restore_default_tv_channel()
    return channel


@main.route('/tv')
def tv():
    return render_template('tv.html')
