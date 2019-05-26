import json
import random
import time
from datetime import timedelta
from typing import List, Callable, Optional

import arrow
import ics
import requests
import validators
from flask import url_for

import meowbot
from meowbot.models import Cat
from meowbot.util import (
    quote_user_id,
    get_cat_api_key,
    get_default_zip_code,
    get_petfinder_api_key,
    get_airnow_api_key,
    get_redis,
    get_darksky_api_key,
    get_location,
    get_channels,
    restore_default_tv_channel
)


class CommandList(object):

    commands = {}
    invisible_commands = {}
    help = {}

    @classmethod
    def register(
        cls,
        name: str,
        invisible: bool = False,
        help: Optional[str] = None,
        aliases: Optional[List[str]] = None
    ) -> Callable:
        def inner(func):
            if cls.has_command(name):
                return ValueError(f'Command {name} already registered')
            if invisible:
                cls.invisible_commands[name] = func
            else:
                cls.commands[name] = func
            if help:
                cls.help[name] = help
            if aliases:
                for alias in aliases:
                    cls.add_alias(name, alias)
            return func
        return inner

    @classmethod
    def get_command(cls, name: str) -> Optional[Callable]:
        return cls.commands.get(name, cls.invisible_commands.get(name, None))

    @classmethod
    def get_help(cls, name: str) -> Optional[str]:
        if not cls.has_command(name):
            return None
        return cls.help.get(name, '`{}`: no help available'.format(name))

    @classmethod
    def has_command(cls, name: str) -> bool:
        return name in cls.commands or name in cls.invisible_commands

    @classmethod
    def add_alias(cls, name: str, alias: str) -> None:
        if not cls.has_command(name):
            raise ValueError(f'Command {name} is not registered')
        if cls.has_command(alias):
            raise ValueError(f'Command {alias} already registered')
        cls.invisible_commands[alias] = cls.get_command(name)
        cls.help[alias] = '`{}` → {}'.format(
            alias,
            cls.get_help(name)
        )


@CommandList.register(
    'help',
    help='`help [command]`: shows all commands, or help for a particular '
         'command'
)
def help(context, *args):
    if args:
        name = args[0]
        if CommandList.has_command(name):
            text = CommandList.get_help(name)
        else:
            text = f'`{name}` is not a valid command'
        return {
            'text': text
        }
    else:
        commands = sorted(CommandList.commands.keys())
        attachment = {
            'pretext': 'Available commands are:',
            'fallback': ', '.join(commands),
            'fields': [
                {'value': CommandList.get_help(command)}
                for command in commands
            ],
            'footer': '<{}|meowbot {}> | For more help, join '
                      '#meowbot_control'.format(
                url_for('main.index', _external=True),
                meowbot.__version__
            ),
            'footer_icon': url_for(
                'static', filename='meowbot_thumb.jpg', _external=True)
        }
        return {
            'attachments': [attachment],
            'thread_ts': context['event']['ts']
        }


@CommandList.register(
    'shrug',
    invisible=True,
    help='`shrug`: shrug'
)
def shrug(context, *args):
    return {
        'text': r'¯\_:cat:_/¯'
    }


@CommandList.register(
    'ping',
    invisible=True,
    help='`ping`: see if meowbot is awake'
)
def ping(context, *args):
    return {
        'text': 'pong!'
    }


@CommandList.register(
    'meow',
    help='`meow`: meow!'
)
def meow(context, *args):
    return {
        'text': 'Meow! :catkool:'
    }


@CommandList.register(
    'lacroix',
    help='`lacroix`: meowbot recommends a flavor'
)
def lacroix(context, *args):
    choices = {
        'Lime': ':lime_lacroix:',
        'Tangerine': ':tangerine_lacroix:',
        'Passionfruit': ':passionfruit_lacroix:',
        'Apricot': ':apricot_lacroix:',
        'Mango': ':mango_lacroix:',
        'Pamplemousse': ':grapefruit_lacroix:'
    }
    flavor = random.choice(list(choices))
    user = quote_user_id(context['event']['user'])
    text = f'{user}: I recommend {choices[flavor]} {flavor} La Croix'
    return {
        'text': text,
    }


