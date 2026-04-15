import os
import discord
from discord.ext import commands

from utils.data_manager import env_validation, create_data_file, read_data_file
from utils.tools import start_loops

from data import config


env_validation()

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

    if config.DATA_FILE[5:len(config.DATA_FILE)] not in os.listdir("data"):
        print("Data file not detected. Creating new one!")
        create_data_file()
    else:
        print("Data file detected. Extracting data!")
        await read_data_file()

    print(f"\nLogged in as {bot.user} (ID: {bot.user.id})")

    if config.setup_completed:
        print("Starting all loops")
        await start_loops()

    await sync()

bot.run(config.BOT_TOKEN)