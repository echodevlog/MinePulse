import os
import discord
from discord.ext import commands

from utils.discord_tools import set_bot_and_guild
from utils.data_manager import env_validation, create_data_file, read_data_file, create_log_file, add_log
from utils.tools import start_loops, get_current_datetime

from data import config


env_validation()
create_log_file() # new log file every new session

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
guild = discord.Object(id=config.GUILD_ID)

async def load_cogs():
    add_log("\n=== Loading Cogs ===")
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            extension = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                add_log(f"Loaded {extension}")
            except Exception as e:
                add_log(f"Failed to load {extension}: {e}")

async def sync():
    add_log("\n=== Syncing Slash Commands ===")
    synced = await (bot.tree.sync(guild=guild))
    add_log(f"Synced {len(synced)} commands to guild {guild.id}")

    for command in synced:
        add_log(f"{command.name}")

@bot.event
async def on_ready():
    set_bot_and_guild(bot)

    if os.path.exists(config.DATA_FILE):
        add_log("Data file detected. Extracting data!")
        if not await read_data_file():
            add_log("Data extraction failed! Trying again")
            await read_data_file()
    else:
        add_log("Data file not detected. Creating new one!")
        create_data_file()

    add_log(f"\nLogged in as {bot.user} (ID: {bot.user.id})")

    await load_cogs()
    await sync()

    if config.setup_completed:
        add_log("\n=== Starting all loops ===")
        await start_loops()

    config.bot_startup_time = get_current_datetime()


bot.run(config.BOT_TOKEN)