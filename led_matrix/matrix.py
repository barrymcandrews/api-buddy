import asyncio
import rgbmatrix

from led_matrix import configuration
from led_matrix.views import View, ImageView

matrix = rgbmatrix.RGBMatrix(options=configuration.matrix_options)


user_view: View = None
# default_view = SolidColorView('#008c1e', 1)
default_view = ImageView('resources/img/matrix.png', 1, 0)


async def start_driver():
    global user_view, default_view

    try:
        print("Main Loop Started.")
        while True:
            view: View = user_view if user_view is not None else default_view

            if view is None:
                await asyncio.sleep(0.005)
                continue

            canvas = matrix.CreateFrameCanvas()
            await view.reset()
            while view.step < view.total_steps:
                canvas.Clear()
                canvas = await view.render(canvas, view.step)
                await view.increment_step()
                canvas = matrix.SwapOnVSync(canvas)
                await asyncio.sleep(0.05)

    # except asyncio.CancelledError as e:
    except Exception as e:
        print(e)
        print("Main Loop Stopped.")
        matrix.Clear()
        raise

