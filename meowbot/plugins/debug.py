from pprint import pformat

from meowbot.triggers import SimpleResponseCommand
from meowbot.conditions import IsCommand, And, IsUser
from meowbot.constants import Emoji
from meowbot.context import CommandContext
from meowbot.util import get_admin_user_id


class Ping(SimpleResponseCommand):

    condition = IsCommand(["ping"])
    help = "`ping`: see if meowbot is awake"

    def get_message_args(self, context: CommandContext):
        return {"text": "pong!", "icon_emoji": f"{Emoji.PING_PONG}"}


class Debug(SimpleResponseCommand):

    private = True
    condition = And(IsCommand(["debug"]), IsUser([get_admin_user_id()]))

    def get_message_args(self, context: CommandContext):
        context._data["token"] = "REMOVED"
        return {"text": pformat(context._data)}
