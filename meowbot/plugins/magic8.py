import random

from meowbot.commands import SimpleResponseCommand
from meowbot.constants import magic_eight_ball_options, Emoji
from meowbot.context import CommandContext
from meowbot.util import quote_user_id


class Magic8(SimpleResponseCommand):

    name = 'magic8'
    help = '`magic8 [question]`: tells your fortune',
    aliases = ['8ball']

    def get_message_args(self, context: CommandContext):
        text = '{} asked:\n>{}\n{}'.format(
            quote_user_id(context.event.user),
            ' '.join(context.args),
            random.choice(magic_eight_ball_options)
        )
        return {
            'text': text,
            'icon_emoji': f'{Emoji.EIGHT_BALL}'
        }
