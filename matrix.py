import asyncio
from abc import abstractmethod

from PIL import Image
from rgbmatrix import graphics, FrameCanvas
import rgbmatrix

import resources

options = rgbmatrix.RGBMatrixOptions()
options.rows = 16
options.cols = 32
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.disable_hardware_pulsing = True
options.pwm_lsb_nanoseconds = 200
matrix = rgbmatrix.RGBMatrix(options=options)


# --------------------------------------------------------------- #
# Messages
# --------------------------------------------------------------- #

class Message(object):
    def __init__(self):
        self.total_steps = 0
        self.step = 0

    @abstractmethod
    async def render(self, canvas, step) -> FrameCanvas:
        pass

    async def increment_step(self):
        self.step = self.step + 1

    async def reset(self):
        self.step = 0


class StaticTextMessage(Message):
    def __init__(self, text, font_name, color_hex, delay, offset):
        super().__init__()
        self.text = text
        self.font = resources.load_font(font_name)
        self.color = resources.load_color(color_hex)
        self.total_steps = delay
        self.offset = offset

    async def render(self, canvas, step) -> FrameCanvas:
        graphics.DrawText(canvas, self.font, self.offset, 12, self.color, self.text)
        return canvas


class ScrollingTextMessage(Message):
    def __init__(self, text, font_name, color_hex):
        super().__init__()
        self.text = text
        self.font = resources.load_font(font_name)
        self.color = resources.load_color(color_hex)

        width = options.cols
        canvas = matrix.CreateFrameCanvas()
        self.text_length = graphics.DrawText(canvas, self.font, width, 12, self.color, self.text)
        del canvas

        self.total_steps = width + self.text_length

    async def render(self, canvas, step) -> FrameCanvas:
        graphics.DrawText(canvas, self.font, canvas.width - self.step, 12, self.color, self.text)
        return canvas


class ImageMessage(Message):
    def __init__(self, image_path, delay, offset):
        super().__init__()
        self.image = resources.load_image(image_path)
        self.total_steps = delay
        self.offset = offset

    async def render(self, canvas, step) -> FrameCanvas:
        canvas.SetImage(self.image)
        return canvas

# --------------------------------------------------------------- #
# Main Board Loop
# --------------------------------------------------------------- #


async def write_to_board(sources):
    try:
        print("Main Loop Started.")
        current_source_index = 0
        current_source = sources[0]
        while True:
            message: Message = await current_source.get_message()
            current_source_index = (current_source_index + 1) % len(sources)
            current_source = sources[current_source_index]

            if message is None:
                await asyncio.sleep(0.5)
                continue

            canvas = matrix.CreateFrameCanvas()
            await message.reset()
            while message.step < message.total_steps:
                canvas.Clear()
                canvas = await message.render(canvas, message.step)
                await message.increment_step()
                canvas = matrix.SwapOnVSync(canvas)
                await asyncio.sleep(0.05)

    except asyncio.CancelledError:
        matrix.Clear()
        raise

