import requests

from meowbot.commands import SimpleResponseCommand
from meowbot.context import CommandContext


class Fact(SimpleResponseCommand):

    name = 'fact'
    help = '`fact`: get a cat fact'
    private = True
    aliases = ['catfact', 'catfacts', 'facts']

    def get_message_args(self, context: CommandContext):
        return {
            'text': requests.get('https://catfact.ninja/fact').json()['fact']
        }
