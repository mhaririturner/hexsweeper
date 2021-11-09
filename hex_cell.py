#!/bin/bash

"""
hex_cell.py: does stuff
"""

__author__ = "Max Hariri-Turner"
__email__ = "maxkht8@gmail.com"

import math

# Constants
sin_30 = math.sin(math.radians(30))
cos_30 = math.cos(math.radians(30))

# Instance variables
h = 0
k = 0


class HexCell(object):
    def __init__(self):
        self.h = 0
        self.k = 0

    def __init__(self, major, minor):
        self.h = major
        self.k = minor

    def get_h(self):
        return self.h

    def get_k(self):
        return self.k

    def get_x(self, diameter):
        return self.k * diameter * cos_30

    def get_y(self, diameter):
        return self.h * diameter + self.k * diameter * sin_30
