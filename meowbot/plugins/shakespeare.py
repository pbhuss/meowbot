import random

from meowbot.conditions import IsCommand
from meowbot.constants import shakespeare_insult_end
from meowbot.constants import shakespeare_insult_middle
from meowbot.constants import shakespeare_insult_start
from meowbot.context import CommandContext
from meowbot.triggers import SimpleResponseCommand


class Shakespeare(SimpleResponseCommand):
    condition = IsCommand(["shakespeare"])
    help = "`shakespeare`: generates a Shakespearean insult"

    def get_message_args(self, context: CommandContext):
        return {
            "text": "{}thou {} {} {}".format(
                " ".join(context.args) + " " if len(context.args) > 0 else "",
                random.choice(shakespeare_insult_start),
                random.choice(shakespeare_insult_middle),
                random.choice(shakespeare_insult_end),
            )
        }
