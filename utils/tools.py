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

async def start_loops(bot):
    loops_cog = bot.get_cog("Loops")

    if loops_cog:
        if config.online_notification:
            loops_cog.sever_online_loop.start()
            print("Starting online loop")

        elif config.vote_notification:
            loops_cog.vote_MH_loop.start()
            print("Starting vote loop")

        else:
            print("No loops activated")
