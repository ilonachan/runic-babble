import io

import discord
import logging
import runicbabble.lang
from runicbabble.config import cfg

log = logging.getLogger(__name__)

intents = discord.Intents.default()

#
# Discord stuff
#
client = discord.Client(intents=intents)


@client.event
async def on_message(message: discord.Message):
    img = runicbabble.lang.render(message.content)
    if img is not None:
        log.info(f'Received message "{message.content}"')
        await message.delete()
        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await message.channel.send(f'{message.author.mention}:',
                                       # does not work due to a bug on Discord Mobile
                                       # allowed_mentions=discord.AllowedMentions.none(),
                                       file=discord.File(fp=image_binary, filename='image.png'))


@client.event
async def on_ready():
    log.info('Logged on as {0}!'.format(client.user))

    activity = discord.Activity(name='the whispers of the otherworld', type=discord.ActivityType.listening)
    await client.change_presence(activity=activity)


def start():
    try:
        client.run(cfg.discord.bot_token())
    except KeyError:
        log.error('No bot token was specified; the Discord bot can not be started.')
