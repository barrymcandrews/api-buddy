import asyncio
import os
import aiofiles
import xml.etree.ElementTree as ET


class InputProtocol(asyncio.Protocol):

    def __init__(self, source):
        super().__init__()
        self.complete_event = asyncio.Event()
        self.source = source

    def connection_made(self, transport):
        print('connection made')

    def data_received(self, data: bytes):
        string = data.decode("utf-8").replace("\n", "")
        print(string)
        parser = ET.XMLParser(encoding="utf-8")
        self.source.put_message(ET.fromstring(string, parser=parser))

    def eof_received(self):
        print("EOF Received!")

    def connection_lost(self, exc):
        print("Connection Lost!")
        self.complete_event.set()

    def pause_writing(self):
        print("Writing Paused!")

    def resume_writing(self):
        print("Writing Resumed")


def create_fifo(path):
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path, mode=0o777)
    os.chmod(path, mode=0o777)


async def read_fifo(source):
    input_protocol = InputProtocol(source)
    loop = asyncio.get_event_loop()
    while True:
        try:
            create_fifo(source.path)
            input_protocol.complete_event.clear()
            fifo = await aiofiles.open(source.path, mode='r')
            await loop.connect_read_pipe(lambda: input_protocol, fifo)
            await input_protocol.complete_event.wait()
            await fifo.close()
        except OSError as e:
            pass
