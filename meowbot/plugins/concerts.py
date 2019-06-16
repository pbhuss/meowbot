from datetime import timedelta

import arrow
import ics
import requests

from meowbot.commands import SimpleResponseCommand
from meowbot.context import CommandContext
from meowbot.util import get_redis


class Concerts(SimpleResponseCommand):

    name = 'concerts'
    help = '`concerts`: upcoming concerts at Yerba Buena Gardens Festival',
    aliases = ['concert']

    def get_message_args(self, context: CommandContext):
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
            'text': 'Upcoming concerts at <https://ybgfestival.org/|'
                    'Yerba Buena Gardens Festival>:',
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
