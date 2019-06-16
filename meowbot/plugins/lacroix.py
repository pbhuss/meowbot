import random

from meowbot.commands import SimpleResponseCommand
from meowbot.constants import Emoji
from meowbot.context import CommandContext
from meowbot.util import quote_user_id


class Lacroix(SimpleResponseCommand):

    name = 'lacroix'
    help = '`lacroix`: meowbot recommends a flavor'

    def get_message_args(self, context: CommandContext):
        flavor = random.choice(list(Emoji.lacroix()))
        flavor_name = flavor.name.split('_')[0].capitalize()
        user = quote_user_id(context.event.user)
        return {
            'text': f'{user}: I recommend {flavor} {flavor_name} La Croix'
        }
