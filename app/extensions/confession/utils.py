import random

import discord


def random_color(seed: int):
    rng = random.Random(seed)
    hue = rng.random()
    saturation = rng.random()
    value = 0.8

    return discord.Color.from_hsv(hue, saturation, value)


def format_id(content: str):
    result = content.replace("#", "")

    if not result.isnumeric():
        return

    return int(result)
