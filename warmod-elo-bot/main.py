import parselogfiles as plf
import logging
import discord

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@tasks.loop(seconds=10)
async def data_parser():
    gamestats = plf.run(PATH="C:/Users/Sarim/Desktop/")
    if not gamestats:
        return


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = commands.Bot(command_prefix="$", intents=intents)
    bot.remove_command("help")

    parse_gamestats.start()
