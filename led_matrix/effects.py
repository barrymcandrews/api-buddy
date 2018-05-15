import numpy as np
from PIL import Image
from led_matrix import configuration


def hexstring_to_rgb(s):
    r = int(s[1:3], 16)
    g = int(s[3:5], 16)
    b = int(s[5:7], 16)
    return r, g, b


def gradient(angle, start_c, end_c) -> Image:
    a = np.radians(angle)
    c1 = hexstring_to_rgb(start_c)
    c2 = hexstring_to_rgb(end_c)
    h = configuration.matrix_options.rows
    w = configuration.matrix_options.cols * configuration.matrix_options.chain_length
    image = Image.new('RGB', (w, h))
    d = (w * np.sin(a)) + (h * np.cos(a))

    for y in range(0, h):
        for x in range(0, w):
            d0 = np.absolute((np.tan(a) * x) + y) / np.sqrt(np.tan(a)**2 + 1)
            res = (c1 + (d0 / d) * np.subtract(c2, c1)).astype(int)
            image.putpixel((x, y), (res[0], res[1], res[2]))
    return image


if __name__ == '__main__':
    gradient(45, '#FFFFFF', '#000000').show()

