import re

from meowbot.conditions import RegexMatch, Condition
from meowbot.constants import Emoji
from meowbot.context import CommandContext
from meowbot.triggers import BaseTrigger
from meowbot.util import quote_user_id


class DatBoi(BaseTrigger):

    condition = RegexMatch(r"\bdat boi\b", re.IGNORECASE)

    def run(self, context: CommandContext):
        args = {
            "name": "datboi2",
            "channel": context.event.channel,
            "timestamp": context.event.ts,
        }
        context.api.reactions_add(args)


class Spicy(BaseTrigger):

    condition = RegexMatch(r"\bspicy\b", re.IGNORECASE)

    def run(self, context: CommandContext):
        args = {
            "name": Emoji.CHILIS.value,
            "channel": context.event.channel,
            "timestamp": context.event.ts,
        }
        context.api.reactions_add(args)


class Ugh(BaseTrigger):

    condition = RegexMatch(r"\bugh+\b", re.IGNORECASE)

    def run(self, context: CommandContext):
        args = {
            "name": Emoji.UGH.value,
            "channel": context.event.channel,
            "timestamp": context.event.ts,
        }
        context.api.reactions_add(args)


class Yubi(BaseTrigger):

    condition = RegexMatch(r"^eid[a-z]{41}$")

    def run(self, context: CommandContext):
        args = {
            "name": Emoji.YUBIKEY.value,
            "channel": context.event.channel,
            "timestamp": context.event.ts,
        }
        context.api.reactions_add(args)


class MeowbotMentioned(Condition):
    def __init__(self, suffix=""):
        self._suffix = suffix

    def evaluate(self, context: CommandContext):
        if context.event.text is None:
            return False
        lower_text = context.event.text.lower()
        return (
            f"meowbot{self._suffix}" in lower_text
            or f"{quote_user_id(context.bot_user)}{self._suffix}" in context.event.text
        )


class MeowShocked(BaseTrigger):

    condition = MeowbotMentioned(suffix="--")

    def run(self, context):
        args = {
            "name": Emoji.MEOW_SHOCKED.value,
            "channel": context.event.channel,
            "timestamp": context.event.ts,
        }
        context.api.reactions_add(args)


class MeowBlush(BaseTrigger):

    condition = MeowbotMentioned(suffix="++")

    def run(self, context):
        args = {
            "name": Emoji.MEOWBLUSH.value,
            "channel": context.event.channel,
            "timestamp": context.event.ts,
        }
        context.api.reactions_add(args)
