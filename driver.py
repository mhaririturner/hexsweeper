#!/bin/bash

"""
driver.py: does stuff
"""

__author__ = "Max Hariri-Turner"
__email__ = "maxkht8@gmail.com"

import pyglet
import logging
import os
import datetime
import json

from pyglet.window import key
from pyglet.gl import glClearColor
from datetime import datetime

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

# Global variables
LOG = logging.getLogger(LOG_NAME)
window = pyglet.window.Window(WIDTH, HEIGHT, "hexsweeper", resizable=True)
event_loop = pyglet.app.EventLoop()
config = {"log_dir": "logs/", "log_ext": ".txt"}
draw = []


def main():
    initialize_log()
    load_config()
    initialize()
    batch = pyglet.graphics.Batch()
    hex_image = pyglet.image.load("resources/hex.png")
    center_image(hex_image)
    hex_sprite = pyglet.sprite.Sprite(img=hex_image, x=WIDTH / 2, y=HEIGHT / 2)

    # Set background to white
    glClearColor(255, 255, 255, 1.0)

    draw.append(hex_sprite)
    pyglet.app.run()


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
    for drawable in draw:
        drawable.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.A:
        print('The "A" key was pressed.')
    elif symbol == key.LEFT:
        print('The left arrow key was pressed.')
    elif symbol == key.ENTER:
        print('The enter key was pressed.')


@window.event
def on_close():
    LOG.debug("Window close detected")
    finalize_log()


def center_image(image):
    """
    Sets an image's anchor point to its center
    """
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


if __name__ == "__main__":
    main()
