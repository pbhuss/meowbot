import json

import requests

from meowbot.commands import CommandList
from meowbot.util import (
    get_bot_access_token,
    quote_user_id,
    get_redis,
    with_app_context
)


@with_app_context
def process_request(data):
    if data['event']['text'].startswith(
        quote_user_id(data['authed_users'][0])
    ):
        bot_access_token = get_bot_access_token(data['team_id'])
        if not bot_access_token:
            raise RuntimeError(f'Missing bot_access_token\nData: {data}')
        command, args = get_command(data['event']['text'])
        resp = {
            'channel': data['event']['channel'],
        }
        if command:
            command_func = CommandList.get_command(command.lower())
            if command_func:
                redis = get_redis()
                redis.hincrby('usage', command.lower())
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
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bot_access_token}"}
        requests.post(
            'https://slack.com/api/chat.postMessage',
            headers=headers,
            data=json.dumps(resp),
        )
        return resp


def get_command(text):
    split = text.split(' ')
    if len(split) > 1:
        return split[1], split[2:]
    else:
        return None, None
