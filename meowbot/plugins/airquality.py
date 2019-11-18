import json

import requests

from meowbot.triggers import SimpleResponseCommand
from meowbot.conditions import IsCommand
from meowbot.context import CommandContext
from meowbot.util import get_default_zip_code, get_redis, get_airnow_api_key


class AirQuality(SimpleResponseCommand):

    condition = IsCommand(["airquality", "aqi", "airnow", "air"])
    help = "`airquality [zipcode]`: get air quality information"

    def get_message_args(self, context: CommandContext):
        if len(context.args) == 1:
            (zip_code,) = context.args
            if not zip_code.isnumeric():
                return {"text": f"Zip code must be a number. Got `{zip_code}`"}
        elif len(context.args) > 1:
            return {"text": "Usage: `airquality [zipcode]`"}
        else:
            zip_code = get_default_zip_code()

        redis = get_redis()

        key = f"aqi:{zip_code}"
        data = redis.get(key)
        if data is None:
            airnow_api_key = get_airnow_api_key()
            observation_url = "http://www.airnowapi.org/aq/observation/zipCode/current/"
            data = requests.get(
                observation_url,
                params={
                    "API_KEY": airnow_api_key,
                    "distance": 25,
                    "zipCode": zip_code,
                    "format": "application/json",
                },
            ).content
            redis.set(key, data, ex=10 * 60)

        observations = json.loads(data.decode("utf-8"))

        # https://docs.airnowapi.org/aq101
        category_color_map = {
            1: "#00e400",  # Good - Green
            2: "#ffff00",  # Moderate - Yellow
            3: "#ff7e00",  # USG - Orange
            4: "#ff0000",  # Unhealthy - Red
            5: "#99004c",  # Very Unhealthy - Purple
            6: "#7e0023",  # Hazardous - Maroon
            7: "#000000",  # Unavailable - Black
        }

        parameter_map = {
            "PM2.5": "fine particulate matter",
            "PM10": "particulate matter",
            "O3": "ozone",
        }

        if len(observations) == 0:
            return {"text": f"No data available for `{zip_code}`"}

        return {
            "text": "Air Quality for {}, {}:".format(
                observations[0]["ReportingArea"], observations[0]["StateCode"]
            ),
            "attachments": [
                {
                    "title": "{} ({})".format(
                        observation["ParameterName"],
                        parameter_map[observation["ParameterName"]],
                    ),
                    "fallback": "{}\n{} - {}".format(
                        observation["ParameterName"],
                        observation["AQI"],
                        observation["Category"]["Name"],
                    ),
                    "color": category_color_map[observation["Category"]["Number"]],
                    "text": "{} - {}".format(
                        observation["AQI"], observation["Category"]["Name"]
                    ),
                    "footer": "Reported at {}{}:00 {}".format(
                        observation["DateObserved"],
                        observation["HourObserved"],
                        observation["LocalTimeZone"],
                    ),
                }
                for observation in observations
            ],
        }
