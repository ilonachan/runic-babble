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


webhooks = {}


async def send_runes(channel: discord.TextChannel, author: discord.User, img_file: discord.File):
    try:
        if channel.id not in webhooks:
            whs = await channel.webhooks()
            for wh in whs:
                wh: discord.Webhook
                if wh.name == f'runicbabble-{channel.id}':
                    log.info(f'Webhook for channel "{channel.name}" ({channel.id}) was found, reusing')
                    webhooks[channel.id] = wh
                    break
            else:
                log.info(f'No existing webhook for channel "{channel.name}" ({channel.id}) was found, creating one')
                webhooks[channel.id] = await channel.create_webhook(name=f'runicbabble-{channel.id}')
        webhook = webhooks[channel.id]

        try:
            await webhook.send(file=img_file, username=author.display_name, avatar_url=author.avatar_url)
        except discord.NotFound:
            log.info(f'Previously known webhook for channel "{channel.name}" ({channel.id}) was deleated, recreating')
            webhooks[channel.id] = await channel.create_webhook(name=f'runicbabble-{channel.id}')
            await webhooks[channel.id].send(file=img_file, username=author.display_name, avatar_url=author.avatar_url)
    except discord.Forbidden:
        await channel.send(f'{author.mention}:',
                           # does not work due to a bug on Discord Mobile
                           # allowed_mentions=discord.AllowedMentions.none(),
                           file=img_file)


@client.event
async def on_message(message: discord.Message):
    img = runicbabble.lang.render(message.content)
    if img is not None:
        log.info(f'Received message "{message.content}"')
        await message.delete()
        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await send_runes(message.channel, message.author, discord.File(fp=image_binary, filename='image.png'))


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
