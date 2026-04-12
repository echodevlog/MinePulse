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
    config.set_bot(bot)
    await load_cogs()

    if config.data_file[5:len(config.data_file)] not in os.listdir("data"):
        print("Data file not detected. Creating new one!")
        config.create_data_file()
    else:
        print("Data file detected. Extracting data!")
        await config.read_data_file()

    print(f"\nLogged in as {bot.user} (ID: {bot.user.id})")

    if config.setup_completed:
        print("Starting all loops")
        await config.start_loops()

    await sync()

bot.run(config.BOT_TOKEN)