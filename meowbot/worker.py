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
    # Ignore messages from bots
    if 'bot_id' in data['event']:
        return

    split_text = data['event']['text'].split(' ')
    bot_user_id = quote_user_id(data['authed_users'][0])

    # If message starts with `@meowbot`
    if split_text[0] == bot_user_id:
        if len(split_text) > 1:
            _, command, *args = split_text
        else:
            command = args = None
    # If message is direct IM, no `@meowbot` necessary
    elif data['event']['type'] == 'message':
        command, *args = split_text
    else:
        return

    bot_access_token = get_bot_access_token(data['team_id'])
    if not bot_access_token:
        raise RuntimeError(f'Missing bot_access_token\nData: {data}')
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
                f'Meow? (I don\'t understand `{command}`). '
                'Try `@meowbot help`.'
            )
    else:
        resp['text'] = 'meow?'
    # Respond to thread if meowbot was mentioned in one
    if 'thread_ts' in data['event']:
        resp['thread_ts'] = data['event']['thread_ts']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bot_access_token}'}
    requests.post(
        'https://slack.com/api/chat.postMessage',
        headers=headers,
        data=json.dumps(resp),
    )
    return resp
