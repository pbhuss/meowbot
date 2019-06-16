import inspect
from abc import ABCMeta, abstractmethod
from typing import MutableMapping

from meowbot.context import CommandContext, InteractivePayload, SlackAction


class CommandRegistry(MutableMapping):

    def __init__(self):
        self._commands = {}

    def __getitem__(self, item):
        return self._commands[item]

    def __setitem__(self, key, value):
        if key in self:
            raise ValueError(f'Command {key} already registered')
        self._commands[key] = value

    def __delitem__(self, key):
        del self._commands[key]

    def __iter__(self):
        return iter(self._commands)

    def __len__(self):
        return len(self._commands)


command_registry = CommandRegistry()


class BaseCommand(metaclass=ABCMeta):

    @property
    @classmethod
    @abstractmethod
    def name(cls):
        return NotImplemented

    @classmethod
    def __init_subclass__(cls, abstract: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)

        if not abstract:
            command_registry[cls.name] = cls

            for alias in getattr(cls, 'aliases', []):
                command_registry[alias] = cls

    @abstractmethod
    def run(self, context: CommandContext):
        pass

    def get_help(self, context: CommandContext):
        if hasattr(self, 'help'):
            return self.help
        return f'`{self.name}`: no help available'


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
            arguments['channel'] = context.event.channel
            # Respond to thread if meowbot was mentioned in one
            if hasattr(context.event, 'thread_ts'):
                arguments['thread_ts'] = context.event.thread_ts

            self.responses.append(context.api.chat_post_message(arguments))

        self.post_run(context)

    def post_run(self, context):
        for response in self.responses:
            if not response.ok:
                raise Exception(response._data)


class InteractiveCommand(BaseCommand, abstract=True, metaclass=ABCMeta):

    @abstractmethod
    def interact(self, payload: InteractivePayload, action: SlackAction):
        return NotImplemented


class MissingCommand(SimpleResponseCommand):

    name = '__missing__'
    private = True

    def get_message_args(self, context: CommandContext):
        return {
            'text': f'Meow? (I don\'t understand `{context.command}`). '
                    'Try `@meowbot help`.'
        }


from meowbot.plugins import *   # noqa
