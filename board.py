"""Stuff for managing the game board."""

from PIL import Image, ImageDraw, ImageFont
from imgurpython import ImgurClient
import json
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
    filename = "images/board.png"
    img = Image.new("RGB", ((dim_x * tile_x) + temp_off_x,
                            (dim_y * tile_x) + temp_off_y),
                            color=(0, 0, 0))
    #img = Image.open("images/boardtemplate.png")
    d = ImageDraw.Draw(img)

    fnt = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 80)
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

    img.save(filename)


if __name__ == "__main__":
    create()
