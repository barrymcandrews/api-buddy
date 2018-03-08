#!/usr/bin/env python3.6
import asyncio
import signal
import os
import uvloop
from setproctitle import setproctitle
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

    tasks = asyncio.gather(*asyncio.Task.all_tasks(), return_exceptions=True)
    loop.add_signal_handler(signal.SIGTERM, lambda: tasks.cancel())
    loop.add_signal_handler(signal.SIGINT, lambda: tasks.cancel())

    print("Starting Event Loop...")
    try:
        loop.run_until_complete(tasks)
    finally:
        loop.stop()
        loop.close()
        print("Event Loop Stopped.")
        os._exit(os.EX_OK)

