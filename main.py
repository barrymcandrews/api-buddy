#!/usr/bin/env python3.6

import asyncio
from logging import getLogger
import xml.etree.ElementTree as ET
import logging
import rgbmatrix
from rgbmatrix import graphics
import time
import aiofiles as aiofiles
import os
import uvloop

from protocols import InputProtocol, read_fifo

FIFO_FILE_PATHS = [
    "/tmp/led-source-spotify",
    "/tmp/led-source-weather",
    "/tmp/test"
]

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)

options = rgbmatrix.RGBMatrixOptions()
options.rows = 16
options.cols = 32
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.disable_hardware_pulsing = True
matrix = rgbmatrix.RGBMatrix(options=options)

messages = asyncio.Queue()


class TextSource(object):
    def __init__(self, fifo_path):
        self.path = fifo_path
        self.queue = asyncio.Queue()
        self.current_message = None

    def put_message(self, message):
        self.queue.put_nowait(message)

    async def get_message(self):
        while not self.queue.empty():
            self.current_message = await self.queue.get()
        return self.current_message


sources = [
    TextSource("/tmp/led-source-spotify"),
    TextSource("/tmp/led-source-weather"),
    TextSource("/tmp/led-source-news"),
    TextSource("/tmp/led-source-stock")
]


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


async def write_to_board():
    try:
        current_source_index = 0
        current_source = sources[0]
        while True:
            message: ET = await current_source.get_message()
            current_source_index = (current_source_index + 1) % len(sources)
            current_source = sources[current_source_index]

            if message is None:
                await asyncio.sleep(0.5)
                continue

            offscreen_canvas = matrix.CreateFrameCanvas()
            font = graphics.Font()
            font_type = ""
            if 'style' in message.attrib:
                font_type = "B" if message.attrib['style'].lower() == 'bold' else "O"

            font.LoadFont("./fonts/7x13" + font_type + ".bdf")
            r, g, b = hex_to_rgb(message.attrib['color'])
            text_color = graphics.Color(r, g, b)
            pos = offscreen_canvas.width
            length = 0

            if message.attrib['type'].lower() == "scroll":
                while pos + length >= 0:
                    offscreen_canvas.Clear()
                    length = graphics.DrawText(offscreen_canvas, font, pos, 12, text_color, message.text)
                    pos -= 1

                    # if pos + length < 0 and messages.empty():
                    #     pos = offscreen_canvas.width

                    await asyncio.sleep(0.05)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
            else:
                graphics.DrawText(offscreen_canvas, font, int(message.attrib['offset']), 12, text_color, message.text)
                matrix.SwapOnVSync(offscreen_canvas)
                await asyncio.sleep(int(message.attrib['delay']))

    except asyncio.CancelledError:
        pass


if __name__ == '__main__':

    for source in sources:
        asyncio.ensure_future(read_fifo(source))

    asyncio.ensure_future(write_to_board())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


