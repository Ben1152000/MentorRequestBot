# MentorRequestBot

Discord bot for creating mentor requests for SB Hacks VIII.

## How to use

Clone the repository and create a `.env` file with the following contents:

    # .env
    DISCORD_TOKEN=<bot_token>
    DISCORD_GUILD=<guild_name>
  
Replace `<bot_token>` and `<guild_name>` with the bot token and name of the discord server, respectively. The bot token can be created on the discord developer portal.

To run, execute `python3 bot.py` in the shell, and it should print out a message like this:

    MentorRequestBot#0742 is connected to the following guild:
    SB Hacks VIII (id: 923781432336347186)
