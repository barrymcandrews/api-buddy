import asyncio
import aiofiles
import xml.etree.cElementTree as ElementTree
import os
from matrix import ScrollingTextMessage, Message, StaticTextMessage, ImageMessage


def create_fifo(path):
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path, mode=0o777)
    os.chmod(path, mode=0o777)


async def create_message(string) -> Message:
    xml = ElementTree.fromstring(string, parser=ElementTree.XMLParser(encoding="utf-8"))
    await asyncio.sleep(0.05)
    font_type = ""
    if 'style' in xml.attrib:
        font_type = "B" if xml.attrib['style'].lower() == 'bold' else "O"

    font = "7x13" + font_type

    await asyncio.sleep(0.05)

    msg_type = xml.attrib['type'].lower()
    if msg_type == "scroll":
        return ScrollingTextMessage(xml.text, font, xml.attrib['color'])
    elif msg_type == "static":
        return StaticTextMessage(xml.text, font, xml.attrib['color'], int(xml.attrib['delay']), int(xml.attrib['offset']))
    elif msg_type == "image":
        return ImageMessage(xml.attrib['src'], int(xml.attrib['delay']), int(xml.attrib['offset']))
    else:
        raise KeyError()


class QueueProtocol(asyncio.Protocol):
    def __init__(self, queue: asyncio.Queue):
        super().__init__()
        self.queue = queue
        self.complete_event = asyncio.Event()

    def data_received(self, data: bytes):
        string = data.decode("utf-8")
        print("Data recieved:\n" + string)
        self.queue.put_nowait(string)

    def connection_lost(self, exc):
        self.complete_event.set()


class XmlSource(object):
    def __init__(self, fifo_path):
        self.path = fifo_path
        self.raw_queue = asyncio.Queue()
        self.message_queue = asyncio.Queue()
        self.current_message = None
        self.protocol = QueueProtocol(self.raw_queue)

    async def start_read(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.parse_data())
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

    async def parse_data(self):
        while True:
            try:
                raw_data = await self.raw_queue.get()
                await self.message_queue.put(await create_message(raw_data))
            except (KeyError, ElementTree.ParseError) as e:
                print(e)

    async def get_message(self):
        while not self.message_queue.empty():
            self.current_message = await self.message_queue.get()
        return self.current_message




