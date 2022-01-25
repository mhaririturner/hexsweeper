#!/usr/bin/env python

"""
driver.py: Main driver for the hexsweeper game
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
DIFFICULTY = 0.25
FONT = pyglet.font.load(None, 16)
COLOR_BLACK = (0, 0, 0, 255)
# Determines specific window settings
PROD_MODE = False

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
live = True


def main():
    """
    Main loop for the game
    :return: None
    """
    # Initialize crap
    initialize_log()
    load_config()
    pyglet.options["vsync"] = True

    # Generate the grid
    generate_hexagonal_grid(GRID_SIZE)

    # Generate mines
    generate_mines(int(len(grid) * DIFFICULTY))

    # Tell the mines to love thy neighbor
    for cell in grid:
        cell.assess_neighbors(grid)

    # Set icon
    window.set_icon(pyglet.image.load("resources/hex.png"))

    # Set background to white
    glClearColor(255, 255, 255, 1.0)

    # Initial rendering pass for cells
    for cell in grid:
        cell.render(HEX_SCALE, window.width, window.height)

    if PROD_MODE:
        window.set_exclusive_keyboard()
        window.set_fullscreen()
    pyglet.clock.schedule_interval(func=update, interval=1 / 60)
    pyglet.app.run()


def generate_hexagonal_grid(radius):
    """
    Generates a "regular" hexagonal grid from a specified radius
    :param radius: The "radius" of the hexagonal grid
    :return: None
    """
    LOG.debug(f"Generating hexagonal grid with radius {radius}")
    for h in range(-radius, radius + 1):
        for k in range(-radius, radius + 1):
            if h * k > 0 and abs(h + k) > radius:
                LOG.debug(f"Skipped cell at ({h}, {k})")
            else:
                grid.append(HexCell(h, k))
                LOG.debug(f"Generating cell at ({h}, {k})")


def generate_mines(number):
    """
    Randomly generates a specified number of mines in a grid
    :param number: The quantity of mines to generate
    :return: None
    """
    for i in range(0, number):
        retry = True
        while retry:
            target = randint(0, len(grid) - 1)
            if not grid[target].get_mine():
                retry = False
                grid[target].set_mine()
                mines.append(grid[target])


def update(dt):
    """
    Necessary method to use pyglet internal draw updates
    :param dt: How much time has elapsed
    :return: None
    """
    return


def initialize_log():
    """
    Start the logging function
    :return: None
    """
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
    """
    Defines draw update cycles
    :return: None
    """
    window.clear()
    flag_count = 0
    # Display all the cells
    for cell in grid:
        cell.get_sprite().draw()
        label = cell.get_label()
        if label is not None:
            cell.render(HEX_SCALE, window.width, window.height)
        if cell.is_flagged():
            flag_count += 1
    # Display any context-specific labels
    for drawable in draw:
        drawable.draw()
    # Display flag counter label
    flags = len(mines) - flag_count
    flag_label = pyglet.text.Label(f"mines remaining: {flags}", font_name=FONT, font_size=16, color=COLOR_BLACK)
    flag_visual_offset = flag_label.content_height
    flag_label.update(flag_visual_offset, window.height - flag_visual_offset)
    flag_label.draw()
    # Display reset info label
    reset_label = pyglet.text.Label(f"press \"r\" to restart", font_name=FONT, font_size=16, color=COLOR_BLACK)
    reset_visual_offset = reset_label.content_height
    reset_label.update(reset_visual_offset, reset_visual_offset)
    reset_label.draw()


@window.event
def on_mouse_motion(x, y, dx, dy):
    """
    Updates sprites on mouseover
    :param x: Mouse x coordinate
    :param y: Mouse y coordinate
    :param dx: Mouse x direction
    :param dy: Mouse y direction
    :return: None
    """
    if not live:
        return
    for cell in grid:
        if cell.alive():
            sprite = cell.get_sprite()
            if sprite.image.height != sprite.image.width:
                LOG.critical("Invalid sprite image used, height/width mismatch")
            radius = sprite.image.height * HEX_SCALE / 2
            # Pythagorean theorem moment pog
            distance = math.sqrt((x - sprite.x) ** 2 + (y - sprite.y) ** 2)
            if distance < radius:
                cell.hover()
            else:
                cell.unhover()


@window.event
def on_mouse_press(x, y, buttons, modifiers):
    """
    Executes main game loop logic
    :param x: The x coordinate of the mouse press
    :param y: The y coordinate of the mouse pres
    :param buttons: Any buttons pressed
    :param modifiers: Any modifiers pressed
    :return: None
    """
    global live
    if not live:
        return
    for cell in grid:
        if cell.alive():
            sprite = cell.get_sprite()
            radius = sprite.image.height * HEX_SCALE / 2
            # Pythagorean theorem moment pog
            distance = math.sqrt((x - sprite.x) ** 2 + (y - sprite.y) ** 2)
            if distance < radius:
                if buttons == mouse.LEFT:
                    global first_move
                    if first_move and (cell.get_neighbor_number() != 0 or cell.get_mine()):
                        LOG.debug("Unacceptable first move, reconfiguring board")
                        mines_to_replenish = 0
                        replace = cell.get_neighbors()
                        replace.append(cell)
                        for cell_to_replace in replace:
                            if cell_to_replace.get_mine():
                                cell_to_replace.set_not_mine()
                                mines.remove(cell_to_replace)
                                mines_to_replenish += 1
                        # Make an array of all possible (non-mine) cells which can "legally" be turned into mines
                        options = []
                        for option in grid:
                            if option not in replace and not option.get_mine():
                                options.append(option)
                        for i in range(0, mines_to_replenish):
                            target = randint(0, len(options) - 1)
                            mines.append(options[target])
                            options[target].set_mine()
                            options.remove(options[target])
                        for refresh in grid:
                            refresh.assess_neighbors(grid)
                    first_move = False
                    if cell.mine():
                        LOG.info("Game lost")
                        # Expose all remaining mines
                        for c in mines:
                            c.mine()
                        # Temporary loss screen
                        label = pyglet.text.Label("loss", font_name=FONT, font_size=200, x=window.width / 2,
                                                  y=window.height / 2, anchor_x='center', anchor_y='center',
                                                  color=(255, 0, 0, 255))
                        backing = pyglet.shapes.Rectangle(window.width / 2 - label.content_width / 2,
                                                          window.height / 2 - label.content_height / 2,
                                                          label.content_width, label.content_height, color=(0, 0, 0))
                        backing.opacity = 128
                        draw.append(backing)
                        draw.append(label)
                        live = False
                    else:
                        swept = 0
                        for c in grid:
                            if not c.alive():
                                swept += 1
                        if len(grid) * (1 - DIFFICULTY) <= swept:
                            LOG.info("Game won")
                            # Temporary win screen
                            label = pyglet.text.Label("win", font_name=FONT, font_size=200, x=window.width / 2,
                                                      y=window.height / 2, anchor_x='center', anchor_y='center',
                                                      color=(0, 255, 0, 255))
                            backing = pyglet.shapes.Rectangle(window.width / 2 - label.content_width / 2,
                                                              window.height / 2 - label.content_height / 2,
                                                              label.content_width, label.content_height,
                                                              color=(0, 0, 0))
                            backing.opacity = 128
                            draw.append(backing)
                            draw.append(label)
                            live = False
                elif buttons == mouse.RIGHT:
                    cell.toggle_flag()


@window.event
def on_key_press(symbol, modifiers):
    """
    Handles keypress functionality
    :param symbol: The symbol pressed
    :param modifiers: Any key modifiers applied
    :return: None
    """
    if symbol == key.R:
        reset()
        window.invalid = True
    elif symbol == key.W and modifiers & key.MOD_COMMAND:
        LOG.debug("Closing via hotkey")
        window.close()


@window.event
def on_close():
    """
    Handles window close functionality
    :return: None
    """
    LOG.debug("Window close detected")
    finalize_log()


def reset():
    """
    Resets the game
    :return: None
    """
    LOG.info("Resetting")
    global grid, mines, draw, live, first_move
    grid = []
    mines = []
    draw = []
    first_move = True
    live = True
    generate_hexagonal_grid(GRID_SIZE)
    generate_mines(int(len(grid) * DIFFICULTY))
    for cell in grid:
        cell.assess_neighbors(grid)
        cell.render(HEX_SCALE, window.width, window.height)


def center_image(image):
    """
    Sets an image's anchor point to its center
    :param image: The image to center
    :return: None
    """
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


if __name__ == "__main__":
    main()
