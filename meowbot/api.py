from enum import Enum
from typing import List

import requests
from requests import Response

from meowbot.util import get_bot_access_token


class SlackMethod(Enum):

    CHAT_POST_MESSAGE = (
        "https://slack.com/api/chat.postMessage",
        requests.post,
        ["channel"],
    )
    CHAT_POST_EPHEMERAL = (
        "https://slack.com/api/chat.postEphemeral",
        requests.post,
        ["channel", "user"],
    )
    CHAT_UPDATE = (
        "https://slack.com/api/chat.update",
        requests.post,
        ["channel", "ts"],
    )
    IM_OPEN = ("https://slack.com/api/im.open", requests.post, ["user"])
    REACTIONS_ADD = (
        "https://slack.com/api/reactions.add",
        requests.post,
        ["name", "channel", "timestamp"],
    )

    def __init__(self, url: str, http_method, required_arguments: List[str]):
        self.url = url
        self.http_method = http_method
        self.required_arguments = required_arguments


class SlackApiResponse:
    def __init__(self, response: Response):
        self._response = response
        self._data = self._response.json()

    @property
    def ok(self) -> bool:
        return self._response.status_code == 200 and self.data()["ok"]

    def __getattr__(self, item):
        if item not in self._data:
            raise AttributeError
        return self._data[item]


class SlackApi:
    def __init__(self, bot_access_token: str):
        self._bot_access_token = bot_access_token

    @classmethod
    def from_command_context(cls, context):
        bot_access_token = get_bot_access_token(context.team_id)
        if not bot_access_token:
            raise RuntimeError(f"Missing bot_access_token")
        return cls(bot_access_token)

    @classmethod
    def from_interactive_payload(cls, payload):
        bot_access_token = get_bot_access_token(payload.team["id"])
        if not bot_access_token:
            raise RuntimeError(f"Missing bot_access_token")
        return cls(bot_access_token)

    def _validate_arguments(self, method: SlackMethod, arguments: dict):
        included_arguments = set(arguments.keys())
        for required in method.required_arguments:
            if required not in included_arguments:
                raise ValueError(f"Method {method} requires argument {required}")

    def _make_request(self, method: SlackMethod, arguments: dict):
        self._validate_arguments(method, arguments)
        headers = {"Authorization": f"Bearer {self._bot_access_token}"}
        response = method.http_method(method.url, headers=headers, json=arguments,)
        return SlackApiResponse(response)

    def chat_post_message(self, arguments: dict) -> SlackApiResponse:
        return self._make_request(SlackMethod.CHAT_POST_MESSAGE, arguments)

    def chat_post_ephemeral(self, arguments: dict) -> SlackApiResponse:
        return self._make_request(SlackMethod.CHAT_POST_EPHEMERAL, arguments)

    def chat_update(self, arguments: dict) -> SlackApiResponse:
        return self._make_request(SlackMethod.CHAT_UPDATE, arguments)

    def im_open(self, arguments: dict) -> SlackApiResponse:
        return self._make_request(SlackMethod.IM_OPEN, arguments)

    def reactions_add(self, arguments: dict) -> SlackApiResponse:
        return self._make_request(SlackMethod.REACTIONS_ADD, arguments)

    def interactive_response(self, payload, arguments) -> SlackApiResponse:
        response = requests.post(payload.response_url, json=arguments)
        return SlackApiResponse(response)