@CommandList.register(
    'cat',
    help='`cat [name] [number]`: gives one cat',
    aliases=['getcat']
)
def cat(context, *args):
    if len(args) in (1, 2):
        name = args[0]
        num_photos = Cat.query.filter_by(
            name=name.lower()
        ).count()
        if num_photos == 0:
            return {'text': 'No cats named {} registered'.format(name)}
        if len(args) == 2:
            number = args[1]
            if not number.isnumeric():
                return {
                    'text': f'Second argument must be a number. Got `{number}`'
                }
            number = int(number)
            if 1 <= number <= num_photos:
                offset = number - 1
            else:
                offset = random.randint(0, num_photos - 1)
        else:
            offset = random.randint(0, num_photos - 1)
        row = Cat.query.filter_by(
            name=name.lower()
        ).order_by(Cat.id).limit(1).offset(offset).one()
        return {
            'attachments': [
                {
                    'fallback': name,
                    'image_url': row.url,
                }
            ]
        }
    return {
        'attachments': [
            {
                'fallback': 'cat gif',
                'image_url': requests.head(
                    'https://api.thecatapi.com/v1/images/search?'
                    'format=src&mime_types=image/gif',
                    headers={'x-api-key': get_cat_api_key()}
                ).headers['Location']
            }
        ]
    }


@CommandList.register(
    'addcat',
    help='`addcat [name] [photo_url]`: add a cat to the database',
    aliases=['addacat', 'registercat']
)
def addcat(context, *args):
    if len(args) != 2:
        return {
            'text': f'Expected 2 args (name, url). Got {len(args)}',
            'thread_ts': context['event']['ts']
        }
    name, url = args
    # TODO: figure out why URLs are wrapped in <>.
    url = url[1:-1]
    if not validators.url(url):
        return {
            'text': '`{}` is not a valid URL'.format(url),
            'thread_ts': context['event']['ts']
        }
    row = Cat(name=name.lower(), url=url)
    meowbot.db.session.add(row)
    meowbot.db.session.commit()
    return {
        'attachments': [
            {
                'text': f'Registered {name}!',
                'image_url': url,
            }
        ],
        'thread_ts': context['event']['ts']
    }


@CommandList.register(
    'listcats',
    help='`listcats`: see all cats available for the `cat` command'
)
def listcats(context, *args):
    rows = meowbot.db.session.query(Cat.name).distinct()
    names = ', '.join((row.name for row in rows))
    return {'text': 'Cats in database: {}'.format(names)}


@CommandList.register(
    'removecat',
    help='`removecat [name] [number]`: delete a photo from the database'
)
def removecat(context, *args):
    if len(args) != 2:
        return {
            'text': f'Expected 2 args (name, number). Got {len(args)}'
        }
    name, number = args
    if not number.isnumeric():
        return {
            'text': f'Second argument must be a number. Got `{number}`'
        }
    offset = int(number)
    if offset <= 0:
        return {
            'text': f'Number must be > 0. Got `{offset}`'
        }
    row = Cat.query.filter_by(
        name=name.lower()
    ).order_by(
        Cat.id
    ).limit(1).offset(
        offset - 1
    ).one_or_none()
    if row is None:
        return {
            'text': 'No matching rows'
        }
    meowbot.db.session.delete(row)
    meowbot.db.session.commit()
    return {'text': 'Successfully removed!'}


@CommandList.register(
    'lanny',
    invisible=True,
    help='`lanny`: LANNY! LANNY!'
)
def lanny(context, *args):
    text = (
        ':lanny_color_0_0::lanny_color_0_1::lanny_color_0_2::lanny_color_0_3:'
        ':lanny_color_0_4:\n'
        ':lanny_color_1_0::lanny_color_1_1::lanny_color_1_2::lanny_color_1_3:'
        ':lanny_color_1_4:\n'
        ':lanny_color_2_0::lanny_color_2_1::lanny_color_2_2::lanny_color_2_3:'
        ':lanny_color_2_4:\n'
        ':lanny_color_3_0::lanny_color_3_1::lanny_color_3_2::lanny_color_3_3:'
        ':lanny_color_3_4:\n'
        ':lanny_color_4_0::lanny_color_4_1::lanny_color_4_2::lanny_color_4_3:'
        ':lanny_color_4_4:'
    )

    return {
        'attachments': [
            {
                'text': text
            }
        ]
    }


