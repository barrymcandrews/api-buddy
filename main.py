#!/usr/bin/env python3.6
import asyncio
from setproctitle import setproctitle
import uvloop
from matrix import write_to_board
from sources import XmlSource

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)


srcs = [
    XmlSource("/tmp/led-source-spotify"),
    XmlSource("/tmp/led-source-weather"),
    XmlSource("/tmp/led-source-news"),
    XmlSource("/tmp/led-source-stock")
]


if __name__ == '__main__':
    setproctitle("matrix-driver")
    for source in srcs:
        asyncio.ensure_future(source.start_read())

    asyncio.ensure_future(write_to_board(srcs))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


