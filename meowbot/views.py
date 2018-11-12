import json
from itertools import groupby

import requests

import meowbot
from meowbot import app

from flask import jsonify, request, Response
from flask import render_template

from meowbot.models import AccessToken, Cat
from meowbot.util import requires_token, get_queue, get_config
from meowbot.worker import process_request


@app.route('/')
def index():
    return render_template('index.html', version=meowbot.__version__)


@app.route('/meow', methods=['POST'])
@requires_token
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


@app.route('/authorize')
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
        return 'Failure :(<br/>{}'.format(parsed['error'])


@app.route('/cats')
def cats():
    cats = Cat.query.order_by(Cat.name).all()
    grouped_cats = groupby(cats, lambda cat: cat.name)
    return render_template('cats.html', cats=grouped_cats, enumerate=enumerate)