@CommandList.register(
    'poop',
    invisible=True,
    help='`poop`: meowbot poops'
)
def poop(context, *args):
    return {
        'text': ':smirk_cat::poop:'
    }


@CommandList.register(
    'no',
    invisible=True,
    help='`no`: bad kitty!',
    aliases=['bad', 'stop']
)
def no(context, *args):
    options = [
        'https://media.giphy.com/media/mYbsoApPfp0cg/giphy.gif',
        'https://media.giphy.com/media/dXO1Cy51pMrGU/giphy.gif',
        # too large 'https://media.giphy.com/media/MGCTZalz2doFq/giphy.gif',
        'https://media.giphy.com/media/ZXWZ6q1HYYpR6/giphy.gif',
        'https://media.giphy.com/media/kpMRmXUtsOeIg/giphy.gif',
        'https://media.giphy.com/media/xg0nPTCKIPJRe/giphy.gif',
    ]
    return {
        'attachments': [
            {
                'fallback': 'dealwithit',
                'image_url': random.choice(options)
            }
        ]
    }


@CommandList.register(
    'hmm',
    help='`hmm`: thinking...',
    aliases=['think', 'thinking']
)
def hmm(context, *args):
    options = [
        ':thinking_face:',
        ':mthinking:',
        ':think_nose:',
        ':blobthinkingeyes:',
        ':blobthinkingcool:',
        ':think_pirate:',
        ':blobthinkingglare:',
        ':thinkingwithblobs:',
        ':overthink:',
        ':thinkcasso:',
        ':blobthinkingfast:',
        ':thonk:',
        ':blobthonkang:',
        ':thonking:',
        ':thinkeng:',
        ':blobhyperthink:',
        ':blobthinkingsmirk:',
        ':think_hand:',
        ':think_fish:',
        ':think_pent:',
        ':thinksylvania:',
        ':thinkingthinkingthinking:',
        ':think_yin_yang:',
        ':think_eyebrows:',
        ':thinking_rotate:',
        ':blobhyperthinkfast:',
    ]
    return {
        'text': random.choice(options)
    }


@CommandList.register(
    'nyan',
    help='`nyan`: nyan'
)
def nyan(context, *args):
    return {
        'attachments': [
            {
                'fallback': 'nyan cat',
                'image_url': (
                    'https://media.giphy.com/media/sIIhZliB2McAo/giphy.gif')
            }
        ]
    }


@CommandList.register(
    'high5',
    help='`high5`: give meowbot a high five',
    aliases=['highfive']
)
def highfive(context, *args):
    return {
        'attachments': [
            {
                'fallback': 'high five',
                'image_url': (
                    'https://media.giphy.com/media/10ZEx0FoCU2XVm/giphy.gif')
            }
        ]
    }


@CommandList.register(
    'magic8',
    help='`magic8 [question]`: tells your fortune',
    aliases=['8ball']
)
def magic8(context, *args):
    options = [
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
        "Chances aren't good"
    ]
    text = '{} asked:\n>{}\n{}'.format(
        quote_user_id(context['event']['user']),
        ' '.join(args),
        random.choice(options)
    )
    return {
        'text': text
    }


@CommandList.register(
    'catnip',
    help='`catnip`: give meowbot some catnip',
)
def catnip(context, *args):
    return {
        'attachments': [
            {
                'fallback': 'catnip',
                'pretext': 'Oh no! You gave meowbot catnip :herb:',
                'image_url': (
                    'https://media.giphy.com/media/DX6y0ENWjEGPe/giphy.gif')
            }
        ]
    }


@CommandList.register(
    'fact',
    help='`fact`: get a cat fact',
    invisible=False,
    aliases=['catfact', 'catfacts', 'facts']
)
def fact(context, *args):
    return {
        'text': requests.get('https://catfact.ninja/fact').json()['fact']
    }


