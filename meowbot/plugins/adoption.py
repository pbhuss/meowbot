import random

import requests

from meowbot.triggers import SimpleResponseCommand
from meowbot.conditions import IsCommand
from meowbot.context import CommandContext
from meowbot.util import get_default_zip_code, get_petfinder_api_key


class AdoptCat(SimpleResponseCommand):

    condition = IsCommand(["adoptcat"])
    help = "`adoptcat [zipcode]`: get cat adoption info"

    def get_message_args(self, context: CommandContext):
        if len(context.args) == 1:
            (zip_code,) = context.args
            if not zip_code.isnumeric():
                return {"text": f"Zip code must be a number. Got `{zip_code}`"}
        elif len(context.args) > 1:
            return {"text": "Usage: `adoptcat [zipcode]`"}
        else:
            zip_code = get_default_zip_code()

        api_key = get_petfinder_api_key()
        petfinder_url = "http://api.petfinder.com/pet.find"
        r = requests.get(
            petfinder_url,
            params={
                "key": api_key,
                "output": "basic",
                "animal": "cat",
                "count": "25",
                "location": zip_code,
                "format": "json",
            },
        )
        data = r.json()

        def pet_info(pet):
            url = (
                "https://www.petfinder.com/cat/"
                "{short_name}-{pet_id}/state/city/shelter-{shelter_id}/"
            ).format(
                short_name=pet["name"]["$t"].split(" ", 1)[0].lower(),
                pet_id=pet["id"]["$t"],
                shelter_id=pet["shelterId"]["$t"],
            )
            photos = [
                photo["$t"]
                for photo in pet.get("media", {}).get("photos", {}).get("photo", [])
                if photo["@size"] == "pn"
            ]
            name = pet["name"]["$t"]
            sex = pet["sex"]["$t"]
            age = pet["age"]["$t"]
            return {
                "basic_info": f"{name} sex: {sex} age: {age} {url}",
                "photo": None if len(photos) == 0 else photos[0],
            }

        pets = random.sample(
            [pet_info(pet) for pet in data["petfinder"]["pets"]["pet"]], k=5
        )
        return {
            "attachments": [
                {"text": pet["basic_info"], "image_url": pet["photo"]} for pet in pets
            ],
            "thread_ts": context.event.ts,
        }
