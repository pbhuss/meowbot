from meowbot.commands import SimpleResponseCommand
from meowbot.constants import Emoji
from meowbot.context import CommandContext


class Ping(SimpleResponseCommand):

    name = 'ping'
    help = '`ping`: see if meowbot is awake'

    def get_message_args(self, context: CommandContext):
        return {
            'text': 'pong!',
            'icon_emoji': f'{Emoji.PING_PONG}'
        }
