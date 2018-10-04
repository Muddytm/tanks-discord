"""Stuff for managing the game board."""

import config
from PIL import Image, ImageDraw, ImageFont
import json
import random
import urllib.request

# Grid length and height
dim_x = 14
dim_y = 14

# Template offets
temp_off_x = 120
temp_off_y = 100

# No need for tile_y - all tiles are squares.
tile_x = 160
tile_y = 160


def create():
    """Create image of game board."""

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
        dimy_y = 11

    filename = "images/board.png"
    img = Image.new("RGB", ((dim_x * tile_x) + temp_off_x,
                            (dim_y * tile_x) + temp_off_y),
                            color=(0, 0, 0))
    #img = Image.open("images/boardtemplate.png")
    d = ImageDraw.Draw(img)

    fnt = ImageFont.truetype(config.font_loc, 80)
    for x in range(dim_x):
        num_offset = 80
        if x > 9:
            num_offset = 30
        d.text(((x * tile_x) + temp_off_x + num_offset, 20), str(x), font=fnt, fill=(244, 246, 247))

    for y in range(dim_y):
        num_offset = 70
        if y > 9:
            num_offset = 20
        d.text((num_offset, (y * tile_y) + temp_off_y + 40), str(y), font=fnt, fill=(244, 246, 247))

    tile = Image.open("images/tiles/empty.png", "r")
    for x in range(dim_x):
        for y in range(dim_y):
            offset = ((x * tile_x) + temp_off_x, (y * tile_x) + temp_off_y)
            img.paste(tile, offset)

    with open("data/game.json") as f:
        data = json.load(f)

    for player in data["players"]:
        loc_x = data["players"][player]["x"]
        loc_y = data["players"][player]["y"]
        hp = data["players"][player]["hp"]
        points = data["players"][player]["points"]
        color_r = data["players"][player]["color"]["r"]
        color_g = data["players"][player]["color"]["g"]
        color_b = data["players"][player]["color"]["b"]

        d.rectangle((((loc_x * tile_x) + 12 + temp_off_x, (loc_y * tile_y) + 12 + temp_off_y),
                    ((loc_x * tile_x) + (tile_x - 12) + temp_off_x, (loc_y * tile_y) + (tile_y - 12) + temp_off_y)),
                    fill=(color_r, color_g, color_b))

        hpbar = Image.open("images/hp/hp{}.png".format(str(hp)))
        offset = ((loc_x * tile_x) + 20 + temp_off_x, (loc_y * tile_y) + 20 + temp_off_y)
        img.paste(hpbar, offset)

        pointbar = Image.open("images/points/points{}.png".format(str(points)))
        offset = ((loc_x * tile_x) + 20 + temp_off_x, (loc_y * tile_y) + 84 + temp_off_y)
        img.paste(pointbar, offset)

    with open("data/drops.json") as f:
        data = json.load(f)

    for type in data:
        if type == "hp":
            color = "red"
        elif type == "points":
            color = "white"
        for drop in data[type]:
            x = data[type][drop]["x"]
            y = data[type][drop]["y"]

            d.rectangle((((x * tile_x) + 48 + temp_off_x, (y * tile_y) + 48 + temp_off_y),
                        ((x * tile_x) + (tile_x - 48) + temp_off_x, (y * tile_y) + (tile_y - 48) + temp_off_y)),
                        fill=color)

    img.save(filename)


def create_drop():
    """Create a random drop if conditions are met (in other words...RNG)."""
    drop_chance = random.randint(1, 100)

    # Arbitrary 1/4 chance
    if drop_chance <= 25:
        types = ["points", "hp"]
        drop_type = random.choice(types)

        with open("data/game.json") as f:
            data = json.load(f)

        with open("data/drops.json") as f:
            drop_data = json.load(f)

        drop_x = random.randint(0, dim_x - 1)
        drop_y = random.randint(0, dim_y - 1)

        for player in data["players"]:
            if (drop_x != data["players"][player]["x"] or
                    drop_y != data["players"][player]["y"]):
                for drop in drop_data[drop_type]:
                    if (drop_x == drop_data[drop_type][drop]["x"] and
                            drop_y == drop_data[drop_type][drop]["y"]):
                        return False

                drop_data[drop_type]["{}{}".format(str(drop_x), str(drop_y))] = {"x": drop_x, "y": drop_y}
                with open("data/drops.json", "w") as f:
                    json.dump(drop_data, f)

                return True

        return False


if __name__ == "__main__":
    create()
