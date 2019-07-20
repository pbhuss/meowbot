import random

from meowbot.commands import SimpleResponseCommand
from meowbot.constants import Emoji
from meowbot.context import CommandContext


class Shrug(SimpleResponseCommand):

    name = 'shrug'
    help = '`shrug`: shrug'
    private = True

    def get_message_args(self, context: CommandContext):
        return {
            'text': rf'¯\_{Emoji.CAT}_/¯'
        }


class Meow(SimpleResponseCommand):

    name = 'meow'
    help = '`meow`: meow!'

    def get_message_args(self, context: CommandContext):
        return {
            'text': f'Meow! {Emoji.CATKOOL}'
        }


class Poop(SimpleResponseCommand):

    name = 'poop'
    help = '`poop`: meowbot poops'
    private = True

    def get_message_args(self, context: CommandContext):
        return {
            'icon_emoji': f'{Emoji.SMIRK_CAT}',
            'text': f'{Emoji.POOP}'
        }


class No(SimpleResponseCommand):

    name = 'no'
    private = True
    help = '`no`: bad kitty!'
    aliases = ['bad', 'stop']

    def get_message_args(self, context: CommandContext):
        options = [
            'https://media.giphy.com/media/mYbsoApPfp0cg/giphy.gif',
            'https://media.giphy.com/media/dXO1Cy51pMrGU/giphy.gif',
            'https://media.giphy.com/media/ZXWZ6q1HYYpR6/giphy.gif',
            'https://media.giphy.com/media/kpMRmXUtsOeIg/giphy.gif',
            'https://media.giphy.com/media/xg0nPTCKIPJRe/giphy.gif',
        ]
        return {
            'blocks': [
                {
                    'type': 'image',
                    'image_url': random.choice(options),
                    'alt_text': 'dealwithit',
                }
            ]
        }


class Hmm(SimpleResponseCommand):

    name = 'hmm'
    help = '`hmm`: thinking...',
    aliases = ['think', 'thinking']

    def get_message_args(self, context: CommandContext):
        return {
            'text': str(random.choice(list(Emoji.thinking())))
        }


class Nyan(SimpleResponseCommand):

    name = 'nyan'
    help = '`nyan`: nyan'

    def get_message_args(self, context: CommandContext):
        return {
            'blocks': [
                {
                    'type': 'image',
                    'image_url': (
                        'https://media.giphy.com/media/sIIhZliB2McAo/giphy.gif'
                    ),
                    'alt_text': 'nyan cat',
                }
            ]
        }


class High5(SimpleResponseCommand):

    name = 'high5'
    help = '`high5`: give meowbot a high five',
    aliases = ['highfive']

    def get_message_args(self, context: CommandContext):
        return {
            'blocks': [
                {
                    'type': 'image',
                    'image_url': (
                        'https://media.giphy.com/media/'
                        '10ZEx0FoCU2XVm/giphy.gif'),
                    'alt_text': 'high five',
                }
            ]
        }


class Catnip(SimpleResponseCommand):

    name = 'catnip'
    help = '`catnip`: give meowbot some catnip'

    def get_message_args(self, context: CommandContext):
        return {
            'blocks': [
                {
                    'type': 'image',
                    'title': {
                        'type': 'plain_text',
                        'text': f'Oh no! You gave meowbot catnip {Emoji.HERB}',
                    },
                    'image_url': (
                        'https://media.giphy.com/media/DX6y0ENWjEGPe/giphy.gif'
                    ),
                    'alt_text': 'catnip',
                }
            ]
        }


class Dog(SimpleResponseCommand):

    name = 'dog'
    private = True

    def get_message_args(self, context: CommandContext):
        return {
            'text': 'no',
            'icon_emoji': f'{Emoji.MONKACAT}'
        }


class Lanny(SimpleResponseCommand):

    name = 'lanny'
    help = '`lanny`: LANNY! LANNY!'
    private = True

    def get_message_args(self, context: CommandContext):
        text = '\n'.join(
            (
                ''.join(
                    (
                        str(Emoji[f'LANNY_{r}_{c}'])
                        for c in range(5)
                    )
                )
                for r in range(5)
            )
        )

        return {
            'attachments': [
                {
                    'text': text
                }
            ],
            'icon_emoji': f'{Emoji.LANNYPARROT}',
            'username': 'Lannybot'
        }

class Sing(SimpleResponseCommand):

    name = 'sing'
    help = '`sing`: get meowbot to sing you a song'

    def get_message_args(self, context: CommandContext):
        return {
                'text': f'https://www.youtube.com/watch?v=4-L6rEm0rnY'
        }

class Movie(SimpleResponseCommand):
    name = 'movie'

    name = 'movie'
    help= '`movie`: get meowbot to show you a movie trailer'

    def get_message_args(self, context: CommandContext):
        return {
                'text': f'https://www.youtube.com/watch?v=FtSd844cI7U'
        }
