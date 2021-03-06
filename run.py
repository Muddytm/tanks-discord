import actions
import asyncio
import board
import datetime
from discord.ext import commands
import config
import discord
import json
import os
import random
import sys
import time

tanks_channel = "tanks-testing"
TOKEN = config.app_token
BOT_PREFIX = "!"
client = commands.Bot(command_prefix=commands.when_mentioned_or(BOT_PREFIX))

game = False
next_activate = True


if not os.path.isfile("data/drops.json"):
    with open("data/drops.json", "w") as outfile:
        data = {"points": {}, "hp": {}}
        json.dump(data, outfile)


if not os.path.isfile("data/game.json"):
    with open("data/game.json", "w") as outfile:
        data = {"players": {}, "jury": {}}
        json.dump(data, outfile)


if not os.path.isfile("data/registered.json"):
    with open("data/registered.json", "w") as outfile:
        data = []
        json.dump(data, outfile)


@client.event
async def on_ready():
    print ("Logged in as")
    print (client.user.name)
    print (client.user.id)
    print ("------")

    # Run this with run.py nextturn
    if len(sys.argv) > 1 and sys.argv[1] == "nextturn":
        next_activate = False
        for channel in client.get_all_channels():
            if channel.name == "commands":
                with open("data/game.json") as f:
                    data = json.load(f)

                for player in data["players"]:
                    if data["players"][player]["points"] < 14:
                        data["players"][player]["points"] += 1

                vote_counter = {}
                jury = False
                for member in data["jury"]:
                    jury = True
                    if data["jury"][member]:
                        if data["jury"][member] not in vote_counter:
                            vote_counter[data["jury"][member]] = 1
                        else:
                            vote_counter[data["jury"][member]] += 1

                        data["jury"][member] = ""

                highest_count = 0
                victor = ""
                tie = True
                for name in vote_counter:
                    if vote_counter[name] > highest_count:
                        highest_count = vote_counter[name]
                        victor = name
                        tie = False
                    elif vote_counter[name] == highest_count:
                        tie = True

                if not tie and victor and highest_count > 0:
                    data["players"][victor]["points"] += 1

                with open("data/game.json", "w") as f:
                    json.dump(data, f)

                drop_created = board.create_drop()
                board.create()
                for board_channel in channel.server.channels:
                    if board_channel.name == "gameboard":
                        with open("images/board.png", "rb") as f:
                            messages = []
                            async for msg in client.logs_from(board_channel, limit=10):
                                messages.append(msg)
                            await client.delete_messages(messages)
                            await client.send_file(board_channel, f)
                        await client.send_message(board_channel, actions.get_player_info())
                        break

                prefix = ""
                if jury:
                    if tie:
                        victor = "Tied vote - no player"
                    elif not victor:
                        victor = "There were no votes, so no one"

                    prefix = "{} won the jury vote!\n".format(victor)

                suffix = ""
                if drop_created:
                    suffix = "\nA lootbox has dropped on the battlefield!"

                await client.send_message(channel, "{}**The next turn has begun, and all living players have received a point.**{}".format(prefix, suffix))

                for jury_channel in channel.server.channels:
                    if jury_channel.name == "jury":
                        await client.send_message(jury_channel,
                                                  "The next turn has started, and all votes have been reset.")
                        break

                await client.logout()


@client.event
async def on_message(message):
    """Activates on any message sent."""
    #if message.author == client.user:
    #    return
    # This allows us to use other commands as well.
    await client.process_commands(message)


@client.command(pass_context=True)
async def register(ctx, stuff=""):
    """Register for the game!"""
    if ctx.message.channel.name != "commands":
        return

    with open("data/registered.json") as f:
        data = json.load(f)

    if ctx.message.author.name in data:
        await client.send_message(ctx.message.channel, "You're already registered!")
        return

    if len(data) >= 16:
        await client.send_message(ctx.message.channel, "Game is full up!")
        return

    member = ctx.message.author
    for role in member.server.roles:
        if role.name == "Players":
            await client.add_roles(member, role)
            data.append(member.name)
            with open("data/registered.json", "w") as f:
                json.dump(data, f)
            await client.send_message(ctx.message.channel, "You're now registered!")
            return


@client.command(pass_context=True)
async def generategame(ctx, stuff=""):
    """Generate the game info."""
    if ctx.message.author.name != "Muddy":
        return

    dim_x = 14
    dim_y = 14
    randlocs = []

    data = {"players": {}, "jury": {}}
    pos_x = 2
    pos_y = 2

    with open("data/colors.json") as f:
        colors = json.load(f)

    color_list = []
    for color in colors:
        color_list.append(color)

    with open("data/drops.json", "w") as outfile:
        drop_data = {"points": {}, "hp": {}}
        json.dump(drop_data, outfile)

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

                if stuff == "random":
                    pos_x = random.randint(0, dim_x - 1)
                    pos_y = random.randint(0, dim_y - 1)

                    while "{} {}".format(str(pos_x), str(pos_y)) in randlocs:
                        pos_x = random.randint(0, dim_x - 1)
                        pos_y = random.randint(0, dim_y - 1)

                    randlocs.append("{} {}".format(str(pos_x), str(pos_y)))

                data["players"][member.name]["x"] = pos_x
                data["players"][member.name]["y"] = pos_y
                data["players"][member.name]["hp"] = 3
                data["players"][member.name]["points"] = 1

                if pos_x >= 11:
                    pos_x = 2
                    pos_y += 3
                else:
                    pos_x += 3

            if role.name == "Jury" and role in member.roles:
                await client.remove_roles(member, role)

    with open("data/game.json", "w") as f:
        json.dump(data, f)

    board.create()

    for channel in ctx.message.server.channels:
        if channel.name == "gameboard":
            with open("images/board.png", "rb") as f:
                messages = []
                async for msg in client.logs_from(channel, limit=10):
                    messages.append(msg)
                await client.delete_messages(messages)
                await client.send_file(channel, f)
            await client.send_message(channel, actions.get_player_info())


