from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime

from utils.data_manager import (update_data)
from utils.tools import start_loops
from utils.api_calls import valid_server_checker
from utils.discord_tools import dc_embed_for_setup

from data import config


class RoleDropdownStandAlone(discord.ui.View):
    def __init__(self, cog: commands.Cog, role_type : str):
        super().__init__(timeout=180)
        self.add_item(RoleDropdown(parent_view=cog, role_type=role_type))

class RoleDropdown(discord.ui.RoleSelect):
    def __init__(self, parent_view: "SetupView", role_type: str):
        super().__init__(placeholder="Search for role ...", min_values=1, max_values=1)
        self.parent_view = parent_view
        self.role_type = role_type

    async def callback(self, interaction: discord.Interaction):
        selected_role_id = self.values[0].id
        selected_role = interaction.guild.get_role(selected_role_id)

        match self.role_type:
            case "STAFF_ROLE":
                config.staff_role = selected_role
                update_data("roles", "staff_role_id", selected_role.id)
                if hasattr(self.parent_view, "create_page"):
                    self.parent_view.staff_role = selected_role
                else:
                    return await interaction.response.edit_message(content=f"✅ Your new staff role is set to `@{selected_role}`", view=None)

            case "ONLINE_ROLE":
                config.online_role = selected_role
                update_data("roles", "online_role_id", selected_role.id)
                if hasattr(self.parent_view, "create_page"):
                    self.parent_view.online_role = selected_role
                else:
                    return await interaction.response.edit_message(content=f"✅ Your new online role is set to `@{selected_role}`", view=None)

            case "VOTE_ROLE":
                config.vote_role = selected_role
                update_data("roles", "vote_role_id", selected_role.id)
                if hasattr(self.parent_view, "create_page"):
                    self.parent_view.vote_role = selected_role
                else:
                    return await interaction.response.edit_message(content=f"✅ Your new vote role is set to `@{selected_role}`", view=None)

        if hasattr(self.parent_view, "create_page"):
            await self.parent_view.continue_callback(interaction)

class ChannelDropdownStandAlone(discord.ui.View):
    def __init__(self, cog: commands.Cog):
        super().__init__(timeout=180)
        self.add_item(ChannelDropdown(parent_view=cog))

class ChannelDropdown(discord.ui.ChannelSelect):
    def __init__(self, parent_view: "SetupView"):
        super().__init__(placeholder="Search for notification channel ...", min_values=1, max_values=1, channel_types=[discord.ChannelType.text])
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        selected_channel_id = self.values[0].id
        selected_channel = interaction.guild.get_channel(selected_channel_id)

        config.notifications_channel = selected_channel
        update_data("text_channels", "notification_channel_id", selected_channel.id)

        if hasattr(self.parent_view, "create_page"):
            self.parent_view.notification_channel = selected_channel
            return await self.parent_view.continue_callback(interaction)
        else:
            return await interaction.response.edit_message(content=f"✅ Your new notification channel is set to `#{selected_channel}`", view=None)

class MineHutModal(discord.ui.Modal, title="Name of MineHut's server"):
    server_name = discord.ui.TextInput(
        label="What is your MineHut's server name?",
        placeholder="e. g. MyEpicMineHutServer",
        min_length=3,
        max_length=32,
        required=True
    )

    def __init__(self, parent_view: "SetupView"):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        if " " in self.server_name.value:
            return await interaction.response.send_message("❌ Error: MineHut server names cannot contain spaces. Please try again!", ephemeral=True)

        config.server_name = self.server_name.value

        if await valid_server_checker():
            if hasattr(self.parent_view, "server_name"):
                self.parent_view.server_name = self.server_name.value

            update_data("settings", "server_name", self.server_name.value)

            if hasattr(self.parent_view, "continue_callback"):
                await self.parent_view.continue_callback(interaction)
            else:
                await interaction.response.send_message(f"✅ Server name updated to: **{self.server_name.value}**", ephemeral=True)

        else:
            config.server_name = None
            return await interaction.response.send_message(f"❌ Error: I can't find provided server (by the name: **{self.server_name.value}**). Please provide valid MineHut server name!", ephemeral=True)

