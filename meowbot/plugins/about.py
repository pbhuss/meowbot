from flask import url_for

from meowbot.commands import SimpleResponseCommand
from meowbot.context import CommandContext


class Homepage(SimpleResponseCommand):

    name = 'homepage'
    help = '`homepage`: link to Meowbot homepage'
    aliases = ['home']

    def get_message_args(self, context: CommandContext):
        return {
            'text': url_for('main.index', _external=True)
        }


class GitHub(SimpleResponseCommand):

    name = 'github'
    help = '`github`: GitHub page for Meowbot'
    aliases = ['git', 'source']

    def get_message_args(self, context: CommandContext):
        return {
            'text': 'https://github.com/pbhuss/meowbot'
        }
