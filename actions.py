"""Helper functions for action-based stuff."""

import json
import random

# Grid length and height
dim_x = 14
dim_y = 14

got_count = False


def action(action, x, y, ctx):
    """An all-in-one function for actions."""
    #set_dims()

    name = ctx.message.author.name
    #private = ctx.message.channel.is_private
    private = True

    try:
        x = int(x)
        y = int(y)
    except Exception:
        return ("Please use correct syntax, with two numbers as the parameter. Example: `!{} 6 9`".format(action)), False

    if x < 0 or y < 0 or x >= dim_x or y >= dim_y:
        return ("Nice try."), False

    if private:
        with open("data/game.json") as f:
            data = json.load(f)

        cur_x = data["players"][name]["x"]
        cur_y = data["players"][name]["y"]

        points = data["players"][name]["points"]

        check, cost = valid_location(action, points, x, y, cur_x, cur_y)

        if check == "valid":
            data["players"][name]["points"] -= cost
            data["players"][name]["x"] = x
            data["players"][name]["y"] = y
            response = "You moved to coordinate ({}, {}).".format(str(x), str(y))
        elif check == "shot":
            data["players"][name]["points"] -= cost
            for player in data["players"]:
                if data["players"][player]["x"] == x and data["players"][player]["y"] == y:
                    data["players"][player]["hp"] -= 1
                    response = "You dealt 1 point of damage to {}!".format(player)
                    if data["players"][player]["hp"] == 0:
                        del data["players"][player]
                        data["jury"][player] = ""
                        response += "\nThey're dead!"
                    break
        elif check == "donated":
            data["players"][name]["points"] -= cost
            for player in data["players"]:
                if data["players"][player]["x"] == x and data["players"][player]["y"] == y:
                    if data["players"][player]["points"] < 14:
                        data["players"][player]["points"] += 1
                        response = "You donated 1 point to {}!".format(player)
                    else:
                        return "{} is holding the maximum amount of points (14).".format(player), False
                    break
        elif check == "gotpoints":
            data["players"][name]["points"] -= cost
            data["players"][name]["points"] += 3
            if data["players"][name]["points"] > 14:
                data["players"][name]["points"] = 14
            data["players"][name]["x"] = x
            data["players"][name]["y"] = y
            response = "You moved to coordinate ({}, {}) and picked up a points drop!".format(str(x), str(y))
        elif check == "gothp":
            data["players"][name]["points"] -= cost
            if data["players"][name]["hp"] < 3:
                data["players"][name]["hp"] += 1
            data["players"][name]["x"] = x
            data["players"][name]["y"] = y
            response = "You moved to coordinate ({}, {}) and picked up an HP drop!".format(str(x), str(y))
        elif check == "blocked":
            return "There's already a player there.", False
        elif check == "missed":
            return "There's nobody to shoot there.", False
        elif check == "invalid":
            return "You don't have enough points to do that (short by {}).".format(cost), False
        elif check == "nopoints":
            return "You're all out of points until next turn.", False
        elif check == "dead":
            return "That player is dead...", False

        with open("data/game.json", "w") as f:
            json.dump(data, f)

        return response, True


def valid_location(action, points, x, y, cur_x, cur_y):
    """Return string based on the action and target coordinates."""
    if points == 0:
        return "nopoints", 0

    if action == "move":
        distance = (0 + points)
    else:
        distance = (2 + points)

    cost = (abs(cur_x - x) + abs(cur_y - y))
    if action != "move" and cost < 4:
        cost = 3

    if cost <= distance:
        with open("data/game.json") as f:
            data = json.load(f)

        for player in data["players"]:
            if data["players"][player]["x"] == x and data["players"][player]["y"] == y:
                if action == "move":
                    return "blocked", 0
                elif action == "shoot":
                    if data["players"][player]["hp"] > 0:
                        return "shot", (cost - 2)
                    else:
                        return "dead", 0
                elif action == "donate":
                    if data["players"][player]["hp"] > 0:
                        return "donated", (cost - 2)
                    else:
                        return "dead", 0

        if action == "move":
            with open("data/drops.json") as f:
                drop_data = json.load(f)

            for type in drop_data:
                for drop in drop_data[type]:
                    if (drop_data[type][drop]["x"] == x and
                            drop_data[type][drop]["y"] == y):
                        del drop_data[type][drop]
                        with open("data/drops.json", "w") as f:
                            json.dump(drop_data, f)
                        return "got{}".format(type), cost

            return "valid", cost
        else:
            return "missed", 0
    else:
        return "invalid", (cost - distance)


def get_player_info():
    """Return string with player info."""
    response = "**REMAINING PLAYERS:**\n"

    with open("data/game.json") as f:
        data = json.load(f)

    for player in data["players"]:
        hp = data["players"][player]["hp"]
        points = data["players"][player]["points"]
        x = data["players"][player]["x"]
        y = data["players"][player]["y"]
        color = data["players"][player]["color"]["name"]

        response += ("{} ({}) | HP: {} | Points {} | Location: ({}, {})"
                     "\n".format(player, color, hp, points, str(x), str(y)))

    return response


def set_dims():
    """Set dimension variables."""
    global dim_y
    global got_count

    if not got_count:
        with open("data/game.json") as f:
            player_list = json.load(f)

        all_players = []
        for type in player_list:
            for player in player_list[type]:
                all_players.append(player)

        player_count = len(all_players)

        if player_count < 5:
            dim_y = 5
        elif player_count < 9:
            dim_y = 8
        elif player_count < 13:
            dim_y = 11
        else:
            dim_y = 14

        got_count = True
