import io

import discord
from discord_slash import SlashCommand, SlashCommandOptionType, SlashContext
import logging

from discord_slash.utils.manage_commands import create_option, create_choice

import runicbabble.formats.mdj_image
import runicbabble.formats.mdj_emotes
from runicbabble.config import cfg

log = logging.getLogger(__name__)

intents = discord.Intents.default()

#
# Discord stuff
#
client = discord.Client(intents=intents)
slash = SlashCommand(client, sync_commands=True)  # Declares slash commands through the client.


@client.event
async def on_ready():
    log.info('Logged on as {0}!'.format(client.user))

    activity = discord.Activity(name='the whispers of the otherworld', type=discord.ActivityType.listening)
    await client.change_presence(activity=activity)

    await runicbabble.formats.mdj_emotes.init_emotes()


webhooks = {}


async def send_as_webhook(channel: discord.TextChannel, author: discord.User, **kwargs):
    """
    Attempts to send a message using webhooks. The bot can use this to send messages under a specified user's name,
    allowing selfbot-like capabilities.

    :param channel: the channel to send the message to
    :param author: the user under whose name to send the message
    :param kwargs: all parameters to be passed to the actual `send` method
    :return: True if the send succeeded, False otherwise
    """
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
        webhook: discord.Webhook = webhooks[channel.id]

        try:
            await webhook.send(username=author.display_name, avatar_url=author.avatar_url, **kwargs)
        except discord.NotFound:
            log.info(f'Previously known webhook for channel "{channel.name}" ({channel.id}) was deleated, recreating')
            webhooks[channel.id] = await channel.create_webhook(name=f'runicbabble-{channel.id}')
            await webhooks[channel.id].send(username=author.display_name, avatar_url=author.avatar_url, **kwargs)
        return True
    except discord.Forbidden:
        return False


@client.event
async def on_message(message: discord.Message):
    params = runicbabble.formats.mdj_emotes.render(message.content)
    if params is not None:
        await message.delete()
        if not await send_as_webhook(message.channel, message.author, **params):
            # if webhooks don't work, just send it yourself
            await message.channel.send(**params)

guild_ids = [854621868002377738, 761260439207936012, 751477559656710155]  # Put your server ID in this array.
if cfg.discord.sync_slash('False').lower() == 'true':
    guild_ids = None


@slash.slash(name="mdj",
             description="Render the entire message as Madouji",
             options=[
                 create_option(
                    name="content",
                    description="The message to be rendered",
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                 ),
                 create_option(
                     name="wrap",
                     description="What line wrapping model to use",
                     option_type=SlashCommandOptionType.STRING,
                     required=False,
                     choices=[
                         create_choice(name="none",  value="none"),
                         create_choice(name="flow",  value="flow"),
                         create_choice(name="force", value="force"),
                     ]
                 ),
                 create_option(
                    name="line-width",
                    description="max amount of characters in a line",
                    option_type=SlashCommandOptionType.INTEGER,
                    required=False
                 )
             ],
             guild_ids=guild_ids)
async def slash_mdj(ctx: SlashContext, content: str, wrap: str = 'none', line_width: int = 8):
    params = runicbabble.formats.mdj_image.render(content, 32, wrap, line_width)
    if await send_as_webhook(ctx.channel, ctx.author, **params):
        await ctx.send('\u200d', hidden=True)
    else:
        # if webhooks don't work, just send it yourself
        await ctx.send(**params)


@slash.slash(name="help", description="Get help with using the bot", guild_ids=guild_ids)
async def slash_help(ctx: SlashContext):
    await ctx.send("**Runic Babble** converts ASCII text into the constructed writing system Madouji, "
                   "created by the Cult of 74.\n\n"
                   "To learn more, visit the official server: https://discord.gg/mg4mCZGFq9", hidden=True)


def start():
    try:
        client.run(cfg.discord.bot_token())
    except KeyError:
        log.error('No bot token was specified; the Discord bot can not be started.')
