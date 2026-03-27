import os
import discord
from discord.ext import commands

from data import config

config.load_env()

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
guild = discord.Object(id=config.GUILD_ID)


async def load_cogs():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            extension = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                print(f"Loaded {extension}")
            except Exception as e:
                print(f"Failed to load {extension}: {e}")

async def sync():
    synced = await (bot.tree.sync(guild=guild))
    print(f"\nSynced {len(synced)} commands to guild {guild.id}")

    for command in synced:
        print(f"{command.name}")


@bot.event
async def on_ready():
    await load_cogs()
    print(f"\nLogged in as {bot.user} (ID: {bot.user.id})")

    await sync()


bot.run(config.BOT_TOKEN)