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
SANS_SERIF = pyglet.font.load(None, 16)
FONT_SIZE = 16

# Instance variables
h = 0
k = 0
sprite = None
label = None
is_mine = None
is_live = None
list_neighbors = None
mine_neighbors = 0


def generate_neighbor_numbers(grid):
    for cell in grid:
        cell.assess_neighbors(grid)


class HexCell(object):
    def __init__(self, major, minor):
        self.h = major
        self.k = minor
        self.sprite = pyglet.sprite.Sprite(img=HEX_IMAGE)
        self.label = None
        self.is_mine = False
        self.is_live = True
        self.mine_neighbors = 0
        self.list_neighbors = []

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
        self.make_label(diameter, window_width, window_height)

    def get_sprite(self):
        return self.sprite

    def get_label(self):
        if self.is_mine:
            return None
        if self.mine_neighbors > 0 and (not self.is_live):
            return self.label

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
            if self.mine_neighbors == 0:
                print("Cascading")
                print(len(self.list_neighbors))
                for cell in self.list_neighbors:
                    if cell.alive():
                        cell.mine()
        else:
            image = HEX_BLOWN
            self.sprite.image = image
        return self.is_mine

    def assess_neighbors(self, grid):
        neighbors = 0
        for cell in grid:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx != dy:
                        if cell.get_h() == self.get_h() + dx and cell.get_k() == self.get_k() + dy:
                            self.list_neighbors.append(cell)
                            if cell.get_mine():
                                neighbors += 1
        self.mine_neighbors = neighbors

    def make_label(self, diameter, window_width, window_height):
        self.label = pyglet.text.Label(str(self.mine_neighbors), font_name=SANS_SERIF, font_size=FONT_SIZE,
                                       x=window_width / 2 + self.get_x(diameter),
                                       y=window_height / 2 + self.get_y(diameter),
                                       anchor_x='center', anchor_y='center', color=(0, 0, 0, 255))
