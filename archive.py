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
