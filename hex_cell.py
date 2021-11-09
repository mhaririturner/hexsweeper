#!/bin/bash

"""
hex_cell.py: does stuff
"""

__author__ = "Max Hariri-Turner"
__email__ = "maxkht8@gmail.com"

import math
import pyglet

# Constants
SIN_30 = math.sin(math.radians(30))
COS_30 = math.cos(math.radians(30))
HEX_IMAGE = pyglet.image.load("resources/hex.png")
HEX_IMAGE.anchor_x = HEX_IMAGE.width // 2
HEX_IMAGE.anchor_y = HEX_IMAGE.height // 2
HEX_HOVER = pyglet.image.load("resources/hex_hover.png")
HEX_HOVER.anchor_x = HEX_HOVER.width // 2
HEX_HOVER.anchor_y = HEX_HOVER.height // 2
HEX_CLEAR = pyglet.image.load("resources/hex_clear.png")
HEX_CLEAR.anchor_x = HEX_CLEAR.width // 2
HEX_CLEAR.anchor_y = HEX_CLEAR.height // 2
HEX_BLOWN = pyglet.image.load("resources/hex_blown.png")
HEX_BLOWN.anchor_x = HEX_BLOWN.width // 2
HEX_BLOWN.anchor_y = HEX_BLOWN.height // 2

# Instance variables
h = 0
k = 0
sprite = None
is_mine = None
is_live = None


class HexCell(object):
    def __init__(self, major, minor):
        self.h = major
        self.k = minor
        self.sprite = pyglet.sprite.Sprite(img=HEX_IMAGE)
        self.is_mine = False
        self.is_live = True

    def get_h(self):
        return self.h

    def get_k(self):
        return self.k

    def get_x(self, diameter):
        return self.k * diameter * COS_30

    def get_y(self, diameter):
        return self.h * diameter + self.k * diameter * SIN_30

    def alive(self):
        return self.is_live

    def render(self, scale, window_width, window_height):
        diameter = HEX_IMAGE.width * scale
        self.sprite.update(scale=scale, x=window_width / 2 + self.get_x(diameter),
                           y=window_height / 2 + self.get_y(diameter))

    def get_sprite(self):
        return self.sprite

    def hover(self):
        image = HEX_HOVER
        self.sprite.image = image

    def unhover(self):
        image = HEX_IMAGE
        self.sprite.image = image

    def get_mine(self):
        return self.is_mine

    def set_mine(self):
        self.is_mine = True

    def mine(self):
        self.is_live = False
        if not self.is_mine:
            image = HEX_CLEAR
            self.sprite.image = image
        else:
            image = HEX_BLOWN
            self.sprite.image = image
        return self.is_mine
