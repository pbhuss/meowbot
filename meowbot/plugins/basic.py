import random

from meowbot.triggers import SimpleResponseCommand
from meowbot.conditions import IsCommand
from meowbot.constants import Emoji
from meowbot.context import CommandContext


class Shrug(SimpleResponseCommand):

    condition = IsCommand(["shrug"])
    help = "`shrug`: shrug"
    private = True

    def get_message_args(self, context: CommandContext):
        return {"text": rf"¯\_{Emoji.CAT}_/¯"}


class Meow(SimpleResponseCommand):

    condition = IsCommand(["meow"])
    help = "`meow`: meow!"

    def get_message_args(self, context: CommandContext):
        return {"text": f"Meow! {Emoji.CATKOOL}"}


class Poop(SimpleResponseCommand):

    condition = IsCommand(["poop"])
    help = "`poop`: meowbot poops"
    private = True

    def get_message_args(self, context: CommandContext):
        return {"icon_emoji": f"{Emoji.SMIRK_CAT}", "text": f"{Emoji.POOP}"}


class No(SimpleResponseCommand):

    condition = IsCommand(["no", "bad", "stop"])
    private = True
    help = "`no`: bad kitty!"

    def get_message_args(self, context: CommandContext):
        options = [
            "https://media.giphy.com/media/mYbsoApPfp0cg/giphy.gif",
            "https://media.giphy.com/media/dXO1Cy51pMrGU/giphy.gif",
            "https://media.giphy.com/media/ZXWZ6q1HYYpR6/giphy.gif",
            "https://media.giphy.com/media/kpMRmXUtsOeIg/giphy.gif",
            "https://media.giphy.com/media/xg0nPTCKIPJRe/giphy.gif",
        ]
        return {
            "blocks": [
                {
                    "type": "image",
                    "image_url": random.choice(options),
                    "alt_text": "dealwithit",
                }
            ]
        }


class Hmm(SimpleResponseCommand):

    condition = IsCommand(["hmm", "think", "thinking"])
    help = ("`hmm`: thinking...",)

    def get_message_args(self, context: CommandContext):
        return {"text": str(random.choice(list(Emoji.thinking())))}


class Nyan(SimpleResponseCommand):

    condition = IsCommand(["nyan"])
    help = "`nyan`: nyan"

    def get_message_args(self, context: CommandContext):
        return {
            "blocks": [
                {
                    "type": "image",
                    "image_url": (
                        "https://media.giphy.com/media/sIIhZliB2McAo/giphy.gif"
                    ),
                    "alt_text": "nyan cat",
                }
            ]
        }


class High5(SimpleResponseCommand):

    condition = IsCommand(["high5", "highfive", "hi5"])
    help = ("`high5`: give meowbot a high five",)
    aliases = ["highfive"]

    def get_message_args(self, context: CommandContext):
        return {
            "blocks": [
                {
                    "type": "image",
                    "image_url": (
                        "https://media.giphy.com/media/10ZEx0FoCU2XVm/giphy.gif"
                    ),
                    "alt_text": "high five",
                }
            ]
        }


class Catnip(SimpleResponseCommand):

    condition = IsCommand(["catnip"])
    help = "`catnip`: give meowbot some catnip"

    def get_message_args(self, context: CommandContext):
        return {
            "blocks": [
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": f"Oh no! You gave meowbot catnip {Emoji.HERB}",
                    },
                    "image_url": (
                        "https://media.giphy.com/media/DX6y0ENWjEGPe/giphy.gif"
                    ),
                    "alt_text": "catnip",
                }
            ]
        }


class Dog(SimpleResponseCommand):

    condition = IsCommand(["dog"])
    private = True

    def get_message_args(self, context: CommandContext):
        return {"text": "no", "icon_emoji": f"{Emoji.MONKACAT}"}


class Lanny(SimpleResponseCommand):

    condition = IsCommand(["lanny"])
    help = "`lanny`: LANNY! LANNY!"
    private = True

    def get_message_args(self, context: CommandContext):
        text = "\n".join(
            (
                "".join((str(Emoji[f"LANNY_{r}_{c}"]) for c in range(5)))
                for r in range(5)
            )
        )

        return {
            "attachments": [{"text": text}],
            "icon_emoji": f"{Emoji.LANNYPARROT}",
            "username": "Lannybot",
        }
