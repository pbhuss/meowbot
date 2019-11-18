from meowbot.triggers import BaseCommand
from meowbot.conditions import IsCommand
from meowbot.constants import Emoji
from meowbot.context import CommandContext


class Love(BaseCommand):

    condition = IsCommand(["love"])
    help = "`love [recipient] [message]`: send meowbot love"

    def run(self, context: CommandContext):
        if len(context.args) < 1:
            return

        user = context.args[0][2:-1]
        open_resp = context.api.im_open({"user": user})
        channel = open_resp.channel["id"]
        extra = ""
        if len(context.args) > 1:
            extra = f'\n>{" ".join(context.args[1:])}'

        context.api.chat_post_message(
            {
                "channel": channel,
                "text": f"{Emoji.HEART_EYES_CAT} Someone has sent you meowbot "
                f"love!{extra}",
            }
        )
        context.api.chat_post_ephemeral(
            {
                "channel": context.event.channel,
                "user": context.event.user,
                "text": "Your meowbot love has been sent",
            }
        )
