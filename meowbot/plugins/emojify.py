import itertools
import random
import string

from meowbot.conditions import IsCommand
from meowbot.constants import Emoji
from meowbot.context import CommandContext
from meowbot.triggers import SimpleResponseCommand


class Emojify(SimpleResponseCommand):
    condition = IsCommand(["emojify", "emojifi"])
    help = "`emojify`: turn any text into emojis"

    def get_message_args(self, context: CommandContext):
        table = {
            32: ":blank:",
            48: ":zero:",
            49: ":one:",
            50: ":two:",
            51: ":three:",
            52: ":four:",
            53: ":five:",
            54: ":six:",
            55: ":seven:",
            56: ":eight:",
            57: ":nine:",
            97: ":a:",
            98: ":b:",
            99: ":color_c:",
            100: ":dailymotion:",
            101: ":edge:",
            102: ":f:",
            103: ":doogle:",
            104: ":h:",
            105: ":uiuc:",
            106: ":jchurch:",
            107: ":k:",
            108: ":l:",
            109: ":mcd:",
            110: ":njudah:",
            111: ":o:",
            112: ":parking:",
            113: ":quake:",
            114: ":registered:",
            115: ":gobears:",
            116: ":t:",
            117: ":u:",
            118: ":v:",
            119: ":wish:",
            120: ":x:",
            121: ":hn:",
            122: ":mana-z:",
        }
        return {"text": str.translate(" ".join(context.args).lower(), table)}


ALL_TEXT_COLORS = ("red", "yellow", "green", "teal", "blue", "purple")


def coloring(text, color_iterator):
    chars = list(text)
    for i, x in enumerate(chars):
        lower = x.lower()
        if x == " ":
            chars[i] = str(Emoji.BLANK)
        elif lower in string.ascii_lowercase:
            cur_color = next(color_iterator)
            chars[i] = f":letter-{lower}-{cur_color}:"
    return "".join(chars)


def random_color():
    cur_color = None
    while True:
        a, b = random.sample(ALL_TEXT_COLORS, 2)
        cur_color = a if a != cur_color else b
        yield cur_color


def christmas_color():
    if random.random() > 0.5:
        return itertools.cycle(("red", "green"))
    else:
        return itertools.cycle(("green", "red"))


class Color(SimpleResponseCommand):
    condition = IsCommand(["color", "colour"])
    help = "`color [text]`: add some color"

    def get_message_args(self, context: CommandContext):
        text = " ".join(context.args)

        return {"text": coloring(text, random_color())}


class Rainbow(SimpleResponseCommand):
    condition = IsCommand(["rainbow"])
    help = "`rainbow [text]`: make rainbow text"

    def get_message_args(self, context: CommandContext):
        text = " ".join(context.args)

        return {"text": coloring(text, itertools.cycle(ALL_TEXT_COLORS))}


class Christmas(SimpleResponseCommand):
    condition = IsCommand(["christmas"])
    help = "`christmas [text]`: make Christmas text"

    def get_message_args(self, context: CommandContext):
        text = " ".join(context.args)

        return {"text": coloring(text, christmas_color())}
