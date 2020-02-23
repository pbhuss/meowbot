from enum import Enum


class Emoji(Enum):
    def __str__(self):
        return f":{self.value}:"

    CAT = "cat"
    CATKOOL = "catkool"
    SMIRK_CAT = "smirk_cat"
    HEART_EYES_CAT = "heart_eyes_cat"
    SHOOKCAT = "shookcat"
    MONKACAT = "monkacat"
    POOP = "poop"
    HERB = "herb"
    YOUTUBE = "youtube"
    TWITCH = "twitch"
    IE = "ie"
    OTTER = "otter"
    JELLYFISH = "jellyfish"
    NASA = "nasa"
    GIRAFFE = "giraffe"
    BIRB = "birb"
    PING_PONG = "ping_pong"
    EIGHT_BALL = "8ball"
    LANNYPARROT = "lannyparrot"
    RED_X = "x"
    RED_O = "o"
    ARROWS_COUNTERCLOCKWISE = "arrows_counterclockwise"
    STRAVA = "strava"
    DATBOI2 = "datboi2"
    CHILIS = "chilis"
    UGH = "ugh"
    YUBIKEY = "yubikey"
    MEOW_SHOCKED = "meow_shocked"
    MEOWBLUSH = "meowblush"
    BLANK = "blank"
    DUMPSTER_FIRE = "dumpster-fire"

    ONE = "one"
    TWO = "two"
    THREE = "three"
    FOUR = "four"
    FIVE = "five"
    SIX = "six"
    SEVEN = "seven"
    EIGHT = "eight"
    NINE = "nine"

    SUNNY = "sunny"
    CRESCENT_MOON = "crescent_moon"
    RAIN_CLOUD = "rain_cloud"
    SNOW_CLOUD = "snow_cloud"
    WIND_BLOWING_FACE = "wind_blowing_face"
    FOG = "fog"
    CLOUD = "cloud"
    PARTLY_SUNNY = "partly_sunny"
    EARTH_AFRICA = "earth_africa"

    @classmethod
    def lacroix(cls):
        return frozenset(
            (
                cls.LIME_LACROIX,
                cls.TANGERINE_LACROIX,
                cls.PASSIONFRUIT_LACROIX,
                cls.APRICOT_LACROIX,
                cls.MANGO_LACROIX,
                cls.GRAPEFRUIT_LACROIX,
            )
        )

    LIME_LACROIX = "lime_lacroix"
    TANGERINE_LACROIX = "tangerine_lacroix"
    PASSIONFRUIT_LACROIX = "passionfruit_lacroix"
    APRICOT_LACROIX = "apricot_lacroix"
    MANGO_LACROIX = "mango_lacroix"
    GRAPEFRUIT_LACROIX = "grapefruit_lacroix"

    @classmethod
    def thinking(cls):
        return frozenset(
            (
                cls.THINKING_FACE,
                cls.MTHINKING,
                cls.THINK_NOSE,
                cls.BLOBTHINKINGEYES,
                cls.BLOBTHINKINGCOOL,
                cls.THINK_PIRATE,
                cls.BLOBTHINKINGGLARE,
                cls.THINKINGWITHBLOBS,
                cls.OVERTHINK,
                cls.THINKCASSO,
                cls.BLOBTHINKINGFAST,
                cls.THONK,
                cls.BLOBTHONKANG,
                cls.THONKING,
                cls.THINKENG,
                cls.BLOBHYPERTHINK,
                cls.BLOBTHINKINGSMIRK,
                cls.THINK_HAND,
                cls.THINK_FISH,
                cls.THINK_PENT,
                cls.THINKSYLVANIA,
                cls.THINKINGTHINKINGTHINKING,
                cls.THINK_YIN_YANG,
                cls.THINK_EYEBROWS,
                cls.THINKING_ROTATE,
                cls.BLOBHYPERTHINKFAST,
            )
        )

    THINKING_FACE = "thinking_face"
    MTHINKING = "mthinking"
    THINK_NOSE = "think_nose"
    BLOBTHINKINGEYES = "blobthinkingeyes"
    BLOBTHINKINGCOOL = "blobthinkingcool"
    THINK_PIRATE = "think_pirate"
    BLOBTHINKINGGLARE = "blobthinkingglare"
    THINKINGWITHBLOBS = "thinkingwithblobs"
    OVERTHINK = "overthink"
    THINKCASSO = "thinkcasso"
    BLOBTHINKINGFAST = "blobthinkingfast"
    THONK = "thonk"
    BLOBTHONKANG = "blobthonkang"
    THONKING = "thonking"
    THINKENG = "thinkeng"
    BLOBHYPERTHINK = "blobhyperthink"
    BLOBTHINKINGSMIRK = "blobthinkingsmirk"
    THINK_HAND = "think_hand"
    THINK_FISH = "think_fish"
    THINK_PENT = "think_pent"
    THINKSYLVANIA = "thinksylvania"
    THINKINGTHINKINGTHINKING = "thinkingthinkingthinking"
    THINK_YIN_YANG = "think_yin_yang"
    THINK_EYEBROWS = "think_eyebrows"
    THINKING_ROTATE = "thinking_rotate"
    BLOBHYPERTHINKFAST = "blobhyperthinkfast"

    LANNY_0_0 = "lanny_color_0_0"
    LANNY_0_1 = "lanny_color_0_1"
    LANNY_0_2 = "lanny_color_0_2"
    LANNY_0_3 = "lanny_color_0_3"
    LANNY_0_4 = "lanny_color_0_4"
    LANNY_1_0 = "lanny_color_1_0"
    LANNY_1_1 = "lanny_color_1_1"
    LANNY_1_2 = "lanny_color_1_2"
    LANNY_1_3 = "lanny_color_1_3"
    LANNY_1_4 = "lanny_color_1_4"
    LANNY_2_0 = "lanny_color_2_0"
    LANNY_2_1 = "lanny_color_2_1"
    LANNY_2_2 = "lanny_color_2_2"
    LANNY_2_3 = "lanny_color_2_3"
    LANNY_2_4 = "lanny_color_2_4"
    LANNY_3_0 = "lanny_color_3_0"
    LANNY_3_1 = "lanny_color_3_1"
    LANNY_3_2 = "lanny_color_3_2"
    LANNY_3_3 = "lanny_color_3_3"
    LANNY_3_4 = "lanny_color_3_4"
    LANNY_4_0 = "lanny_color_4_0"
    LANNY_4_1 = "lanny_color_4_1"
    LANNY_4_2 = "lanny_color_4_2"
    LANNY_4_3 = "lanny_color_4_3"
    LANNY_4_4 = "lanny_color_4_4"


