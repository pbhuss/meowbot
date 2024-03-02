import inspect
from abc import ABCMeta
from abc import abstractmethod

from meowbot.conditions import IsCommand
from meowbot.conditions import Never
from meowbot.context import CommandContext
from meowbot.context import InteractivePayload
from meowbot.context import SlackAction

trigger_registry = []


class BaseTrigger(metaclass=ABCMeta):
    @property
    @classmethod
    @abstractmethod
    def condition(cls):
        return NotImplemented

    @classmethod
    def __init_subclass__(cls, abstract: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)

        if not abstract:
            trigger_registry.append(cls)

    def activated(self, context):
        return self.condition.evaluate(context)

    @abstractmethod
    def run(self, context: CommandContext):
        pass


class BaseCommand(BaseTrigger, abstract=True, metaclass=ABCMeta):
    def get_help(self, context: CommandContext):
        if hasattr(self, "help"):
            return self.help
        return "no help available"


class SimpleResponseCommand(BaseCommand, abstract=True, metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.responses = []

    @abstractmethod
    def get_message_args(self, context: CommandContext):
        return NotImplemented

    def run(self, context: CommandContext):
        arg_gen = (
            self.get_message_args(context)
            if inspect.isgeneratorfunction(self.get_message_args)
            else (self.get_message_args(context),)
        )

        for arguments in arg_gen:
            arguments["channel"] = context.event.channel
            # Respond to thread if meowbot was mentioned in one
            if hasattr(context.event, "thread_ts"):
                arguments["thread_ts"] = context.event.thread_ts

            self.responses.append(context.api.chat_post_message(arguments))

        self.post_run(context)

    def post_run(self, context):
        for response in self.responses:
            if not response.ok:
                raise Exception(response._data)


class InteractiveCommand(BaseCommand, abstract=True, metaclass=ABCMeta):
    def is_action_relevant(self, action):
        if isinstance(self.condition, IsCommand):
            return action.command in self.condition._aliases
        return False

    @abstractmethod
    def interact(self, payload: InteractivePayload, action: SlackAction):
        return NotImplemented


class MissingCommand(SimpleResponseCommand):
    condition = Never()
    private = True

    def get_message_args(self, context: CommandContext):
        return {
            "text": f"Meow? (I don't understand `{context.command}`). "
            "Try `@meowbot help`."
        }


from meowbot.plugins import *  # noqa
