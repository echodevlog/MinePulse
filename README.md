<div align="center">

# 🤖 MinePulse
**Discord bot for MineHut's Minecraft servers**

![Python](https://img.shields.io/badge/python-3.12+-blue.svg?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/echodevlog/MinePulse?color=blue)
![Last Commit](https://img.shields.io/github/last-commit/echodevlog/MinePulse?color=ff69b4)
![Repo Size](https://img.shields.io/github/repo-size/echodevlog/MinePulse)
![Issues](https://img.shields.io/github/issues/echodevlog/MinePulse?color=orange)

<br />
Get more info about this project bellow 


[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@EchoDevlog)

[Commands](COMMANDS.md) | [Setup Guide](#setup-guide) | [Report Bug](https://github.com/echodevlog/MinePulse/issues)

</div>

---

## About MinePulse
MinePulse is a dedicated Discord bot designed to track and notify you the moment your MineHut Minecraft server goes online. By utilizing MineHut's public API, it bypasses the "hibernation" status to provide real time updates, player counts, and voting reminders, helping you and your friends make the most of your server's daily uptime.

---

## Setup Guide


Before setting up MinePulse you should create the following channels and roles in your discord server (the names don't matter just remember them for later):

- `#notification-channel` a channel where you want MinePules to send messages in
- `@staff-role` (staff/admin role) if you don't have one yet. Anyone with this role will be able to change setting of MinePulse
- `@online-notification-role` MinePulse will ping this role each time your MineHut server goes online (if enabled)
- `@vote-notification-role` MinePulse will ping this role daily with a vote reminder for MineHut if you want free daily credits (if enabled)

Create your own instance of this bot (on [Discord developer portal](https://discord.com/developers/)). Then set up your own `.env` file. Follow the provided template in [example.env](example.env). You'll need to get your `BOT_TOKEN` and `GUILD_ID`.

Clone the repository using the following:
>```bash git clone https://github.com/echodevlog/MinePulse.git cd MinePulse```

Install requirements using:
>```pip install -r requirements.txt```


After that run the bot. `data.json` and `bot.log` will be created automatically.

When bot joins your Discord server you should use `/setup` command which will guide you through a simple setup. Just follow the instructions in the embedded message (sent by bot in your server).

If you'd like to change any configurations later use `/change` followed by setting you want to change.

___

## File Structure

```commandline
MinePulse/
├── .gitignore
├── README.md
├── COMMANDS.md
├── LICENSE.txt
├── requirements.txt            <-- The list of required libraries
├── app.py                      <-- Main project file
├── example.env                 <-- Copy and fill variables (BOT_TOKEN and GUILD_ID) than creat your own .env file
├── .env                        <-- File you should creat yourself
│                               
├── cogs/                       
│   ├── bot-setup.py            <-- Commands for bot's setup
│   ├── commands.py             <-- Slash commands for a user to use
│   ├── error-handler.py        <-- Khm ... error handler ...
│   └── loops.py                <-- Server online and vote reminder logic
│
├── data/
│   ├── bot.log                 <-- Yeah bot log ...
│   ├── config.py               <-- Try not to mess with it unless you know what you're doing
│   └── data.json               <-- Saved data for your Discord server
│
└── utils/
    ├── __init__.py
    ├── api_calls.py            <-- Connection logic to MineHut API
    ├── data_manager.py         <-- Logic related to saving data in to data.json and bot.log
    ├── discord_tools.py        <-- Discord object conversion & other Discord stuff
    ├── health.py               <-- Logic that checks if your MineHut server is healty and/or online
    └── tools.py                <-- Miscellaneous tools (mostly time conversion)
```

---

## Commands
List of all commands alongside their explanation is in the [COMMANDS.md](COMMANDS.md) file.