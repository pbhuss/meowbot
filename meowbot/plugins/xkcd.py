import datetime

import requests

from meowbot.conditions import IsCommand
from meowbot.context import CommandContext
from meowbot.triggers import SimpleResponseCommand


class XKCD(SimpleResponseCommand):
    condition = IsCommand(["xkcd"])
    help = "`xkcd [num]`: get today's xkcd, or a particular number"

    def get_message_args(self, context: CommandContext):
        if context.args:
            if len(context.args) != 1:
                return {"text": f"Usage: {self.get_help(context)}"}

            (num,) = context.args
            if not num.isnumeric():
                return {"text": f"Argument must be a number (got `{num}`)"}

            url = f"http://xkcd.com/{num}/info.0.json"
        else:
            url = "http://xkcd.com/info.0.json"

        resp = requests.get(url)
        if resp.status_code == 404:
            return {"text": "Comic not found"}
        data = resp.json()

        date = datetime.date(
            int(data["year"]), int(data["month"]), int(data["day"])
        ).strftime("%b %d, %Y")

        return {
            "blocks": [
                {
                    "type": "image",
                    "image_url": data["img"],
                    "title": {"type": "plain_text", "text": data["safe_title"]},
                    "alt_text": data["alt"],
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"#{data['num']}"},
                        {"type": "mrkdwn", "text": date},
                    ],
                },
            ]
        }
