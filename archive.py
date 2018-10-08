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

# @client.command(pass_context=True)
# async def startgame(ctx, stuff=""):
#     """Start game, and go to the next turn after a specified amount of time."""
#     if ctx.message.author.name != "Muddy":
#         return
#
#     turn = 0
#     game = True
#
#     if ctx.message.author.name != "Muddy":
#         return
#
#     while game:
#         if turn > 0:
#             with open("data/game.json") as f:
#                 data = json.load(f)
#
#             for player in data["players"]:
#                 if data["players"][player]["points"] < 14:
#                     data["players"][player]["points"] += 1
#
#             vote_counter = {}
#             jury = False
#             for member in data["jury"]:
#                 jury = True
#                 if data["jury"][member] not in vote_counter:
#                     vote_counter[data["jury"][member]] = 1
#                 else:
#                     vote_counter[data["jury"][member]] += 1
#
#                 data["jury"][member] = ""
#
#             highest_count = 0
#             victor = ""
#             tie = True
#             for name in vote_counter:
#                 if vote_counter[name] > highest_count:
#                     highest_count = vote_counter[name]
#                     victor = name
#                     tie = False
#                 elif vote_counter[name] == highest_count:
#                     tie = True
#
#             if not tie and victor and highest_count > 0:
#                 data["players"][victor]["points"] += 1
#
#             with open("data/game.json", "w") as f:
#                 json.dump(data, f)
#
#             drop_created = board.create_drop()
#             board.create()
#             for channel in ctx.message.server.channels:
#                 if channel.name == "gameboard":
#                     with open("images/board.png", "rb") as f:
#                         messages = []
#                         async for msg in client.logs_from(channel, limit=10):
#                             messages.append(msg)
#                         await client.delete_messages(messages)
#                         await client.send_file(channel, f)
#                     await client.send_message(channel, actions.get_player_info())
#
#             prefix = ""
#             if jury:
#                 if not victor:
#                     victor = "Tied vote - no player"
#
#                 prefix = "{} won the jury vote!\n"
#
#             suffix = ""
#             if drop_created:
#                 suffix = "\nA lootbox has dropped on the battlefield!"
#
#             await client.send_message(ctx.message.channel, "{}**The next turn has begun, and all living players have received a point.**{}".format(prefix, suffix))
#
#         turn += 1
#         time.sleep(30)
