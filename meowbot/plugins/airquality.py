import json
import time

import requests
from geopy.distance import distance

from meowbot.conditions import IsCommand
from meowbot.context import CommandContext
from meowbot.triggers import SimpleResponseCommand
from meowbot.util import get_airnow_api_key
from meowbot.util import get_default_zip_code
from meowbot.util import get_location
from meowbot.util import get_redis


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


USER_LOCATION = "user_location"
PURPLEAIR_DATA_URL = "https://www.purpleair.com/json"
# https://docs.airnowapi.org/aq101
# https://www.airnow.gov/sites/default/files/2018-05/aqi-technical-assistance-document-may2016.pdf
BANDS = [
    {
        "pm25": (0.0, 12.0),
        "aqi": (0, 50),
        "color": "#00e400",  # Good - Green
        "name": "Good",
    },
    {
        "pm25": (12.1, 35.4),
        "aqi": (51, 100),
        "color": "#ffff00",  # Moderate - Yellow
        "name": "Moderate",
    },
    {
        "pm25": (35.5, 55.4),
        "aqi": (101, 150),
        "color": "#ff7e00",  # USG - Orange
        "name": "Unhealthy for Sensitive Groups",
    },
    {
        "pm25": (55.5, 150.4),
        "aqi": (151, 200),
        "color": "#ff0000",  # Unhealthy - Red,
        "name": "Unhealthy",
    },
    {
        "pm25": (150.5, 250.4),
        "aqi": (201, 300),
        "color": "#99004c",  # Very Unhealthy - Purple
        "name": "Very Unhealthy",
    },
    {
        "pm25": (250.5, 500.4),
        "aqi": (301, 500),
        "color": "#7e0023",  # Hazardous - Maroon,
        "name": "Hazardous",
    },
]


class PurpleAir(SimpleResponseCommand):
    condition = IsCommand(["purpleair", "purple"])
    help = "`purpleair [location]`: get PurpleAir air quality information"

    def get_message_args(self, context: CommandContext):
        redis = get_redis()
        if len(context.args) >= 1:
            query = " ".join(context.args)
        else:
            if redis.hexists(USER_LOCATION, context.event.user):
                query = redis.hget(USER_LOCATION, context.event.user).decode("utf-8")
            else:
                query = get_default_zip_code()

        location = get_location(query)
        if location is None:
            return {"text": f"Location `{query}` not found"}
        location_coords = (float(location["lat"]), float(location["lon"]))

        key = "purpleair"
        data = redis.get(key)
        if data is None:
            data = requests.get(PURPLEAIR_DATA_URL).content
            redis.set(key, data, ex=5 * 60)

        results = json.loads(data.decode("utf-8"))["results"]

        filtered_points = [
            point
            for point in results
            if (
                point.get("DEVICE_LOCATIONTYPE") == "outside"
                and "Lat" in point
                and "Lon" in point
                and point["AGE"] <= 30
            )
        ]
        child_points = {
            point["ParentID"]: point for point in results if "ParentID" in point
        }
        point_distances = (
            (point, distance((point["Lat"], point["Lon"]), location_coords))
            for point in filtered_points
        )
        point_distances = sorted(
            filter(lambda p_d: p_d[1].miles <= 25.0, point_distances),
            key=lambda p_d: p_d[1],
        )
        closest_points = point_distances[:3]
        if len(closest_points) == 0:
            return {
                "text": "No PurpleAir sensor within 25 miles of "
                f"{location['display_name']}"
            }

        def build_attachment(point, distance):
            pm25_10_min_avg = json.loads(point["Stats"])["v1"]
            flagged = "Flag" in point
            child_point = child_points.get(point["ID"])
            if child_point:
                pm25_10_min_avg = (
                    pm25_10_min_avg + json.loads(child_point["Stats"])["v1"]
                ) / 2
                flagged |= "Flag" in child_point

            for band in BANDS:
                lower_pm, upper_pm = band["pm25"]
                lower_aqi, upper_aqi = band["aqi"]
                color = band["color"]
                name = band["name"]
                if pm25_10_min_avg <= upper_pm:
                    # https://en.wikipedia.org/wiki/Air_quality_index#Computing_the_AQI
                    ten_min_aqi = (upper_aqi - lower_aqi) / (upper_pm - lower_pm) * (
                        pm25_10_min_avg - lower_pm
                    ) + lower_aqi
                    break

            return {
                "fallback": f"{ten_min_aqi} - {name}",
                "color": color,
                "text": f"{ten_min_aqi:.0f} - {name}",
                "footer": "{} | {:.1f} mi away | reported {:.0f} minutes ago".format(
                    point["Label"],
                    distance.miles,
                    (time.time() - point["LastSeen"]) / 60,
                ),
            }

        map_url = (
            "https://www.purpleair.com/map?opt=1/i/mAQI/a10/cC0#13.0/"
            f"{location_coords[0]}/{location_coords[1]}"
        )
        return {
            "text": f"PurpleAir sensors near <{map_url}|{location['display_name']}>:",
            "icon_emoji": ":purpleair:",
            "attachments": [
                build_attachment(point, distance) for point, distance in closest_points
            ],
        }
