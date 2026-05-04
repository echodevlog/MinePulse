import re
from discord.ext import tasks
from datetime import datetime

from data import config


def time_conversion(milliseconds : int):
    total_seconds = milliseconds // 1000
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    return days, hours, minutes, seconds

def date_conversion(milliseconds : int):
    if not milliseconds or milliseconds == 0:
        return "Not yet"

    seconds = milliseconds / 1000
    date_object = datetime.fromtimestamp(seconds)
    readable_date = date_object.strftime("%d %b %Y - %H:%M")

    return readable_date

def get_current_datetime():
    current_datetime = datetime.now(config.timezone)
    return current_datetime

def clean_motd(motd : str):
    clean_text = re.sub(r"<[^>]+>", "", motd)

    if re.search(r'\n', clean_text):
        clean_text = f"```{clean_text}```"

    return clean_text

async def start_loops():
    from utils.data_manager import add_log

    loops_cog = config.bot.get_cog("Loops")

    if loops_cog:
        if config.online_notification:
            try:
                loops_cog.sever_online_loop.start()
                add_log("Online loop started.")
            except tasks.LoopAlreadyRunning as e:
                return

        if config.vote_notification:
            try:
                loops_cog.vote_MH_loop.start()
                add_log("Vote loop started.")
            except tasks.LoopAlreadyRunning as e:
                return
