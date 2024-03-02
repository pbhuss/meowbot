from meowbot.context import CommandContext
from meowbot.context import InteractivePayload
from meowbot.triggers import InteractiveCommand
from meowbot.triggers import trigger_registry
from meowbot.util import with_app_context


@with_app_context
def process_request(data):
    context = CommandContext(data)

    activated_triggers = []
    for trigger_cls in trigger_registry:
        trigger = trigger_cls()
        if trigger.activated(context):
            activated_triggers.append(trigger)

    for trigger in sorted(
        activated_triggers, key=lambda t: getattr(t, "priority", 0), reverse=True
    ):
        trigger.run(context)

    return activated_triggers


@with_app_context
def process_interactive(data):
    payload = InteractivePayload(data)

    for action in payload.actions:
        for trigger_cls in trigger_registry:
            if issubclass(trigger_cls, InteractiveCommand):
                trigger = trigger_cls()
                if trigger.is_action_relevant(action):
                    trigger.interact(payload, action)

    return
