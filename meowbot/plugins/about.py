from flask import url_for

from meowbot.conditions import IsCommand
from meowbot.context import CommandContext
from meowbot.triggers import SimpleResponseCommand


class Homepage(SimpleResponseCommand):
    condition = IsCommand(["homepage", "home"])
    help = "`homepage`: link to Meowbot homepage"

    def get_message_args(self, context: CommandContext):
        return {"text": url_for("main.index", _external=True)}


class GitHub(SimpleResponseCommand):
    condition = IsCommand(["github", "git", "source"])
    help = "`github`: GitHub page for Meowbot"

    def get_message_args(self, context: CommandContext):
        return {"text": "https://github.com/pbhuss/meowbot"}
