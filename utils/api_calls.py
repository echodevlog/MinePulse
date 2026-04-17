import aiohttp
from data import config


async def get_api_data():
    if config.server_name is None:
        return False

    minehut_api = f"https://api.minehut.com/server/{config.server_name}?byName=True"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=minehut_api) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                return None

        except Exception as e:
            print(f"Error fetching MineHut API: {e}")
            return None

async def valid_server_checker():
    data = await get_api_data()

    if data and data.get("server"):
        return True
    return False