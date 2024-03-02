from pprint import pformat

from meowbot.conditions import And
from meowbot.conditions import IsCommand
from meowbot.conditions import IsUser
from meowbot.constants import Emoji
from meowbot.context import CommandContext
from meowbot.triggers import SimpleResponseCommand
from meowbot.util import get_admin_user_id
from meowbot.util import get_queue
from meowbot.util import get_redis


class Ping(SimpleResponseCommand):
    condition = IsCommand(["ping"])
    help = "`ping`: see if meowbot is awake"

    def get_message_args(self, context: CommandContext):
        return {"text": "pong!", "icon_emoji": f"{Emoji.PING_PONG}"}


class Debug(SimpleResponseCommand):
    private = True
    condition = And(IsCommand(["debug"]), IsUser([get_admin_user_id()]))

    def get_message_args(self, context: CommandContext):
        context._data["token"] = "REMOVED"
        return {"text": pformat(context._data)}


class Redis(SimpleResponseCommand):
    private = True
    condition = And(IsCommand(["redis"]), IsUser([get_admin_user_id()]))

    def get_message_args(self, context: CommandContext):
        if len(context.args) == 0:
            return {"text": "must specify at least one argument"}
        redis = get_redis()
        func_name, *func_args = context.args
        func = getattr(redis, func_name, None)
        if func is None:
            return {"text": f"invalid func_name: {func_name}"}
        arg_names = ", ".join(func_args)
        ret = func(*func_args)
        return {"text": f"Ran `{func_name}({arg_names})`\nReturned `{ret}`"}


class FailedQueue(SimpleResponseCommand):
    private = True
    condition = And(IsCommand(["failedqueue"]), IsUser([get_admin_user_id()]))

    def get_message_args(self, context: CommandContext):
        if len(context.args) == 0:
            yield {"text": "expected at least one argument"}
            return
        subcommand = context.args[0]
        queue = get_queue()
        failed_registry = queue.failed_job_registry
        task_count = failed_registry.count
        if subcommand == "size":
            yield {"text": f"Failed queue size: {task_count}"}
        elif subcommand == "empty":
            yield {"text": f"Removing {task_count} failed tasks"}
            job_ids = failed_registry.get_job_ids()
            for job_id in job_ids:
                failed_registry.remove(job_id)
            yield {"text": "Cleanup complete! :catkool:"}
        else:
            yield {"text": f"Unknown subcommand: {subcommand}"}


class Fail(SimpleResponseCommand):
    private = True
    condition = And(IsCommand(["fail"]), IsUser([get_admin_user_id()]))

    def get_message_args(self, context: CommandContext):
        raise Exception()
