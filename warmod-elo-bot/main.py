import parselogfiles
import compiledata
import queries
import topelo

import discord
from discord.ext import commands
from discord.ext import tasks
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)
bot.remove_command("help")

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)

import sqlite3
conn = sqlite3.connect("elo.db")
c = conn.cursor()
queries.create_table(c, conn)

def open_key():
    with open("keys.txt", "r") as f:
        keys = f.readlines()
        discordkey = keys[0].split(":")[0]
        steamkey = keys[1].split(":")[0]
    return discordkey, steamkey

discordkey, steamkey = open_key()

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@tasks.loop(seconds=1)
async def data_parser():
    gamestats = parselogfiles.run(PATH=None)
    if gamestats:
        compiledata.run(gamestats, c, conn)

@bot.command()
async def top_elo(ctx):
    pages = topelo.run(steamkey, c)
    for page in pages:
        await ctx.message.channel.send(page)

if __name__ == "__main__":
    data_parser.start()
    bot.run(discordkey)
