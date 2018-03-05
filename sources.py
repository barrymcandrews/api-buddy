from abc import abstractmethod
import asyncio
from rgbmatrix import graphics

import aiofiles
import xml.etree.cElementTree as ElementTree
import os

from matrix import ScrollingTextMessage, Message, StaticTextMessage


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def create_fifo(path):
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path, mode=0o777)
    os.chmod(path, mode=0o777)


class Source(object):

    @abstractmethod
    async def start_read(self):
        pass

    @abstractmethod
    def put_message(self, message):
        pass

    @abstractmethod
    async def get_message(self):
        pass


class XmlSource(Source):
    def __init__(self, fifo_path):
        self.path = fifo_path
        self.queue = asyncio.Queue()
        self.current_message = None
        self.protocol = self.XmlProtocol(self)

    class XmlProtocol(asyncio.Protocol):
        def __init__(self, source):
            super().__init__()
            self.source = source
            self.complete_event = asyncio.Event()

        def data_received(self, data: bytes):
            string = data.decode("utf-8").replace("\n", "")
            print(string)
            try:
                xmlParser = ElementTree.XMLParser(encoding="utf-8")
                message = self.create_message(ElementTree.fromstring(string, parser=xmlParser))
                self.source.put_message(message)
            except KeyError:
                pass

        def connection_lost(self, exc):
            self.complete_event.set()

        @staticmethod
        def create_message(xml) -> Message:
            font_type = ""
            if 'style' in xml.attrib:
                font_type = "B" if xml.attrib['style'].lower() == 'bold' else "O"

            # TODO: Load resources ONLY in-between messages (So you can't see the pause)
            font = graphics.Font()
            font.LoadFont("./fonts/7x13" + font_type + ".bdf")

            r, g, b = hex_to_rgb(xml.attrib['color'])
            text_color = graphics.Color(r, g, b)

            if xml.attrib['type'].lower() == "scroll":
                return ScrollingTextMessage(xml.text, font, text_color)
            elif xml.attrib['type'].lower() == "static":
                return StaticTextMessage(xml.text, font, text_color, int(xml.attrib['delay']), int(xml.attrib['offset']))
            else:
                raise KeyError()

    async def start_read(self):
        loop = asyncio.get_event_loop()
        while True:
            try:
                create_fifo(self.path)
                self.protocol.complete_event.clear()
                fifo = await aiofiles.open(self.path, mode='r')
                await loop.connect_read_pipe(lambda: self.protocol, fifo)
                await self.protocol.complete_event.wait()
                await fifo.close()
            except OSError:
                pass

    def put_message(self, message):
        self.queue.put_nowait(message)

    async def get_message(self):
        while not self.queue.empty():
            self.current_message = await self.queue.get()
        return self.current_message
