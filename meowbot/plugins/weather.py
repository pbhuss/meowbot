import json

import arrow
import requests

from meowbot.conditions import IsCommand
from meowbot.constants import Emoji
from meowbot.context import CommandContext
from meowbot.triggers import BaseCommand
from meowbot.triggers import InteractiveCommand
from meowbot.triggers import SimpleResponseCommand
from meowbot.util import get_darksky_api_key
from meowbot.util import get_default_zip_code
from meowbot.util import get_location
from meowbot.util import get_redis

USER_UNITS = "user_units"
USER_LOCATION = "user_location"
DEFAULT_UNITS = "us"


class Weather(SimpleResponseCommand, InteractiveCommand):
    condition = IsCommand(["weather", "forecast"])
    help = "`weather [location]`: get weather forecast"

    def get_message_args(self, context: CommandContext):
        redis = get_redis()
        if len(context.args) >= 1:
            query = " ".join(context.args)
        else:
            if redis.hexists(USER_LOCATION, context.event.user):
                query = redis.hget(USER_LOCATION, context.event.user).decode("utf-8")
            else:
                query = get_default_zip_code()
        if redis.hexists(USER_UNITS, context.event.user):
            units = redis.hget(USER_UNITS, context.event.user).decode("utf-8")
        else:
            units = DEFAULT_UNITS
        return self._weather_arguments(query, units=units)

    def interact(self, payload, action):
        units = action.action_name
        query = action.value
        arguments = self._weather_arguments(query, units)
        arguments["replace_original"] = True
        payload.api.interactive_response(payload, arguments)

    def _weather_arguments(self, query, units):
        key = f"weather:{units}:{query}"
        redis = get_redis()
        data = redis.get(key)
        location = get_location(query)
        if location is None:
            return {"text": f"Location `{query}` not found"}

        icon_map = {
            "clear-day": Emoji.SUNNY,
            "clear-night": Emoji.CRESCENT_MOON,
            "rain": Emoji.RAIN_CLOUD,
            "snow": Emoji.SNOW_CLOUD,
            "sleet": Emoji.RAIN_CLOUD,
            "wind": Emoji.WIND_BLOWING_FACE,
            "fog": Emoji.FOG,
            "cloudy": Emoji.CLOUD,
            "partly-cloudy-day": Emoji.PARTLY_SUNNY,
            "partly-cloudy-night": Emoji.PARTLY_SUNNY,
        }
        icon_default = Emoji.EARTH_AFRICA

        if data is None:
            api_key = get_darksky_api_key()
            lat = location["lat"]
            lon = location["lon"]
            data = requests.get(
                f"https://api.darksky.net/forecast/{api_key}/{lat},{lon}",
                params={
                    "exclude": "minutely,alerts,flags",
                    "lang": "en",
                    "units": units,
                },
            ).content
            redis.set(key, data, ex=5 * 60)

        result = json.loads(data.decode("utf-8"))

        temp_symbol = "℉" if units == "us" else "℃"
        other_symbol = "℃" if units == "us" else "℉"
        other_unit = "si" if units == "us" else "us"

        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f'*Forecast for {location["display_name"]}*',
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "action_id": f"weather:{units}",
                            "text": {
                                "type": "plain_text",
                                "text": (f"{Emoji.ARROWS_COUNTERCLOCKWISE} Refresh"),
                                "emoji": True,
                            },
                            "value": str(query),
                        },
                        {
                            "type": "button",
                            "action_id": f"weather:{other_unit}",
                            "text": {
                                "type": "plain_text",
                                "text": f"to {other_symbol}",
                            },
                            "value": str(query),
                        },
                    ],
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Current Weather*\n{summary}\n"
                        "{icon} {current_temperature}{temp_unit}\n".format(
                            summary=result["hourly"]["summary"],
                            icon=icon_map.get(
                                result["currently"]["icon"], icon_default
                            ),
                            current_temperature=int(result["currently"]["temperature"]),
                            temp_unit=temp_symbol,
                        ),
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*This Week*"},
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": (
                                "*{day}*\n{icon} {high}{temp_unit} / "
                                "{low}{temp_unit}".format(
                                    day=arrow.get(day["time"]).format("ddd"),
                                    icon=icon_map.get(day["icon"], icon_default),
                                    high=int(day["temperatureHigh"]),
                                    low=int(day["temperatureLow"]),
                                    temp_unit=temp_symbol,
                                )
                            ),
                        }
                        for day in result["daily"]["data"]
                    ],
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "<https://darksky.net/poweredby/|"
                            "Powered by Dark Sky>",
                        }
                    ],
                },
            ]
        }


class SetLocation(BaseCommand):
    condition = IsCommand(["setlocation"])
    help = "`setlocation [location]`: set your default location for `weather`"

    def run(self, context: CommandContext):
        location = " ".join(context.args)
        redis = get_redis()
        redis.hset("user_location", context.event.user, location)
        context.api.chat_post_ephemeral(
            {
                "channel": context.event.channel,
                "user": context.event.user,
                "text": f"Set default location to {location}",
            }
        )


class SetUnits(BaseCommand):
    condition = IsCommand(["setunits"])
    help = "`setunits [f|c]`: set your default units for `weather`"

    def run(self, context: CommandContext):
        if len(context.args) != 1:
            context.api.chat_post_ephemeral(
                {
                    "channel": context.event.channel,
                    "user": context.event.user,
                    "text": "Expected a single argument (f/c)",
                }
            )
            return
        (units,) = context.args
        units = units.lower()
        unit_map = {"fahrenheit": "us", "f": "us", "celsius": "si", "c": "si"}
        if units not in unit_map:
            context.api.chat_post_ephemeral(
                {
                    "channel": context.event.channel,
                    "user": context.event.user,
                    "text": f"Units must either be `f` or `c`. Got {units}",
                }
            )
            return
        redis = get_redis()
        redis.hset("user_units", context.event.user, unit_map[units])
        context.api.chat_post_ephemeral(
            {
                "channel": context.event.channel,
                "user": context.event.user,
                "text": f"Set default units to {units}",
            }
        )
