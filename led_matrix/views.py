import asyncio
import inspect
import io
import aiohttp

from time import strftime, localtime
from typing import List
from abc import abstractmethod
from rgbmatrix import graphics, FrameCanvas
from led_matrix import matrix, resources, data_sources, effects
from led_matrix import configuration
from led_matrix.data_sources import RestApi


class View(object):
    def __init__(self):
        self.total_steps = 1
        self.step = 0

    async def update_data(self):
        pass

    @abstractmethod
    async def render(self, canvas) -> FrameCanvas:
        self.step = (self.step + 1) % self.total_steps


class TextView(View):
    def __init__(self, text, font_name='7x13', color_hex='#00ff00', delay=5, offset=0):
        super().__init__()
        self.text = text
        self.font = resources.load_font(font_name)
        self.color = resources.load_color(color_hex)
        self.total_steps = delay
        self.offset = offset

    async def render(self, canvas) -> FrameCanvas:
        await super().render(canvas)
        graphics.DrawText(canvas, self.font, self.offset, 12, self.color, self.text)
        return canvas


class TimeView(TextView):
    def __init__(self, delay=300):
        super().__init__(None, offset=4, font_name='7x13B', color_hex='#FFFFFF', delay=delay)

    async def render(self, canvas):
        self.text = strftime("%H:%M:%S", localtime())
        return await super().render(canvas)


class ScrollingTextView(View):
    def __init__(self, text, font_name='7x13', color_hex='#00ff00'):
        super().__init__()
        self.text = text
        self.font = resources.load_font(font_name)
        self.color = resources.load_color(color_hex)
        self.text_length = 0

    async def update_data(self):
        width = configuration.matrix_options.cols * configuration.matrix_options.chain_length
        canvas = matrix.matrix.CreateFrameCanvas()
        self.text_length = graphics.DrawText(canvas, self.font, width, 12, self.color, self.text)
        del canvas
        self.total_steps = width + self.text_length

    async def render(self, canvas) -> FrameCanvas:
        await super().render(canvas)
        graphics.DrawText(canvas, self.font, canvas.width - self.step, 12, self.color, self.text)
        return canvas


class ApiView(ScrollingTextView):
    def __init__(self, api: RestApi, font_name='7x13', color_hex='#0000FF'):
        super().__init__(None, font_name=font_name, color_hex=color_hex)
        self.api = api

    async def update_data(self):
        if not self.api.initialized.is_set():
            await self.api.initialized.wait()
        self.text = self.api.text()
        await super().update_data()


class ImageView(View):
    def __init__(self, image_path, delay=1, offset=0):
        super().__init__()
        self.image = resources.load_image(image_path)
        self.total_steps = delay
        self.offset = offset

    async def render(self, canvas) -> FrameCanvas:
        await super().render(canvas)
        canvas.SetImage(self.image)
        return canvas


class AnimatedImageView(View):
    def __init__(self, image_path, delay=1, offset=0):
        super().__init__()
        self.frames = resources.load_animation(image_path)
        self.n_frames = len(self.frames)
        self.total_steps = delay * self.n_frames
        self.offset = offset

    async def render(self, canvas) -> FrameCanvas:
        await super().render(canvas)
        canvas.SetImage(self.frames[self.step % self.n_frames])
        await asyncio.sleep(0.05)
        return canvas


class ColorView(View):
    def __init__(self, color_hex, delay=1):
        super().__init__()
        self.color = resources.load_color(color_hex)
        self.total_steps = delay

    async def render(self, canvas) -> FrameCanvas:
        await super().render(canvas)
        canvas.Fill(self.color.red, self.color.green, self.color.blue)
        return canvas


class SequenceView(View):
    def __init__(self, views: List[View]):
        super().__init__()
        self.views: List[View] = views
        self.current_view = 0
        self.total_steps = 0
        for view in self.views:
            self.total_steps += view.total_steps

    async def update_data(self):
        await self.views[0].update_data()

    async def render(self, canvas):
        await super().render(canvas)
        if self.views[self.current_view].step == (self.views[self.current_view].total_steps - 1):
            self.current_view = (self.current_view + 1) % len(self.views)
            await self.views[self.current_view].update_data()
        return await self.views[self.current_view].render(canvas)


class GradientView(View):
    def __init__(self, angle, start_color, end_color, delay=1):
        super().__init__()
        self.total_steps = delay
        self.image = effects.gradient(angle, start_color, end_color)

    async def render(self, canvas):
        canvas.SetImage(self.image)
        return canvas


async def create_view(json: dict) -> View:
    view_class = globals()[json['type']]
    class_params = inspect.signature(view_class.__init__).parameters
    given_params = json['args']
    if 'image_url' in given_params:
        async with aiohttp.ClientSession() as session:
            async with session.get(json['image_url']) as resp:
                given_params['image_path'] = io.BytesIO(await resp.read())
    if 'api' in given_params:
        given_params['api'] = getattr(data_sources, given_params['api'])()
    for name, value in class_params.items():
        if type(value.default) == inspect._empty and name not in given_params:
            raise KeyError('Required argument missing: ' + name)
    return view_class(**given_params)

