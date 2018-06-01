import rgbmatrix
from led_matrix import configuration
from led_matrix.views import View, ColorView, TimeView, ApiView, SequenceView
from led_matrix.data_sources import *

matrix = rgbmatrix.RGBMatrix(options=configuration.matrix_options)
canvas = matrix.CreateFrameCanvas()

home = configuration.HomeOptions
user_view: View = None
default_view = ColorView('#000000')

if home.enabled:
    views = []
    if home.show_weather:
        views.append(ApiView(WeatherApi(), font_name='7x13B'))
    if home.show_time:
        views.append(TimeView())
    if home.show_news:
        views.append(ApiView(NewsApi(), font_name='helvR12', color_hex='#FF0028'))
    if len(views) > 0:
        default_view = SequenceView(views)


async def start_driver():
    global user_view, default_view, canvas

    try:
        print("Main Loop Started.")
        while True:
            view: View = user_view if user_view is not None else default_view

            if view.step == 0:
                await view.update_data()

            canvas.Clear()
            canvas = await view.render(canvas)
            canvas = matrix.SwapOnVSync(canvas)
            await asyncio.sleep(0.05)

    # except asyncio.CancelledError as e:
    except Exception as e:
        print(e)
        print("Main Loop Stopped.")
        matrix.Clear()
        raise

