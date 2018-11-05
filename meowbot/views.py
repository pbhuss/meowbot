import json
from itertools import groupby

import requests

import meowbot
from meowbot import app

from flask import jsonify, request, Response
from flask import render_template

from meowbot.appcontext import get_config
from meowbot.commands import CommandList
from meowbot.models import AccessToken, Cat
from meowbot.util import quote_user_id, requires_token, get_bot_access_token


@app.route('/')
def index():
    return render_template('index.html', version=meowbot.__version__)


def get_command(text):
    split = text.split(' ')
    if len(split) > 1:
        return split[1], split[2:]
    else:
        return None, None


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

    # If chat line begins with "@meowbot"
    if data['event']['text'].startswith(
        quote_user_id(data['authed_users'][0])
    ):
        bot_access_token = get_bot_access_token(data['team_id'])
        if not bot_access_token:
            meowbot.log.error(
                'Missing bot_access_token\nData: {}'.format(data)
            )
            return Response(status=200)
        command, args = get_command(data['event']['text'])
        resp = {
            'channel': data['event']['channel'],
        }
        if command:
            command_func = CommandList.get_command(command.lower())
            if command_func:
                resp.update(command_func(data, *args))
            else:
                resp['text'] = (
                    'Meow? (I don\'t understand `{}`). '
                    'Try `@meowbot help`.'.format(command)
                )
        else:
            resp['text'] = 'meow?'
        # Respond to thread if meowbot was mentioned in one
        if 'thread_ts' in data['event']:
            resp['thread_ts'] = data['event']['thread_ts']
        meowbot.log.debug(resp)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(bot_access_token)}
        requests.post(
            'https://slack.com/api/chat.postMessage',
            headers=headers,
            data=json.dumps(resp),
        )
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
