import asyncio
from abc import abstractmethod
from rgbmatrix import graphics, FrameCanvas
from led_matrix import matrix, resources


class View(object):
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


class StaticTextView(View):
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


class ScrollingTextView(View):
    def __init__(self, text, font_name='7x13', color_hex='#00ff00'):
        super().__init__()
        self.text = text
        self.font = resources.load_font(font_name)
        self.color = resources.load_color(color_hex)

        width = matrix.options.cols * matrix.options.chain_length
        canvas = matrix.matrix.CreateFrameCanvas()
        self.text_length = graphics.DrawText(canvas, self.font, width, 12, self.color, self.text)
        del canvas

        self.total_steps = width + self.text_length

    async def render(self, canvas, step) -> FrameCanvas:
        graphics.DrawText(canvas, self.font, canvas.width - self.step, 12, self.color, self.text)
        return canvas


class ImageView(View):
    def __init__(self, image_path, delay, offset):
        super().__init__()
        self.image = resources.load_image(image_path)
        self.total_steps = delay
        self.offset = offset

    async def render(self, canvas, step) -> FrameCanvas:
        canvas.SetImage(self.image)
        return canvas


class AnimatedImageView(View):
    def __init__(self, image_path, delay, offset):
        super().__init__()
        self.frames = resources.load_animation(image_path)
        self.n_frames = len(self.frames)
        self.total_steps = delay * self.n_frames
        self.offset = offset

    async def render(self, canvas, step) -> FrameCanvas:
        canvas.SetImage(self.frames[self.step % self.n_frames])
        await asyncio.sleep(0.05)
        return canvas


class SolidColorView(View):
    def __init__(self, color_hex, delay):
        super().__init__()
        self.color = resources.load_color(color_hex)
        self.total_steps = delay

    async def render(self, canvas, step) -> FrameCanvas:
        canvas.Fill(self.color.red, self.color.green, self.color.blue)
        return canvas
