import aiohttp
from data import config
from utils.data_manager import add_log

initial_log = True
successful_connection = False
previous_connection_error = None

async def get_api_data():
    global initial_log, successful_connection, previous_connection_error

    if config.server_name is None:
        return False

    if initial_log:
        add_log("\n=== MH API Connection Status ===")
        initial_log = False

    minehut_api = f"https://api.minehut.com/server/{config.server_name}?byName=True"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=minehut_api) as response:
                if response.status == 200:
                    if not successful_connection:
                        config.bot_state = "Connection to MH API succeeded!"
                        add_log(config.bot_state)
                        config.connections_succeeded_count += 1
                        successful_connection = True
                    data = await response.json()
                    return data
                return None

        except Exception as e:
            if successful_connection or e != previous_connection_error:
                config.bot_state = f"Error fetching MineHut API"
                add_log(f"Error fetching MineHut API: {e}")
                previous_connection_error = e
                config.connections_failed_count += 1
                successful_connection = False
            return None

async def valid_server_checker():
    data = await get_api_data()

    if data and data.get("server"):
        return True
    return False