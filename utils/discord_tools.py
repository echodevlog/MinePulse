import discord
from data import config
from data.config import bot, guild, notifications_channel


def dc_embed_for_setup(embed_page: int):
    if embed_page == 0:
        return discord.Embed(
            title=f"{config.BOT_NAME} Setup",
            description=(
                f"Thank you for using {config.BOT_NAME} bot!\n"
                "This is initial set up for the bot. Just follow instructions as you go.\n\n"
                "I was built by **Echodevlog**. Don't forget to follow his socials!\n\n"
                "When you're ready, press the button below 👇."
            ),
            color=discord.Color.orange())

    elif embed_page == 1:
        return discord.Embed(
            title="Step 1: Staff",
            description="Please select which role is your a staff role in the dropdown below:",
            color=discord.Color.orange())

    elif embed_page == 2:
        return discord.Embed(
            title="Step 2: Minecraft Server Updates",
            description="Please select a channel in which I can send notifications about your minecraft server.",
            color=discord.Color.orange())

    elif embed_page == 3:
        return discord.Embed(
            title="Step 3: Name of your MineHut server",
            description="Please enter your MineHut's server name:",
            color=discord.Color.orange())

    elif embed_page == 4:
        return discord.Embed(
            title="Step 4: Bot's functions",
            description="Please select which bot's functions do you want to use. You can select one or both functions.",
            color=discord.Color.orange())

    elif embed_page == 5:
        if config.online_notification:
            return discord.Embed(
                title="Step 5: MC server online notification role",
                description="Which role can bot ping each time your Minecraft server goes online?",
                color=discord.Color.orange()
            )

    elif config.vote_notification:
        if embed_page == 6:
            return discord.Embed(
                title="Step 6: Vote notification role",
                description="Which role can bot ping for vote notifications?",
                color=discord.Color.orange()
            )

        elif embed_page == 7:
            return discord.Embed(
                title="Step 7: Notification Timing",
                description=
                    ("1. Select your **Timezone**."
                    "\n2. Click the button to set your **preferred time**."
                    "\n3. Press `Finish` button. (If you don't see your selected options but you did select them don't panic. The options were saved."),
                color=discord.Color.orange())
        else:
            return None

    return None

async def discord_object_converter(data_id : int | None):
    output_obj = None
    if data_id is None:
        return output_obj

    if bot.get_channel(data_id):
        output_obj = bot.get_channel(data_id)

    elif guild.get_role(data_id) is not None:
        output_obj = guild.get_role(data_id)

    elif notifications_channel:
        try:
            output_obj = await notifications_channel.fetch_message(data_id)
        except discord.NotFound:
            pass

    return output_obj
