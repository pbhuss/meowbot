from flask import url_for

import meowbot
from meowbot.commands import SimpleResponseCommand, command_registry
from meowbot.context import CommandContext


class Help(SimpleResponseCommand):

    name = 'help'
    help = '`help`: shows all commands, or help for a particular command'

    def get_message_args(self, context: CommandContext):
        if context.args:
            name = context.args[0].lower()
            if name in command_registry:
                text = command_registry[name]().get_help(context)
            else:
                text = f'`{name}` is not a valid command'
            return {
                'text': text
            }
        else:
            commands = sorted((
                name
                for name, command in command_registry.items()
                if name == command.name
                and not getattr(command, 'private', False)
            ))
            attachment = {
                'pretext': 'Available commands are:',
                'fallback': ', '.join(commands),
                'fields': [
                    {'value': command_registry[name]().get_help(context)}
                    for name in commands
                ],
                'footer': '<{}|meowbot {}> | For more help, join '
                          '#meowbot_control'.format(
                    url_for('main.index', _external=True),
                    meowbot.__version__
                ),
                'footer_icon': url_for(
                    'static', filename='meowbot_thumb.jpg', _external=True)
            }
            return {
                'attachments': [attachment],
                'thread_ts': context.event.ts
            }