class FunctionsDropdown(discord.ui.Select):
    def __init__(self, parent_view: "SetupView"):
        self.parent_view = parent_view

        options = [
            discord.SelectOption(
                label="🌐 Online Notifications",
                value="online",
                description="I'll send a notification each time your MineHut server is online."),

            discord.SelectOption(
                label="🗳️ Vote Notifications",
                value="vote",
                description="I'll send daily notifications where you can vote for MineHut in order to get free credits."),
        ]
        super().__init__(placeholder="Select which bot functions do you want to use ...", min_values=1, max_values=2, options=options)

    async def callback(self, interaction: discord.Interaction):
        config.online_notification = False
        config.vote_notification = False

        if "online" in self.values:
            config.online_notification = True
            update_data("settings", "online_notifications", True)
        if "vote" in self.values:
            config.vote_notification = True
            update_data("settings", "vote_notifications", True)

        await self.parent_view.continue_callback(interaction)

class TimezoneDropdownStandalone(discord.ui.View):
    def __init__(self, cog: commands.Cog):
        super().__init__(timeout=180)
        self.add_item(TimezoneDropdown(parent_view=cog))

class TimezoneDropdown(discord.ui.Select):
    def __init__(self, parent_view: "SetupView"):
        self.parent_view = parent_view

        options = [
            # America
            discord.SelectOption(label="Eastern Time (NY / Toronto)", value="America/New_York"),
            discord.SelectOption(label="Central Time (Chicago / Mexico City)", value="America/Chicago"),
            discord.SelectOption(label="Mountain Time (Denver)", value="America/Denver"),
            discord.SelectOption(label="Pacific Time (LA / Vancouver)", value="America/Los_Angeles"),
            discord.SelectOption(label="Atlantic Time (Halifax)", value="America/Halifax"),

            # Europe & Africa
            discord.SelectOption(label="Western European (London / Lisbon)", value="Europe/London"),
            discord.SelectOption(label="Central European (Paris / Berlin / Ljubljana)", value="Europe/Paris"),
            discord.SelectOption(label="Eastern European (Athens / Cairo)", value="Europe/Athens"),
            discord.SelectOption(label="Moscow Time", value="Europe/Moscow"),

            # Asia
            discord.SelectOption(label="India Standard Time", value="Asia/Kolkata"),
            discord.SelectOption(label="Singapore / Hong Kong", value="Asia/Singapore"),
            discord.SelectOption(label="Japan / Korea Standard Time", value="Asia/Tokyo"),
            discord.SelectOption(label="Australian Eastern (Sydney)", value="Australia/Sydney"),
            discord.SelectOption(label="New Zealand (Auckland)", value="Pacific/Auckland"),

            # Universal
            discord.SelectOption(label="UTC / GMT", value="UTC"),
        ]

        super().__init__(placeholder="Select your server's timezone...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_timezone = self.values[0]
        config.timezone = ZoneInfo(selected_timezone)
        update_data("settings", "timezone", selected_timezone)

        for option in self.options:
            option.default = (option.value == selected_timezone)

        if hasattr(self.parent_view, "create_page"):
            self.parent_view.timezone = selected_timezone
            await interaction.response.edit_message(view=self.parent_view)
        else:
            await interaction.response.edit_message(content=f"✅ Timezone updated to **{selected_timezone}**", view=None)

class TimeModal(discord.ui.Modal, title="Timing for vote notifications"):
    vote_time = discord.ui.TextInput(
        label="Set timeing for daily vote notifications:",
        placeholder="e. g. 06:30 pm",
        min_length=7,
        max_length=8,
        required=True
    )

    def __init__(self, parent_view: "SetupView"):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        time_str = self.vote_time.value.strip().lower()

        try:
            converted_time = datetime.strptime(time_str, "%I:%M %p").time()
            config.vote_time = converted_time
            update_data("settings", "vote_time", str(converted_time))

            if hasattr(self.parent_view, "create_page"):
                self.parent_view.vote_time = converted_time
                self.parent_view.create_page()
                await interaction.response.edit_message(view=self.parent_view)
            else:
                await interaction.response.send_message(f"✅ Vote timing has been set to: `{converted_time}`", ephemeral=True)

        except ValueError:
            return await interaction.response.send_message("❌ **Invalid Format!** Please use the format `HH:MM am/pm` (e.g., `06:30 pm`).", ephemeral=True)

class SetupView(discord.ui.View):
    def __init__(self, cog: "DiscordCog"):
        super().__init__(timeout=None)
        self.cog = cog
        self.current_page : int = 0
        self.staff_role : discord.Role | None = None
        self.notification_channel : discord.TextChannel | None = None
        self.server_name : str | None = None
        self.online_role : discord.Role | None = None
        self.vote_role : discord.Role | None = None
        self.timezone : str | None = None
        self.vote_time : datetime | None = None
        self.create_page()

    def create_page(self):
        self.clear_items()

        # --- Social/Link Buttons ---
        if self.current_page == 0:
            self.add_item(discord.ui.Button(label="YouTube", style=discord.ButtonStyle.link, url="https://www.youtube.com/@EchoDevlog"))
            self.add_item(discord.ui.Button(label="Discord Server", style=discord.ButtonStyle.link, url="https://discord.gg/example"))

        # --- Step 1: Staff Role ---
        elif self.current_page == 1:
            self.add_item(RoleDropdown(parent_view=self, role_type="STAFF_ROLE"))

        # --- Step 2: Channel Selection ---
        elif self.current_page == 2:
            self.add_item(ChannelDropdown(parent_view=self))

        # --- Step 3: Server Name ---
        elif self.current_page == 3:
            modal_btn = discord.ui.Button(label="Press here to enter your server name", style=discord.ButtonStyle.red)
            modal_btn.callback = self.open_name_modal_callback
            self.add_item(modal_btn)

        # --- Step 4: Toggle Functions ---
        elif self.current_page == 4:
            self.add_item(FunctionsDropdown(parent_view=self))

        # --- Step 5: Online Role ---
        elif self.current_page == 5:
            self.add_item(RoleDropdown(parent_view=self, role_type="ONLINE_ROLE"))

        # --- Step 6: Vote Role ---
        elif self.current_page == 6 and config.vote_notification:
            self.add_item(RoleDropdown(parent_view=self, role_type="VOTE_ROLE"))

        # --- Step 7: Timezone & Timing ---
        elif self.current_page == 7 and config.vote_notification:
            self.add_item(TimezoneDropdown(parent_view=self))

            if self.vote_time:
                time_display = self.vote_time.strftime("%I:%M %p")
                button_label = f"Timing set to {time_display}"
                button_style = discord.ButtonStyle.green
            else:
                button_label = "Enter timing here"
                button_style = discord.ButtonStyle.red

            time_btn = discord.ui.Button(label=button_label, style=button_style, row=1)
            time_btn.callback = self.open_time_modal_callback
            self.add_item(time_btn)

        if self.current_page not in [1, 2, 3, 4, 5, 6]:
            next_embed = dc_embed_for_setup(self.current_page + 1)

            if next_embed:
                continue_btn = discord.ui.Button(label="Continue", style=discord.ButtonStyle.green, row=4)
                continue_btn.callback = self.continue_callback
                self.add_item(continue_btn)
            else:
                finish_btn = discord.ui.Button(label="Finish Setup", style=discord.ButtonStyle.blurple, row=4)
                finish_btn.callback = self.continue_callback
                self.add_item(finish_btn)

    async def continue_callback(self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer()
        self.current_page += 1

        if self.current_page == 5 and not config.online_notification:
            self.current_page += 1

        if self.current_page == 6 and not config.vote_notification:
            self.current_page += 2

        self.create_page()
        next_embed = dc_embed_for_setup(self.current_page)

        if next_embed:
            await interaction.edit_original_response(embed=next_embed, view=self)

        else:
            if config.vote_notification:
                if config.timezone is None:
                    return await  interaction.followup.send("Please select your timezone before finishing setup.", ephemeral=True)
                elif config.vote_time is None:
                    return await  interaction.followup.send("Please enter when you'd line to receive vote notifications via red button.", ephemeral=True)

            self.clear_items()

            online_str = f"{config.online_role.mention}" if config.online_role else f""
            vote_str = f"{config.vote_role.mention}" if config.vote_role else f""

            embed = discord.Embed(
                title="✅ Setup complete!",
                description=(
                    f"Staff: {config.staff_role.mention}"
                    f"\n\nServer: `{config.server_name}`"
                    f"\nOnline Notifications: `{config.online_notification}`, {online_str}"
                    f"\nVote Notifications: `{config.vote_notification}`, {vote_str}"
                    f"\n\nTimezone: `{config.timezone}`"
                    f"\nVote Timing: `{self.vote_time.strftime('%I:%M %p') if self.vote_time else 'N/A'}`"
                    f"\n\nThank you for choosing me!"),
                color=discord.Color.green()
            )
            self.add_item(discord.ui.Button(label="YouTube", style=discord.ButtonStyle.link, url="https://www.youtube.com/@EchoDevlog"))
            self.add_item(discord.ui.Button(label="Discord Server", style=discord.ButtonStyle.link, url="https://discord.gg/example"))

            await interaction.edit_original_response(embed=embed, view=self)
            config.setup_completed = True
            update_data("settings", "setup_completed", True)
            await start_loops()
            self.stop()

    async def open_name_modal_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MineHutModal(self))

    async def open_time_modal_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TimeModal(self))