@client.command(pass_context=True)
async def move(ctx, x="", y=""):
    """!move up/down/left/right"""
    if ctx.message.channel.name != "commands":
        return

    with open("data/game.json") as f:
        data = json.load(f)

    suffix = ", from {} {}".format(data["players"][ctx.message.author.name]["x"],
                                   data["players"][ctx.message.author.name]["y"])

    action = "{}: {} {} {}".format(ctx.message.author.name, "move", x, y)
    # action_queue.append(action)
    # print (action_queue)
    # while action_queue[0] != action:
    #     time.sleep(2)

    response, changed = actions.action("move", x, y, ctx)
    await client.send_message(ctx.message.channel, response)

    if changed:
        board.create()
        for channel in ctx.message.server.channels:
            if channel.name == "gameboard":
                with open("images/board.png", "rb") as f:
                    messages = []
                    async for msg in client.logs_from(channel, limit=10):
                        messages.append(msg)
                    await client.delete_messages(messages)
                    await client.send_file(channel, f)
                await client.send_message(channel, actions.get_player_info())


        for channel in ctx.message.server.channels:
            if channel.name == "actionlog":
                await client.send_message(channel, action + suffix)

    # action_queue.pop(0)


@client.command(pass_context=True)
async def shoot(ctx, x="", y=""):
    """!shoot up/down/left/right"""
    if ctx.message.channel.name != "commands":
        return

    action = "{}: {} {} {}".format(ctx.message.author.name, "shoot", x, y)
    # action_queue.append(action)
    # print (action_queue)
    # while action_queue[0] != action:
    #     time.sleep(2)

    response, changed = actions.action("shoot", x, y, ctx)
    await client.send_message(ctx.message.channel, response)

    if changed:
        board.create()
        for channel in ctx.message.server.channels:
            if channel.name == "gameboard":
                with open("images/board.png", "rb") as f:
                    messages = []
                    messages = []
                    async for msg in client.logs_from(channel, limit=10):
                        messages.append(msg)
                    await client.delete_messages(messages)
                    await client.send_file(channel, f)
                await client.send_message(channel, actions.get_player_info())

        for channel in ctx.message.server.channels:
            if channel.name == "actionlog":
                with open("data/game.json") as f:
                    data = json.load(f)
                suffix = ", from {} {}".format(data["players"][ctx.message.author.name]["x"],
                                               data["players"][ctx.message.author.name]["y"])
                await client.send_message(channel, action + suffix)

        with open("data/game.json") as f:
            data = json.load(f)

        for member in ctx.message.server.members:
            for role in ctx.message.server.roles:
                if member.name in data["jury"] and role.name == "Jury":
                    await client.add_roles(member, role)

    # action_queue.pop(0)


@client.command(pass_context=True)
async def donate(ctx, x="", y=""):
    """!donate up/down/left/right"""
    if ctx.message.channel.name != "commands":
        return

    action = "{}: {} {} {}".format(ctx.message.author.name, "donate", x, y)
    # action_queue.append(action)
    # print (action_queue)
    # while action_queue[0] != action:
    #     time.sleep(2)

    response, changed = actions.action("donate", x, y, ctx)
    await client.send_message(ctx.message.channel, response)

    if changed:
        board.create()
        for channel in ctx.message.server.channels:
            if channel.name == "gameboard":
                with open("images/board.png", "rb") as f:
                    messages = []
                    async for msg in client.logs_from(channel, limit=10):
                        messages.append(msg)
                    await client.delete_messages(messages)
                    await client.send_file(channel, f)
                await client.send_message(channel, actions.get_player_info())

        for channel in ctx.message.server.channels:
            if channel.name == "actionlog":
                with open("data/game.json") as f:
                    data = json.load(f)
                suffix = ", from {} {}".format(data["players"][ctx.message.author.name]["x"],
                                               data["players"][ctx.message.author.name]["y"])
                await client.send_message(channel, action + suffix)

    # action_queue.pop(0)


@client.command(pass_context=True)
async def vote(ctx, stuff=""):
    """Vote for a player to receive a point. Available only to jury."""
    if ctx.message.channel.name != "jury":
        return

    with open("data/game.json") as f:
        data = json.load(f)

    if ctx.message.author.name not in data["jury"]:
        return
    else:
        for player in data["players"]:
            if stuff.lower() in player.lower():
                data["jury"][ctx.message.author.name] = player
                await client.send_message(ctx.message.channel, "You are now voting for {}.".format(player))
                with open("data/game.json", "w") as f:
                    json.dump(data, f)
                return

        await client.send_message(ctx.message.channel, "No player with that name was found.")
        return


@client.command(pass_context=True)
async def refresh(ctx, stuff=""):
    """Refresh the board."""
    if "muddy" not in ctx.message.author.name.lower():
        return

    board.create()
    for channel in ctx.message.server.channels:
        if channel.name == "gameboard":
            with open("images/board.png", "rb") as f:
                messages = []
                async for msg in client.logs_from(channel, limit=10):
                    messages.append(msg)
                await client.delete_messages(messages)
                await client.send_file(channel, f)
            await client.send_message(channel, actions.get_player_info())


@client.command(pass_context=True)
async def test(ctx, stuff=""):
    """Test."""
    await client.say("owo")


@client.command(pass_context=True)
async def scram(ctx, stuff=""):
    """Close the bot."""
    if ctx.message.author.name != "Muddy":
        return

    await client.say("Peace out, gramps.")
    await client.logout()


client.run(TOKEN)