@CommandList.register(
    'concerts',
    help='`concerts`: upcoming concerts at Yerba Buena Gardens Festival',
    aliases=['concert']
)
def concerts(context, *args):
    redis = get_redis()
    key = 'concertcal'
    ical_data = redis.get(key)
    if ical_data is None:
        ical_data = requests.get(
            'https://ybgfestival.org/events/?ical=1&tribe_display=list'
        ).content
        redis.set(key, ical_data)
        # Expire at midnight PST
        redis.expireat(
            key,
            (arrow.utcnow().to('US/Pacific') + timedelta(days=1)).replace(
                hour=0, minute=0).timestamp
        )

    cal = ics.Calendar(ical_data.decode('utf-8'))
    events = cal.timeline.start_after(arrow.utcnow() - timedelta(hours=3))
    colors = ['#7aff33', '#33a2ff']
    return {
        'text': 'Upcoming concerts at <https://ybgfestival.org/|Yerba Buena '
                'Gardens Festival>:',
        'attachments': [
            {
                'title': event.name,
                'title_link': event.url,
                'text': event.description,
                'color': color,
                'fields': [
                    {
                        'title': 'When',
                        'value': '{} - {}'.format(
                            event.begin.strftime('%a %b %d, %I:%M'),
                            event.end.strftime('%I:%M %p')
                        ),
                        'short': False
                    },
                ]
            }
            for event, color in zip(events, colors)
        ]
    }


@CommandList.register(
    'weather',
    help='`weather [location]`: get weather forecast',
    aliases=['forecast']
)
def weather(context, *args):
    if len(args) >= 1:
        query = ' '.join(args)
    else:
        query = get_default_zip_code()

    key = f'weather:{query}'
    redis = get_redis()
    data = redis.get(key)
    location = get_location(query)
    if location is None:
        return {'text': 'Location `{}` not found'.format(query)}

    icon_map = {
        'clear-day': '☀️',
        'clear-night': '🌙',
        'rain': '🌧',
        'snow': '🌨',
        'sleet': '🌧',
        'wind': '💨',
        'fog': '🌫',
        'cloudy': '☁️',
        'partly-cloudy-day': '⛅',
        'partly-cloudy-night': '⛅',
    }
    icon_default = '🌎'

    color_map = {
        'clear-day': '#ffde5b',
        'clear-night': '#2d2d2d',
        'rain': '#5badff',
        'snow': '#d6e0ff',
        'sleet': '#5badff',
        'wind': '#9ee1ff',
        'fog': '#9b9b9b',
        'cloudy': '#d6e0ff',
        'partly-cloudy-day': '#ffde5b',
        'partly-cloudy-night': '#2d2d2d',
    }
    color_default = '#5badff'

    if data is None:
        api_key = get_darksky_api_key()
        lat = location['lat']
        lon = location['lon']
        data = requests.get(
            f'https://api.darksky.net/forecast/{api_key}/{lat},{lon}',
            params={
                'exclude': 'minutely,alerts,flags',
                'lang': 'en'
            }
        ).content
        redis.set(key, data, ex=5*60)

    result = json.loads(data.decode('utf-8'))

    return {
        'text': '*Forecast for {}*'.format(location['display_name']),
        'attachments': [
            {
                'title': 'Current Weather',
                'text': '{summary}\n'
                        '{icon} {current_temperature}℉\n'.format(
                            summary=result['hourly']['summary'],
                            icon=icon_map.get(
                                result['currently']['icon'], icon_default),
                            current_temperature=int(
                                result['currently']['temperature']),
                        ),
                'color': color_map.get(
                    result['currently']['icon'], color_default)
            },
            {
                'title': 'This Week',
                'fields': [
                    {
                        'title': arrow.get(day['time']).format('ddd'),
                        'value': '{icon} {high}℉ / {low}℉'.format(
                            icon=icon_map.get(day['icon'], icon_default),
                            high=int(day['temperatureHigh']),
                            low=int(day['temperatureLow'])
                        ),
                        'short': True
                    }
                    for day in result['daily']['data']
                ],
                'color': color_map.get(result['daily']['icon'], color_default),
                'footer': (
                    '<https://darksky.net/poweredby/|Powered by Dark Sky>'),
            }
        ]
    }


