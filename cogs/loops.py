import discord
from discord.ext import commands, tasks

from data import config

class Loops(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_connections_cog = self.bot.get_cog("APIConnections")

    @tasks.loop(seconds=60)
    async def sever_online_loop(self):
        if self.api_connections_cog:
            data = self.api_connections_cog.get_api_data()

            if data:
                categories = data["server"]["categories"]
                motd = data["server"]["motd"].strip()
                server_plan = data["server"]["server_plan"]
                name = data["server"]["name"]
                creation = data["server"]["creation"]
                platform = data["server"]["platform"]
                port = data["server"]["port"]
                last_online = data["server"]["last_online"]
                expired = data["server"]["expired"]
                joins = data["server"]["joins"]
                daily_online_time = data["server"]["daily_online_time"]
                deleted = data["server"]["deleted"]
                hidden = data["server"]["hidden"]
                boosts = data["server"]["boosts"]
                online = data["server"]["online"]
                maxPlayers = data["server"]["maxPlayers"]
                playerCount = data["server"]["playerCount"]
                rawPlan = data["server"]["rawPlan"]

                if online:
                    embed = discord.Embed(
                        title=f"{name} is currently ONLINE!",
                        description="Let's play together",
                        color=discord.Color.green()
                    )
                    embed.set_footer(text=f"Current player count: {playerCount}")

                else:
                    embed = discord.Embed(
                        title=f"{name} is currently OFFLINE!",
                        description="Join the server to start it!",
                        color=discord.Color.green()
                    )

                if config.online_message is None:
                    config.online_message = await config.NOTIFICATIONS_CHANNEL.send(content=config.ONLINE_ROLE.mention, embed=embed)
                    config.update_data("messages", "online_message_id", config.online_message.id)
                else:
                    await config.online_message.edit(content=config.ONLINE_ROLE.mention, embed=embed)





    @tasks.loop(hours=24)
    async def vote_MH_loop(self):
        pass



async def setup(bot: commands.Bot):
    await bot.add_cog(Loops(bot))