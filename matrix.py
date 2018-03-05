import asyncio
from abc import abstractmethod

from rgbmatrix import graphics, FrameCanvas
import rgbmatrix

options = rgbmatrix.RGBMatrixOptions()
options.rows = 16
options.cols = 32
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.disable_hardware_pulsing = True
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
    def __init__(self, text, font, color, delay, offset):
        super().__init__()
        self.text = text
        self.font = font
        self.color = color
        self.total_steps = delay
        self.offset = offset

    async def render(self, canvas, step) -> FrameCanvas:
        graphics.DrawText(canvas, self.font, self.offset, 12, self.color, self.text)
        return canvas


class ScrollingTextMessage(Message):
    def __init__(self, text, font, color):
        super().__init__()
        self.text = text
        self.font = font
        self.color = color

        width = options.cols
        canvas = matrix.CreateFrameCanvas()
        self.text_length = graphics.DrawText(canvas, self.font, width, 12, color, self.text)
        del canvas

        self.total_steps = width + self.text_length

    async def render(self, canvas, step) -> FrameCanvas:
        graphics.DrawText(canvas, self.font, canvas.width - self.step, 12, self.color, self.text)
        return canvas


# --------------------------------------------------------------- #
# Main Board Loop
# --------------------------------------------------------------- #


async def write_to_board(sources):
    try:
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
        pass