class BotSetup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    stop = app_commands.Group(name="stop", description="Stop notifications", guild_ids=[config.GUILD_ID])
    start = app_commands.Group(name="start", description="Activate notifications", guild_ids=[config.GUILD_ID])
    change = app_commands.Group(name="change", description="Change settings", guild_ids=[config.GUILD_ID])
    server = app_commands.Group(name="server", description="Server related commands", guild_ids=[config.GUILD_ID], parent=change)
    vote = app_commands.Group(name="vote", description="Vote related commands", guild_ids=[config.GUILD_ID], parent=change)
    online = app_commands.Group(name="online", description="Online related commands", guild_ids=[config.GUILD_ID], parent=change)
    staff = app_commands.Group(name="staff", description="Staff related commands", guild_ids=[config.GUILD_ID], parent=change)
    notification = app_commands.Group(name="notification", description="Notification related commands", guild_ids=[config.GUILD_ID], parent=change)

    @app_commands.command(name="setup", description="Initial set up for the bot")
    @app_commands.guilds(config.GUILD_ID)
    async def dc_setup(self, interaction: discord.Interaction):
        if config.staff_role is not None:
            if config.staff_role not in interaction.user.roles:
                return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        if config.setup_completed:
            embed = discord.Embed(
                title="Setup was already completed",
                description=("`/setup` function can only be run once. It seems like you already did that. If you'd like to change any bot's settings you can do it by using commands below:"
                             "\n`/change notification channel`"
                             "\n`/stop online notifications`"
                             "\n`/stop vote notifications`"
                             "\n`/change server name`"
                             "\n`/change time zone`"
                             "\n`/change vote timing`"
                             "\n`/change vote role`"
                             "\n`/change online role`"),
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        view = SetupView(self)
        embed = dc_embed_for_setup(0)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @stop.command(name="online-notification", description="Stop notifying when MC server goes online.")
    async def stop_online_notification(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.staff_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
            return

        if not config.online_notification:
            await interaction.response.send_message("Online notification is already deactivated. Use `/start online-notification` if you want to activate it back.", ephemeral=True)
            return

        config.online_notification = False
        await interaction.response.send_message("Online notification is deactivated. Use `/start online-notification` if you want to activate it back.", ephemeral=True)

    @stop.command(name="vote-notification", description="Stop sending vote for MH notification.")
    async def stop_vote_notification(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.staff_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
            return

        if not config.vote_notification:
            await interaction.response.send_message("Vote notification is already deactivated. Use `/start vote-notification` if you want to activate it back.", ephemeral=True)
            return

        config.vote_notification = False
        await interaction.response.send_message("Vote notification is deactivated. Use `/start vote-notification` if you want to activate it back.", ephemeral=True)

    @start.command(name="online-notification", description="Activate vote for MH notification.")
    async def start_online_notification(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.staff_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
            return

        if config.online_notification:
            await interaction.response.send_message("Online notification is already active. Use `/stop online-notification` if you want to deactivate it.", ephemeral=True)
            return

        config.online_notification = True
        start_loops()
        await interaction.response.send_message("Online notification is active. Use `/stop online-notification` if you want to deactivate it.", ephemeral=True)

    @start.command(name="vote-notification", description="Activate vote for MH notification.")
    async def start_vote_notification(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.staff_role not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
            return

        if config.vote_notification:
            await interaction.response.send_message("Vote notification is already active. Use `/stop vote-notification` if you want to deactivate it.", ephemeral=True)
            return

        config.vote_notification = True
        start_loops()
        await interaction.response.send_message("Vote notification is active. Use `/stop vote-notification` if you want to deactivate it.", ephemeral=True)

    @server.command(name="name", description="Change server name setting")
    async def change_server_name(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.staff_role not in interaction.user.roles:
            return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        modal = MineHutModal(self)
        return await interaction.response.send_modal(modal)

    @vote.command(name="timezone", description="Change vote timezone setting")
    async def change_vote_timezone(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message( "It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.staff_role not in interaction.user.roles:
            return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        view = TimezoneDropdownStandalone(self)
        return await interaction.response.send_message(f"Please select your new timezone:", view=view, ephemeral=True)

    @vote.command(name="timing", description="Change vote timing setting")
    async def change_vote_timing(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.staff_role not in interaction.user.roles:
            return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        modal = TimeModal(self)
        return await interaction.response.send_modal(modal)

    @staff.command(name="role", description="Change staff role setting")
    async def change_staff_role(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.staff_role not in interaction.user.roles:
            return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        view = RoleDropdownStandAlone(self, "STAFF_ROLE")
        return await interaction.response.send_message(f"Please select your new staff role (**DISCLAIMER: Please note that all staff commands won't be available to be used from current staff role. Make sure you have a new role applied!**):", view=view, ephemeral=True)

    @online.command(name="role", description="Change online role setting")
    async def change_online_role(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.online_role not in interaction.user.roles:
            return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        view = RoleDropdownStandAlone(self, "ONLINE_ROLE")
        return await interaction.response.send_message(f"Please select your new online notification role:", view=view, ephemeral=True)

    @vote.command(name="role", description="Change vote role setting")
    async def change_vote_role(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.vote_role not in interaction.user.roles:
            return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        view = RoleDropdownStandAlone(self, "VOTE_ROLE")
        return await interaction.response.send_message(f"Please select your new vote notification role:", view=view, ephemeral=True)

    @notification.command(name="channel", description="Change notification channel setting")
    async def change_notification_channel(self, interaction: discord.Interaction):
        if not config.setup_completed:
            return await interaction.response.send_message("It seems like you haven't made initial setup for this bot. Please use `/setup` function", ephemeral=True)

        if config.vote_role not in interaction.user.roles:
            return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        view = ChannelDropdownStandAlone(self)
        return await interaction.response.send_message(f"please select your new notification channel:", view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(BotSetup(bot))