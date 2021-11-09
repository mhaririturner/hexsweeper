#!/bin/bash

"""
driver.py: does stuff
"""

__author__ = "Max Hariri-Turner"
__email__ = "maxkht8@gmail.com"

from random import randint

import pyglet
import logging
import os
import datetime
import json
import math


from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import glClearColor
from datetime import datetime
from hex_cell import HexCell
import hex_cell

FILE_CONFIG = "config.json"

# Constants
# Logging format for entries
LOGGING_FORMAT = "%(name)-32s %(asctime)s %(levelname)-8s %(message)s"
# Logging format for times
LOGGING_TIME_FORMAT = "%H:%M:%S"
# Default logging level
default_logging_level = logging.DEBUG
LOG_NAME = "driver"
start_time = datetime.now()
WIDTH = 1280
HEIGHT = 720
HEX_SCALE = 0.1
GRID_SIZE = 5
DIFFICULTY = 0.9

# Global variables
LOG = logging.getLogger(LOG_NAME)
window = pyglet.window.Window(width=WIDTH, height=HEIGHT, caption="hexsweeper", resizable=True)
event_loop = pyglet.app.EventLoop()
config = {"log_dir": "logs/", "log_ext": ".txt"}
grid = []
grid_batch = pyglet.graphics.Batch()
draw = []
mines = []
first_move = True


def main():
    # Initialize crap
    initialize_log()
    load_config()
    initialize()

    # Generate the grid
    generate_hexagonal_grid(GRID_SIZE)

    # Generate mines
    generate_mines(int(len(grid) * DIFFICULTY))

    # Tell the mines to love thy neighbor
    hex_cell.generate_neighbor_numbers(grid)

    # Set icon
    window.set_icon(pyglet.image.load("resources/hex.png"))

    # Set background to white
    glClearColor(255, 255, 255, 1.0)

    # Initial rendering pass for cells
    for cell in grid:
        cell.render(HEX_SCALE, window.width, window.height)

    pyglet.clock.schedule_interval(func=update, interval=1/240)
    pyglet.app.run()


def generate_hexagonal_grid(radius):
    LOG.debug(f"Generating hexagonal grid with radius {radius}")
    for h in range(-radius, radius + 1):
        for k in range(-radius, radius + 1):
            if h * k > 0 and abs(h + k) > radius:
                LOG.debug(f"Skipped cell at ({h}, {k})")
            else:
                grid.append(HexCell(h, k))
                LOG.debug(f"Generating cell at ({h}, {k})")


def generate_mines(number):
    for i in range(0, number):
        retry = True
        while retry:
            target = randint(0, len(grid) - 1)
            if not grid[target].get_mine():
                retry = False
                grid[target].set_mine()
                mines.append(grid[target])


def update(dt):
    return


def initialize():
    LOG.debug("Initializing")
    pyglet.options["vsync"] = True


def initialize_log():
    global start_time
    file_name = f"{config['log_dir']}{start_time.strftime('%Y_%m_%d_%H_%M_%S')}{config['log_ext']}"
    logging.basicConfig(filename=file_name, level=default_logging_level, format=LOGGING_FORMAT,
                        datefmt=LOGGING_TIME_FORMAT)


def finalize_log():
    """
    Writes the logs to disk
    :return: None
    """
    if not os.path.exists(config["log_dir"]):
        os.makedirs(config["log_dir"])
        LOG.warning("Creating log directory")
    now = datetime.now()
    then = start_time
    elapsed = now - then
    LOG.info(f"Process complete ({str(elapsed)} elapsed)")


def load_config():
    """
    Loads config options from the config file
    :return: None
    """
    LOG.debug(f"Attempting to load {FILE_CONFIG!r}")
    with open(FILE_CONFIG, "r") as json_file:
        data = json.load(json_file)
    for data_key in data.keys():
        config[data_key] = data[data_key]
        LOG.debug(f"Loaded config field {data_key!r} with value {data[data_key]!r}")
    LOG.debug(f"{FILE_CONFIG!r} loaded, {len(data)} config options loaded")


@window.event
def on_draw():
    window.clear()
    for cell in grid:
        cell.get_sprite().draw()
        label = cell.get_label()
        if label is not None:
            label.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    for cell in grid:
        if cell.alive():
            sprite = cell.get_sprite()
            if sprite.image.height != sprite.image.width:
                LOG.critical("Invalid sprite image used, height/width mismatch")
            radius = sprite.image.height * HEX_SCALE / 2
            # Pythagorean theorem moment pog
            distance = math.sqrt((x - sprite.x)**2 + (y - sprite.y)**2)
            if distance < radius:
                cell.hover()
            else:
                cell.unhover()


@window.event
def on_mouse_press(x, y, buttons, modifiers):
    for cell in grid:
        if cell.alive():
            sprite = cell.get_sprite()
            radius = sprite.image.height * HEX_SCALE / 2
            # Pythagorean theorem moment pog
            distance = math.sqrt((x - sprite.x)**2 + (y - sprite.y)**2)
            if distance < radius:
                if buttons == mouse.LEFT:
                    global first_move
                    if first_move and (cell.get_neighbor_number() != 0 or cell.get_mine()):
                        reset()
                        on_mouse_press(x, y, buttons, modifiers)
                    else:
                        first_move = False
                        cell.mine()
                if buttons == mouse.RIGHT:
                    cell.toggle_flag()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.A:
        print('The "A" key was pressed.')
    elif symbol == key.LEFT:
        print('The left arrow key was pressed.')
    elif symbol == key.ENTER:
        print('The enter key was pressed.')
    elif symbol == key.R:
        reset()
        window.invalid = True



@window.event
def on_close():
    LOG.debug("Window close detected")
    finalize_log()


def reset():
    print("Resetting")
    LOG.info("Resetting")
    global grid, mines, first_move
    grid = []
    mines = []
    first_move = True
    generate_hexagonal_grid(GRID_SIZE)
    generate_mines(int(len(grid) * DIFFICULTY))
    hex_cell.generate_neighbor_numbers(grid)
    for cell in grid:
        cell.render(HEX_SCALE, window.width, window.height)


def center_image(image):
    """
    Sets an image's anchor point to its center
    """
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


if __name__ == "__main__":
    main()