@CommandList.register(
    'airquality',
    help='`airquality [zipcode]`: get air quality information',
    aliases=['aqi', 'airnow', 'air']
)
def airquality(context, *args):

    if len(args) == 1:
        zip_code, = args
        if not zip_code.isnumeric():
            return {
                'text': f'Zip code must be a number. Got `{zip_code}`'
            }
    elif len(args) > 1:
        return {
            'text': 'Usage: `airquality [zipcode]`'
        }
    else:
        zip_code = get_default_zip_code()

    redis = get_redis()

    key = 'aqi:{}'.format(zip_code)
    data = redis.get(key)
    if data is None:
        airnow_api_key = get_airnow_api_key()
        observation_url = (
            'http://www.airnowapi.org/aq/observation/zipCode/current/')
        data = requests.get(
            observation_url,
            params={
                'API_KEY': airnow_api_key,
                'distance': 25,
                'zipCode': zip_code,
                'format': 'application/json'
            }
        ).content
        redis.set(key, data, ex=10*60)

    observations = json.loads(data.decode('utf-8'))

    # https://docs.airnowapi.org/aq101
    category_color_map = {
        1: '#00e400',  # Good - Green
        2: '#ffff00',  # Moderate - Yellow
        3: '#ff7e00',  # USG - Orange
        4: '#ff0000',  # Unhealthy - Red
        5: '#99004c',  # Very Unhealthy - Purple
        6: '#7e0023',  # Hazardous - Maroon
        7: '#000000',  # Unavailable - Black
    }

    parameter_map = {
        'PM2.5': 'fine particulate matter',
        'PM10': 'particulate matter',
        'O3': 'ozone'
    }

    if len(observations) == 0:
        return {'text': f'No data available for `{zip_code}`'}

    return {
        "text": "Air Quality for {}, {}:".format(
            observations[0]['ReportingArea'],
            observations[0]['StateCode']
        ),
        "attachments": [
            {
                "title": "{} ({})".format(
                    observation['ParameterName'],
                    parameter_map[observation['ParameterName']],
                ),
                "fallback": "{}\n{} - {}".format(
                    observation['ParameterName'],
                    observation['AQI'],
                    observation['Category']['Name']
                ),
                "color": category_color_map[
                    observation['Category']['Number']
                ],
                "text": "{} - {}".format(
                    observation['AQI'],
                    observation['Category']['Name']
                ),
                "footer": "Reported at {}{}:00 {}".format(
                    observation['DateObserved'],
                    observation['HourObserved'],
                    observation['LocalTimeZone']
                )
            }
            for observation in observations
        ]
    }


@CommandList.register(
    'poke',
    help='`poke`: poke meowbot'
)
def poke(context, *args):
    team_id = context['team_id']
    user_id = context['event']['user']
    ts = time.time()
    redis = get_redis()
    last_poke_time_key = f'poke:last:{team_id}'
    user_count_key = f'poke:user:{team_id}'
    last_poke_user_key = f'poke:lastuser:{team_id}'
    last_poke_time = redis.get(last_poke_time_key)
    redis.set(last_poke_time_key, ts)
    last_poked_user_id = redis.get(last_poke_user_key)
    if last_poked_user_id:
        last_poked_user_id = last_poked_user_id.decode('utf-8')
    redis.set(last_poke_user_key, user_id)
    total_pokes = redis.hincrby(user_count_key, user_id)

    if last_poke_time is None:
        return {
            'text': (
                f'You have poked meowbot {total_pokes} times! :shookcat:\n\n'
                'You\'re the first to poke meowbot!'
            )
        }

    s = '' if total_pokes == 1 else 's'
    last_poke = arrow.get(float(last_poke_time)).humanize()
    last_user = quote_user_id(last_poked_user_id)
    return {
        'text': f'You have poked meowbot {total_pokes} time{s}! :shookcat:\n\n'
                f'Meowbot was last poked {last_poke} by {last_user}'
    }


@CommandList.register(
    'homepage',
    help='`homepage`: link to Meowbot homepage',
    aliases=['home']
)
def homepage(context, *args):
    return {
        'text': url_for('main.index', _external=True)
    }


@CommandList.register(
    'github',
    help='`github`: GitHub page for Meowbot',
    aliases=['git', 'source'],
    invisible=True
)
def github(context, *args):
    return {
        'text': 'https://github.com/pbhuss/meowbot'
    }


