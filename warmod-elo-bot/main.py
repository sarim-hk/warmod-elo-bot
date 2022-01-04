import parselogfiles
import compiledata
import queries

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
        key = f.readline()
        key = key.split(":")[0]
    return key

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@tasks.loop(seconds=10)
async def data_parser():
    gamestats = parselogfiles.run()
    if gamestats:
        compiledata.run(gamestats, c, conn)

if __name__ == "__main__":
    data_parser.start()
    bot.run(open_key())
