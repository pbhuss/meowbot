from meowbot.commands import command_registry, MissingCommand
from meowbot.context import CommandContext, InteractivePayload
from meowbot.util import (
    with_app_context
)


@with_app_context
def process_request(data):
    context = CommandContext(data)

    # Ignore messages from bots
    if getattr(context.event, 'subtype', None) in (
        'bot_message',
        'message_changed',
        'message_deleted'
    ):
        return

    if context.command is None:
        return

    command_obj = command_registry.get(context.command, MissingCommand)()
    command_obj.run(context)

    return command_obj


@with_app_context
def process_interactive(data):
    payload = InteractivePayload(data)

    for action in payload.actions:
        if action.command in command_registry:
            command_obj = command_registry[action.command]()
            command_obj.interact(payload, action)

    return
