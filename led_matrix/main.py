#!/usr/bin/env python3.6
import asyncio
import uvloop
import signal
import os
from setproctitle import setproctitle
from led_matrix.matrix import start_driver

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)
from led_matrix import mqtt

if __name__ == '__main__':
    setproctitle("led-matrix")

    asyncio.ensure_future(mqtt.start_client())
    asyncio.ensure_future(start_driver())

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