@CommandList.register(
    'adoptcat',
    help='`adoptcat [zipcode]`: get cat adoption info',
)
def adoptcat(context, *args):
    if len(args) == 1:
        zip_code, = args
        if not zip_code.isnumeric():
            return {
                'text': 'Zip code must be a number. Got `{}`'.format(zip_code)
            }
    elif len(args) > 1:
        return {
            'text': 'Usage: `adoptcat [zipcode]`'
        }
    else:
        zip_code = get_default_zip_code()

    api_key = get_petfinder_api_key()
    petfinder_url = 'http://api.petfinder.com/pet.find'
    r = requests.get(
        petfinder_url,
        params={
                'key': api_key,
                'output': 'basic',
                'animal': 'cat',
                'count': '25',
                'location': zip_code,
                'format': 'json'
            }
    )
    data = r.json()

    def pet_info(pet):
        url = (
            'https://www.petfinder.com/cat/'
            '{short_name}-{pet_id}/state/city/shelter-{shelter_id}/'
        ).format(
            short_name=pet['name']['$t'].split(' ', 1)[0].lower(),
            pet_id=pet['id']['$t'],
            shelter_id=pet['shelterId']['$t']
        )
        photos = [
            photo['$t']
            for photo in pet.get(
                'media', {}).get('photos', {}).get('photo', [])
            if photo['@size'] == 'pn'
        ]
        name = pet['name']['$t']
        sex = pet['sex']['$t']
        age = pet['age']['$t']
        return {
            'basic_info': f'{name} sex: {sex} age: {age} {url}',
            'photo': None if len(photos) == 0 else photos[0]
        }

    pets = random.sample(
        [pet_info(pet) for pet in data['petfinder']['pets']['pet']],
        k=5
    )
    return {
        'attachments': [
            {'text': pet['basic_info'], 'image_url': pet['photo']}
            for pet in pets
        ],
        'thread_ts': context['event']['ts']
    }


@CommandList.register(
    'shakespeare',
    help='`shakespeare`: generates a Shakespearean insult'
)
def shakespeare(context, *args):
    first = [
        'artless', 'bawdy', 'beslubbering', 'bootless', 'churlish', 'cockered',
        'clouted', 'craven', 'currish', 'dankish', 'dissembling', 'droning',
        'errant', 'fawning', 'fobbing', 'froward', 'frothy', 'gleeking',
        'goatish', 'gorbellied', 'impertinent', 'infectious', 'jarring',
        'loggerheaded', 'lumpish', 'mammering', 'mangled', 'mewling',
        'paunchy', 'pribbling', 'puking', 'puny', 'qualling', 'rank', 'reeky',
        'roguish', 'ruttish', 'saucy', 'spleeny', 'spongy', 'surly',
        'tottering', 'unmuzzled', 'vain', 'venomed', 'villainous', 'warped',
        'wayward', 'weedy', 'yeasty'
    ]

    second = [
        'base-court', 'bat-fowling', 'beef-witted', 'beetle-headed',
        'boil-brained', 'clapper-clawed', 'clay-brained', 'common-kissing',
        'crook-pated', 'dismal-dreaming', 'dizzy-eyed', 'doghearted',
        'dread-bolted', 'earth-vexing', 'elf-skinned', 'fat-kidneyed',
        'fen-sucked', 'flap-mouthed', 'fly-bitten', 'folly-fallen',
        'fool-born', 'full-gorged', 'guts-griping', 'half-faced',
        'hasty-witted', 'hedge-born', 'hell-hated', 'idle-headed',
        'ill-breeding', 'ill-nurtured', 'knotty-pated', 'milk-livered',
        'motley-minded', 'onion-eyed', 'plume-plucked', 'pottle-deep',
        'pox-marked', 'reeling-ripe', 'rough-hewn', 'rude-growing', 'rump-fed',
        'shard-borne', 'sheep-biting', 'spur-galled', 'swag-bellied',
        'tardy-gaited', 'tickle-brained', 'toad-spotted', 'unchin-snouted',
        'weather-bitten'
    ]

    third = [
        'apple-john', 'baggage', 'barnacle', 'bladder', 'boar-pig', 'bugbear',
        'bum-bailey', 'canker-blossom', 'clack-dish', 'clotpole', 'coxcomb',
        'codpiece', 'death-token', 'dewberry', 'flap-dragon', 'flax-wench',
        'flirt-gill', 'foot-licker', 'fustilarian', 'giglet', 'gudgeon',
        'haggard', 'harpy', 'hedge-pig', 'horn-beast', 'hugger-mugger',
        'joithead', 'lewdster', 'lout', 'maggot-pie', 'malt-worm', 'mammet',
        'measle', 'minnow', 'miscreant', 'moldwarp', 'mumble-news', 'nut-hook',
        'pigeon-egg', 'pignut', 'puttock', 'pumpion', 'ratsbane', 'scut',
        'skainsmate', 'strumpet', 'varlot', 'vassal', 'whey-face', 'wagtail'
    ]

    return {
        'text': '{}Thou {} {} {}'.format(
            ' '.join(args) + ' ' if len(args) > 0 else '',
            random.choice(first),
            random.choice(second),
            random.choice(third)
        )
    }


