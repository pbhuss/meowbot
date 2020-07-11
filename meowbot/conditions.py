import re
from abc import ABCMeta, abstractmethod

from meowbot.context import CommandContext


class Condition(metaclass=ABCMeta):
    @abstractmethod
    def evaluate(self, context: CommandContext):
        pass


class And(Condition):
    def __init__(self, *conditions):
        self._conditions = conditions

    def evaluate(self, context: CommandContext):
        return all(condition.evaluate(context) for condition in self._conditions)


class Or(Condition):
    def __init__(self, *conditions):
        self._conditions = conditions

    def evaluate(self, context: CommandContext):
        return any(condition.evaluate(context) for condition in self._conditions)


class Not(Condition):
    def __init__(self, condition):
        self._condition = condition

    def evaluate(self, context: CommandContext):
        return not self._condition.evaluate(context)


class Always(Condition):
    def evaluate(self, context: CommandContext):
        return True


class Never(Condition):
    def evaluate(self, context: CommandContext):
        return False


class IsCommand(Condition):
    def __init__(self, aliases):
        self._name = aliases[0]
        self._aliases = set(aliases)

    def evaluate(self, context: CommandContext):
        if context.event.subtype in (
            "bot_message",
            "message_changed",
            "message_deleted",
        ):
            return False
        if hasattr(context.event, "bot_id"):
            return False
        return context.command in self._aliases


class IsReaction(Condition):
    def __init__(self, reactions):
        self._reactions = set(reactions)

    def evaluate(self, context: CommandContext):
        return (
            context.event.type == "reaction_added"
            and context.event.reaction in self._reactions
        )


class InChannel(Condition):
    def __init__(self, channels):
        self._channels = set(channels)

    def evaluate(self, context: CommandContext):
        return context.event.channel in self._channels


class IsUser(Condition):
    def __init__(self, users):
        self._users = set(users)

    def evaluate(self, context: CommandContext):
        return context.event.user in self._users


class RegexMatch(Condition):
    def __init__(self, pattern, flags=0):
        self._regex = re.compile(pattern, flags=flags)

    def evaluate(self, context: CommandContext):
        if context.event.text is None:
            return False
        return self._regex.search(context.event.text)
