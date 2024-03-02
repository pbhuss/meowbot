import random

from meowbot.conditions import IsCommand
from meowbot.constants import Emoji
from meowbot.constants import magic_eight_ball_options
from meowbot.context import CommandContext
from meowbot.triggers import SimpleResponseCommand
from meowbot.util import quote_user_id


class Magic8(SimpleResponseCommand):
    condition = IsCommand(["magic8", "8ball"])
    help = "`magic8 [question]`: tells your fortune"

    def get_message_args(self, context: CommandContext):
        text = "{} asked:\n>{}\n{}".format(
            quote_user_id(context.event.user),
            " ".join(context.args),
            random.choice(magic_eight_ball_options),
        )
        return {"text": text, "icon_emoji": f"{Emoji.EIGHT_BALL}"}
