import os
import discord
from discord.ext import commands

from utils.discord_tools import set_bot_and_guild
from utils.data_manager import env_validation, create_data_file, read_data_file, create_log_file, add_log
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
                add_log(f"Loaded {extension}")
            except Exception as e:
                add_log(f"Failed to load {extension}: {e}")

async def sync():
    add_log("\nSyncing slash commands ...")
    synced = await (bot.tree.sync(guild=guild))
    add_log(f"Synced {len(synced)} commands to guild {guild.id}")

    for command in synced:
        add_log(f"{command.name}")

@bot.event
async def on_ready():
    set_bot_and_guild(bot)

    if os.path.exists(config.DATA_FILE):
        print("Data file detected. Extracting data!")
        await read_data_file()
    else:
        print("Data file not detected. Creating new one!")
        create_data_file()

    create_log_file() # new log file every new session
    add_log(f"\nLogged in as {bot.user} (ID: {bot.user.id})")

    await load_cogs()

    if config.setup_completed:
        add_log("\nStarting all loops")
        await start_loops()

    await sync()

bot.run(config.BOT_TOKEN)