magic_eight_ball_options = [
    "It is certain",
    "It is decidedly so",
    "Without a doubt",
    "Yes definitely",
    "You may rely on it",
    "You can count on it",
    "As I see it, yes",
    "Most likely",
    "Outlook good",
    "Yes",
    "Signs point to yes",
    "Absolutely",
    "Reply hazy try again",
    "Ask again later",
    "Better not tell you now",
    "Cannot predict now",
    "Concentrate and ask again",
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful",
    "Chances aren't good",
]


shakespeare_insult_start = [
    "artless",
    "bawdy",
    "beslubbering",
    "bootless",
    "churlish",
    "cockered",
    "clouted",
    "craven",
    "currish",
    "dankish",
    "dissembling",
    "droning",
    "errant",
    "fawning",
    "fobbing",
    "froward",
    "frothy",
    "gleeking",
    "goatish",
    "gorbellied",
    "impertinent",
    "infectious",
    "jarring",
    "loggerheaded",
    "lumpish",
    "mammering",
    "mangled",
    "mewling",
    "paunchy",
    "pribbling",
    "puking",
    "puny",
    "qualling",
    "rank",
    "reeky",
    "roguish",
    "ruttish",
    "saucy",
    "spleeny",
    "spongy",
    "surly",
    "tottering",
    "unmuzzled",
    "vain",
    "venomed",
    "villainous",
    "warped",
    "wayward",
    "weedy",
    "yeasty",
]


shakespeare_insult_middle = [
    "base-court",
    "bat-fowling",
    "beef-witted",
    "beetle-headed",
    "boil-brained",
    "clapper-clawed",
    "clay-brained",
    "common-kissing",
    "crook-pated",
    "dismal-dreaming",
    "dizzy-eyed",
    "doghearted",
    "dread-bolted",
    "earth-vexing",
    "elf-skinned",
    "fat-kidneyed",
    "fen-sucked",
    "flap-mouthed",
    "fly-bitten",
    "folly-fallen",
    "fool-born",
    "full-gorged",
    "guts-griping",
    "half-faced",
    "hasty-witted",
    "hedge-born",
    "hell-hated",
    "idle-headed",
    "ill-breeding",
    "ill-nurtured",
    "knotty-pated",
    "milk-livered",
    "motley-minded",
    "onion-eyed",
    "plume-plucked",
    "pottle-deep",
    "pox-marked",
    "reeling-ripe",
    "rough-hewn",
    "rude-growing",
    "rump-fed",
    "shard-borne",
    "sheep-biting",
    "spur-galled",
    "swag-bellied",
    "tardy-gaited",
    "tickle-brained",
    "toad-spotted",
    "unchin-snouted",
    "weather-bitten",
]


shakespeare_insult_end = [
    "apple-john",
    "baggage",
    "barnacle",
    "bladder",
    "boar-pig",
    "bugbear",
    "bum-bailey",
    "canker-blossom",
    "clack-dish",
    "clotpole",
    "coxcomb",
    "codpiece",
    "death-token",
    "dewberry",
    "flap-dragon",
    "flax-wench",
    "flirt-gill",
    "foot-licker",
    "fustilarian",
    "giglet",
    "gudgeon",
    "haggard",
    "harpy",
    "hedge-pig",
    "horn-beast",
    "hugger-mugger",
    "joithead",
    "lewdster",
    "lout",
    "maggot-pie",
    "malt-worm",
    "mammet",
    "measle",
    "minnow",
    "miscreant",
    "moldwarp",
    "mumble-news",
    "nut-hook",
    "pigeon-egg",
    "pignut",
    "puttock",
    "pumpion",
    "ratsbane",
    "scut",
    "skainsmate",
    "strumpet",
    "varlot",
    "vassal",
    "whey-face",
    "wagtail",
]
