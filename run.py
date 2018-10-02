import actions
import asyncio
import board
from discord.ext import commands
import config
import discord
import json
import os
import random
import sys

tanks_channel = "tanks-testing"
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
    if message.author == client.user:
        return
    # This allows us to use other commands as well.
    await client.process_commands(message)


@client.command(pass_context=True)
async def register(ctx, stuff=""):
    """Register for the game!"""
    if ctx.message.channel.name != "commands":
        return

    member = ctx.message.author
    for role in member.server.roles:
        if role.name == "Players":
            await client.add_roles(member, role)
            return


@client.command(pass_context=True)
async def generategame(ctx, stuff=""):
    """Generate the game info."""
    if ctx.message.author.name != "Muddy":
        return

    data = {"players": {}}
    pos_x = 2
    pos_y = 2

    with open("data/colors.json") as f:
        colors = json.load(f)

    color_list = []
    for color in colors:
        color_list.append(color)

    for role in ctx.message.server.roles:
        for member in ctx.message.server.members:
            if role.name == "Players" and role in member.roles:
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
                data["players"][member.name]["hp"] = 3
                data["players"][member.name]["points"] = 1

                if pos_x >= 11:
                    pos_x = 2
                    pos_y += 3
                else:
                    pos_x += 3

    with open("data/game.json", "w") as f:
        json.dump(data, f)

    board.create()

    for channel in ctx.message.server.channels:
        if channel.name == "gameboard":
            with open("images/board.png", "rb") as f:
                messages = []
                async for msg in client.logs_from(channel, limit=10):
                    await client.delete_message(msg)
                await client.send_file(channel, f)


@client.command(pass_context=True)
async def move(ctx, x="", y=""):
    """Queue action: !move up/down/left/right"""
    if ctx.message.channel.name != "commands":
        return

    response, changed = actions.action("move", x, y, ctx)
    await client.send_message(ctx.message.channel, response)

    if changed:
        board.create()
        for channel in ctx.message.server.channels:
            if channel.name == "gameboard":
                with open("images/board.png", "rb") as f:
                    messages = []
                    async for msg in client.logs_from(channel, limit=10):
                        await client.delete_message(msg)
                    await client.send_file(channel, f)


@client.command(pass_context=True)
async def shoot(ctx, x="", y=""):
    """Queue action: !shoot up/down/left/right"""
    if ctx.message.channel.name != "commands":
        return

    response, changed = actions.action("shoot", x, y, ctx)
    await client.send_message(ctx.message.channel, response)

    if changed:
        board.create()
        for channel in ctx.message.server.channels:
            if channel.name == "gameboard":
                with open("images/board.png", "rb") as f:
                    messages = []
                    async for msg in client.logs_from(channel, limit=10):
                        await client.delete_message(msg)
                    await client.send_file(channel, f)


@client.command(pass_context=True)
async def donate(ctx, x="", y=""):
    """Queue action: !donate up/down/left/right"""
    if ctx.message.channel.name != "commands":
        return

    response, changed = actions.action("donate", x, y, ctx)
    await client.send_message(ctx.message.channel, response)

    if changed:
        board.create()
        for channel in ctx.message.server.channels:
            if channel.name == "gameboard":
                with open("images/board.png", "rb") as f:
                    messages = []
                    async for msg in client.logs_from(channel, limit=10):
                        await client.delete_message(msg)
                    await client.send_file(channel, f)


# @client.command(pass_context=True)
# async def loadtestdata(ctx, stuff=""):
#     """Load testing data from S N A C C S group."""
#     if ctx.message.channel.name != tanks_channel:
#         return
#
#     data = {"players": {}}
#     pos_x = 2
#     pos_y = 2
#
#     with open("data/colors.json") as f:
#         colors = json.load(f)
#
#     color_list = []
#     for color in colors:
#         color_list.append(color)
#
#     for role in ctx.message.server.roles:
#         for member in ctx.message.server.members:
#             if role.name == "s n a c c s" and role in member.roles:
#                 if not color_list:
#                     break
#                 else:
#                     data["players"][member.name] = {}
#                     color = random.choice(color_list)
#                     r = colors[color]["r"]
#                     g = colors[color]["g"]
#                     b = colors[color]["b"]
#                 data["players"][member.name]["color"] = {"name": color,
#                                                          "r": r,
#                                                          "g": g,
#                                                          "b": b}
#                 color_list.remove(color)
#
#                 data["players"][member.name]["x"] = pos_x
#                 data["players"][member.name]["y"] = pos_y
#                 #data["players"][member.name]["avatar"] = member.avatar_url.replace("1024", "32")
#                 data["players"][member.name]["hp"] = random.randint(1, 3)
#                 data["players"][member.name]["points"] = random.randint(1, 14)
#
#                 if pos_x >= 11:
#                     pos_x = 2
#                     pos_y += 3
#                 else:
#                     pos_x += 3
#
#     with open("data/game.json", "w") as f:
#         json.dump(data, f)


@client.command(pass_context=True)
async def nextturn(ctx, stuff=""):
    """Activate next turn."""
    if ctx.message.author.name != "Muddy":
        return

    with open("data/game.json") as f:
        data = json.load(f)

    for player in data["players"]:
        data["players"][player]["points"] += 1

    with open("data/game.json", "w") as f:
        json.dump(data, f)

    board.create()
    for channel in ctx.message.server.channels:
        if channel.name == "gameboard":
            with open("images/board.png", "rb") as f:
                messages = []
                async for msg in client.logs_from(channel, limit=10):
                    await client.delete_message(msg)
                await client.send_file(channel, f)


@client.command(pass_context=True)
async def scram(ctx, stuff=""):
    """Close the bot."""
    if ctx.message.author.name != "Muddy":
        return

    await client.say("Peace out, gramps.")
    await client.logout()


client.run(TOKEN)
