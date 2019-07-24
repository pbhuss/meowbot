from flask import url_for

from meowbot.commands import SimpleResponseCommand
from meowbot.constants import Emoji
from meowbot.context import CommandContext
from meowbot.util import get_channels, get_redis, restore_default_tv_channel


class ListChannels(SimpleResponseCommand):

    name = 'listchannels'
    help = '`listchannels`: show available Meowbot TV channels'
    aliases = ['channels', 'showchannels', 'tvguide']

    def get_message_args(self, context: CommandContext):
        channels = get_channels()
        channel_aliases = sorted(channels.keys())
        extra_channels = [
            {
                'title': 'youtube <video_id>',
                'value': f'{Emoji.YOUTUBE} Youtube video',
            },
            {
                'title': 'twitch <username>',
                'value': f'{Emoji.TWITCH} Twitch stream',
            },
            {
                'title': 'url <url>',
                'value': f'{Emoji.IE} Specified website',
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
            'thread_ts': context.event.ts
        }


class SetChannel(SimpleResponseCommand):

    name = 'setchannel'
    help = '`setchannel`: change Meowbot TV channel'
    aliases = ['changechannel']

    def get_message_args(self, context: CommandContext):
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
        if len(context.args) == 1:
            channel, = context.args
            if channel not in channels:
                return {
                    'text': f'{channel} is not a valid channel.\n\n'
                            f'Available channels: {available_channels}',
                    'thread_ts': context.event.ts
                }
            redis.set('tvchannel', channels[channel]['url'])
            return {
                'text': f'Changing channel to {channels[channel]["name"]}!',
            }
        elif len(context.args) == 2:
            channel_type, value = context.args
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
                    'text': f'Changing channel to {Emoji.TWITCH} {value}!',
                }
            elif channel_type == 'youtube':
                url = (
                    f'https://www.youtube.com/embed/{value}?'
                    f'autoplay=1&loop=1&playlist={value}'
                )
                redis.set('tvchannel', url)
                return {
                    'text': f'Changing channel to {Emoji.YOUTUBE} {value}!',
                }
        return {
            'text': 'Must provide a channel.\n\n'
                    f'Available channels: {available_channels}',
            'thread_ts': context.event.ts
        }


class TV(SimpleResponseCommand):

    name = 'tv'
    help = '`tv`: watch Meowbot TV'
    aliases = ['television', 'meowtv', 'meowbottv']

    def get_message_args(self, context: CommandContext):
        return {
            'text': url_for('main.tv')
        }


class KillTV(SimpleResponseCommand):

    name = 'killtv'
    help = '`killtv`: this kills Meowbot TV'
    aliases = ['disabletv']
    private = True

    def get_message_args(self, context: CommandContext):
        redis = get_redis()
        redis.set('killtv', '1')
        restore_default_tv_channel()
        return {
            'text': (
                'Meowbot TV has been disabled. '
                'Contact Meowbot admin to reenable'
            )
        }
