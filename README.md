# meowbot

Simple [Slack](https://slack.com) chatbot that responds to predefined commands.

## Getting Started

### Prerequisites

You must have [docker](https://docs.docker.com/install/) and
[docker-compose](https://docs.docker.com/compose/install/) installed.

Meowbot is configured to use Nginx as a reverse-proxy with uWSGI.
* Instructions available at https://github.com/nginx-proxy/nginx-proxy
* Meowbot expects that this runs on a Docker network named `nginx-proxy`

You'll also need an existing Slack workspace to connect to meowbot. Create one
[here](https://slack.com/create).

### Installing

#### Slack Setup
Create a new Slack app at https://api.slack.com/app.
* Go to `Features → Event Subscriptions`
    * Enable events for `https://[your-server]:[port]/meow`
    * Meowbot uses port 1338 by default
    * Subscribe to the following Bot Events:
        * `message.channels` - A message was posted to a channel
        * `message.groups` - A message was posted to a private channel
        * `message.im` - A message was posted in a direct message channel
        * `message.mpim` - A message was posted in a multiparty direct message
        channel
        * `reaction_added` - A member has added an emoji reaction to an item
* Go to `Features → App Home`
    * Create a bot user with display name and username `meowbot`
* Go to `Features → OAuth & Permissions`
    * Add a Redirect URL for `https://[your-server]:[port]/authorize`
    * Under Scopes, add the scope `bot`
        * Note: this scope is deprecated. Instructions for granular permissions
        will be added soon
* Go to `Settings → Basic Information`
    * You'll need the Client ID, Client Secret, and Signing Secret for the next
    step

#### Configuration
Update [config.yaml](instance/config.yaml)
* Get `signing_secret`, `client_id` and `client_secret` from the Slack Setup
above
* Sign up for the free APIs listed and paste in your API keys
* Set your `default_zip_code`
    * This will be used for commands such as `weather` and `airquality` when no
    location is specified
* Set your `admin_username` and `admin_password`
    * Currently only used for viewing the
    [RQ Dashboard](https://github.com/eoranged/rq-dashboard)
* Set the `default_tv_channel`
    * Must be one of the keys in [channels.json](instance/channels.json)

Update [.env](.env)
* Change `MEOWBOT_HOST` to the hostname you would like to use for meowbot.

\[optional\] Update [channels.json](instance/channels.json)
* Add your favorite live YouTube streams or other videos
* Full-screen embedded players work best

### Docker

Start meowbot by running:
```bash
docker-compose up -d
```
Stop it by running:
```bash
docker-compose down
```

## Built With

* [Flask](http://flask.pocoo.org/) - Python web app framework
* [Redis](https://redis.io/) - In-memory data structure store
* [RQ (Redis Queue)](https://python-rq.org/) - Python task queue library
* [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) - WSGI server
* [Docker](https://docs.docker.com/) /
  [Docker Compose](https://docs.docker.com/compose/) - Multi-container platform

## APIs

* [TheCatAPI](https://thecatapi.com/) - Cats as a Service
* [Petfinder](https://www.petfinder.com/developers/) - Pet adoption database
* [Dark Sky](https://darksky.net/dev) - Weather conditions & forecasts
* [AirNow](https://docs.airnowapi.org/) - Air quality information
* [Nominatim](https://nominatim.openstreetmap.org/) - OpenStreetMap geocoder
* [Strava](https://developers.strava.com/) - Social fitness tracker

## Authors

* Peter Huss - [pbhuss](https://github.com/pbhuss)

See also the list of
[contributors](https://github.com/pbhuss/meowbot/contributors) who participated
in this project.

## License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md)
for details.