@CommandList.register(
    'listchannels',
    help='`listchannels`: show available Meowbot TV channels',
    aliases=['channels', 'showchannels', 'tvguide'],
)
def listchannels(context, *args):
    channels = get_channels()
    channel_aliases = sorted(channels.keys())
    extra_channels = [
        {
            'title': 'youtube <video_id>',
            'value': ':youtube: Youtube video',
        },
        {
            'title': 'twitch <username>',
            'value': ':twitch: Twitch stream',
        },
        {
            'title': 'url <url>',
            'value': ':ie: Specified website',
        }
    ]
    attachment = {
        'pretext': 'Available channels:',
        'fallback': ', '.join(channel_aliases),
        'fields': [
            {
                'title': alias,
                'value': channels[alias]['name'],
            }
            for alias in channel_aliases
        ] + extra_channels
    }
    return {
        'attachments': [attachment],
        'thread_ts': context['event']['ts']
    }


@CommandList.register(
    'setchannel',
    help='`setchannel`: change Meowbot TV channel',
    aliases=['changechannel'],
)
def setchannel(context, *args):
    redis = get_redis()
    if redis.exists('killtv'):
        return {
            'text': (
                'Meowbot TV has been disabled. '
                'Contact Meowbot admin to reenable'
            )
        }

    channels = get_channels()
    available_channels = ', '.join(sorted(channels.keys()))
    if len(args) == 1:
        channel, = args
        if channel not in channels:
            return {
                'text': f'{channel} is not a valid channel.\n\n'
                        f'Available channels: {available_channels}',
                'thread_ts': context['event']['ts']
            }
        redis.set('tvchannel', channels[channel]['url'])
        return {
            'text': 'Changing channel to {}!'.format(
                channels[channel]['name']
            ),
        }
    elif len(args) == 2:
        channel_type, value = args
        if channel_type == 'url':
            url = value[1:-1]
            redis.set('tvchannel', url)
            return {
                'text': f'Changing channel to {url}!',
            }
        elif channel_type == 'twitch':
            url = f'https://player.twitch.tv/?channel={value}'
            redis.set('tvchannel', url)
            return {
                'text': f'Changing channel to :twitch: {value}!',
            }
        elif channel_type == 'youtube':
            url = (
                'https://www.youtube.com/embed/{video_id}?'
                'autoplay=1&loop=1&playlist={video_id}'
            ).format(video_id=value)
            redis.set('tvchannel', url)
            return {
                'text': f'Changing channel to :youtube: {value}!',
            }
    return {
        'text': 'Must provide a channel.\n\n'
                f'Available channels: {available_channels}',
        'thread_ts': context['event']['ts']
    }


@CommandList.register(
    'tv',
    help='`tv`: watch Meowbot TV',
    aliases=['television', 'meowtv', 'meowbottv'],
)
def tv(context, *args):
    return {
        'text': url_for('main.tv')
    }


@CommandList.register(
    'killtv',
    help='`killtv`: this kills Meowbot TV',
    aliases=['disabletv'],
    invisible=True
)
def killtv(context, *args):
    redis = get_redis()
    redis.set('killtv', '1')
    restore_default_tv_channel()
    return {
        'text': (
            'Meowbot TV has been disabled. Contact Meowbot admin to reenable'
        )
    }
