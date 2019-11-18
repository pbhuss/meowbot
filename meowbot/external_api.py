import requests

from meowbot.util import (
    get_redis,
    get_strava_client_id,
    get_strava_client_secret,
    get_config,
)


class StravaApi:
    def __init__(self):
        redis = get_redis()
        self._access_token = _get_strava_access_token(redis)

    @property
    def _headers(self):
        return {"Authorization": f"Bearer {self._access_token}"}

    def club_activities(self, club_id, page=None, per_page=None):
        return requests.get(
            f"https://www.strava.com/api/v3/clubs/{club_id}/activities",
            params={"page": page, "per_page": per_page},
            headers=self._headers,
        ).json()


def _get_strava_refresh_token(redis):
    key = "strava:refresh_token"
    refresh_token = redis.get(key)
    if refresh_token:
        refresh_token = refresh_token.decode("utf-8")
    else:
        refresh_token = get_config()["strava_refresh_token"]
        redis.set(key, refresh_token)
    return refresh_token


def _get_strava_access_token(redis):
    access_token_key = "strava:access_token"
    access_token = redis.get(access_token_key)
    if access_token:
        return access_token.decode("utf-8")
    else:
        response = requests.post(
            "https://www.strava.com/oauth/token",
            params={
                "client_id": get_strava_client_id(),
                "client_secret": get_strava_client_secret(),
                "grant_type": "refresh_token",
                "refresh_token": _get_strava_refresh_token(redis),
            },
        )
        data = response.json()
        redis.set(access_token_key, data["access_token"])
        redis.expireat(access_token_key, data["expires_at"] - 3600)
        redis.set("strava:refresh_token", data["refresh_token"])
        return data["access_token"]
