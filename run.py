import asyncio
import board
from discord.ext import commands
import config
import discord
import json
import os
import random
import sys

TOKEN = config.app_token
BOT_PREFIX = "!"
client = commands.Bot(command_prefix=commands.when_mentioned_or(BOT_PREFIX))


@client.event
async def on_ready():
    print ("Logged in as")
    print (client.user.name)
    print (client.user.id)
    print ("------")


@client.event
async def on_message(message):
    """Activates on any message sent."""
    if message.channel.name != "tanks-testing":
        return
    # This allows us to use other commands as well.
    await client.process_commands(message)


@client.command(pass_context=True)
async def loadtestdata(ctx, stuff=""):
    """Load testing data from S N A C C S group."""
    data = {"players": {}}
    pos_x = 0
    pos_y = 0

    with open("data/colors.json") as f:
        colors = json.load(f)

    color_list = []
    for color in colors:
        color_list.append(color)

    for role in ctx.message.server.roles:
        for member in ctx.message.server.members:
            if role.name == "s n a c c s" and role in member.roles:
                if not color_list:
                    break
                else:
                    data["players"][member.name] = {}
                    color = random.choice(color_list)
                    r = colors[color]["r"]
                    g = colors[color]["g"]
                    b = colors[color]["b"]
                data["players"][member.name]["color"] = {"name": color,
                                                         "r": r,
                                                         "g": g,
                                                         "b": b}
                color_list.remove(color)

                data["players"][member.name]["x"] = pos_x
                data["players"][member.name]["y"] = pos_y
                #data["players"][member.name]["avatar"] = member.avatar_url.replace("1024", "32")
                data["players"][member.name]["hp"] = random.randint(1, 3)
                data["players"][member.name]["points"] = random.randint(1, 14)

                if pos_x >= 11:
                    pos_x = 0
                    pos_y += 1
                else:
                    pos_x += 1

    with open("data/game.json", "w") as f:
        json.dump(data, f)


@client.command(pass_context=True)
async def nextturn(ctx, stuff=""):
    """Activate next turn."""
    board.create()
    with open("images/board.png", "rb") as f:
        await client.send_file(ctx.message.channel, f)


@client.command(pass_context=True)
async def scram(ctx, stuff=""):
    """Close the bot."""
    await client.say("Peace out, gramps.")
    await client.logout()


client.run(TOKEN)
