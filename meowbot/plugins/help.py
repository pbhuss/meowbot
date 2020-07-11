from flask import url_for

import meowbot
from meowbot.triggers import SimpleResponseCommand, trigger_registry, BaseCommand
from meowbot.conditions import IsCommand
from meowbot.context import CommandContext


class Help(SimpleResponseCommand):

    condition = IsCommand(["help"])
    help = "`help`: shows all commands, or help for a particular command"

    def get_message_args(self, context: CommandContext):
        if context.args:
            name = context.args[0].lower()
            for trigger in trigger_registry:
                if (
                    issubclass(trigger, BaseCommand)
                    and not getattr(trigger, "private", False)
                    and (name in trigger.condition._aliases)
                ):
                    text = trigger().get_help(context)
                    return {"text": text}
            else:
                text = f"`{name}` is not a valid command"
                return {"text": text}

        else:
            commands = {
                trigger.condition._name: trigger
                for trigger in trigger_registry
                if issubclass(trigger, BaseCommand)
                and isinstance(trigger.condition, IsCommand)
                and not getattr(trigger, "private", False)
            }

            attachment = {
                "pretext": "Available commands are:",
                "fallback": ", ".join(sorted(commands)),
                "fields": [
                    {"value": commands[name]().get_help(context)}
                    for name in sorted(commands)
                ],
                "footer": "<{}|meowbot {}> | For more help, join "
                "#meowbot_control".format(
                    url_for("main.index", _external=True), meowbot.__version__
                ),
                "footer_icon": url_for(
                    "static", filename="meowbot_thumb.jpg", _external=True
                ),
            }
            return {"attachments": [attachment], "thread_ts": context.event.ts}
