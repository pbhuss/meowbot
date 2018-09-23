import json

import requests

import meowbot
from meowbot import app

from flask import jsonify, request, Response
from flask import render_template

from meowbot.appcontext import get_config
from meowbot.commands import CommandList
from meowbot.util import quote_user_id, requires_token


@app.route('/')
def index():
    return render_template('index.html', version=meowbot.__version__)


def get_command(text):
    split = text.split(' ')
    if len(split) > 1:
        return split[1], split[2:]
    else:
        return None, None


# TODO: improve Slack workspace-specific token saving / loading
def get_bot_token(team_id):
    with open('tokens.json', 'r') as fp:
        for line in fp:
            row = json.loads(line)
            if row.get('team_id') == team_id:
                return row['bot']['bot_access_token']


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
        bot_token = get_bot_token(data['team_id'])
        if not bot_token:
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
            "Authorization": "Bearer {}".format(bot_token)}
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
        with open('tokens.json', 'a') as fp:
            fp.write(r.text)
            fp.write('\n')
        return 'Success!'
    else:
        meowbot.log.error(r.text)
        return 'Failure :(<br/>{}'.format(parsed['error'])
