import time

import arrow

from meowbot.conditions import IsCommand
from meowbot.constants import Emoji
from meowbot.context import CommandContext
from meowbot.triggers import SimpleResponseCommand
from meowbot.util import get_redis
from meowbot.util import quote_user_id


class Poke(SimpleResponseCommand):
    condition = IsCommand(["poke"])
    help = "`poke`: poke meowbot"

    def get_message_args(self, context: CommandContext):
        team_id = context.team_id
        user_id = context.event.user
        ts = time.time()
        redis = get_redis()
        last_poke_time_key = f"poke:last:{team_id}"
        user_count_key = f"poke:user:{team_id}"
        last_poke_user_key = f"poke:lastuser:{team_id}"
        last_poke_time = redis.get(last_poke_time_key)
        redis.set(last_poke_time_key, ts)
        last_poked_user_id = redis.get(last_poke_user_key)
        if last_poked_user_id:
            last_poked_user_id = last_poked_user_id.decode("utf-8")
        redis.set(last_poke_user_key, user_id)
        total_pokes = redis.hincrby(user_count_key, user_id)

        if last_poke_time is None:
            return {
                "icon_emoji": f"{Emoji.SHOOKCAT}",
                "text": (
                    "You have poked meowbot 1 time!\n\n"
                    "You're the first to poke meowbot!"
                ),
            }

        s = "" if total_pokes == 1 else "s"
        last_poke = arrow.get(float(last_poke_time)).humanize()
        last_user = quote_user_id(last_poked_user_id)
        return {
            "icon_emoji": f"{Emoji.SHOOKCAT}",
            "text": f"You have poked meowbot {total_pokes} time{s}!\n\n"
            f"Meowbot was last poked {last_poke} by {last_user}",
        }
