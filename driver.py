#!/bin/bash

"""
driver.py: does stuff
"""

__author__ = "Max Hariri-Turner"
__email__ = "maxkht8@gmail.com"

import pyglet
from pyglet.window import key

window = pyglet.window.Window()

def main():
    print("sugma")
    pyglet.app.run()


@window.event
def on_draw():
    window.clear()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.A:
        print('The "A" key was pressed.')
    elif symbol == key.LEFT:
        print('The left arrow key was pressed.')
    elif symbol == key.ENTER:
        print('The enter key was pressed.')

if __name__ == "__main__":
    main()
