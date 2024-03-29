import requests

from meowbot.conditions import IsCommand
from meowbot.context import CommandContext
from meowbot.triggers import SimpleResponseCommand


class Fact(SimpleResponseCommand):
    condition = IsCommand(["fact", "catfact", "catfacts", "facts"])
    help = "`fact`: get a cat fact"
    private = True

    def get_message_args(self, context: CommandContext):
        return {"text": requests.get("https://catfact.ninja/fact").json()["fact"]}
