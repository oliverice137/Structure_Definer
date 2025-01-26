# colors by Oliver Rice


import math as m

import numpy as np
from matplotlib import cm
from matplotlib import colors as col
from matplotlib import pyplot as plt
from numba import jit


class Colors:
    def __init__(self, cmap, start, stop):
        self.cmap = plt.get_cmap(cmap)
        self.norm = col.Normalize(vmin=start, vmax=stop)
        self.map = cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

    def get_rgb(self, val):
        rbg_map = self.map.to_rgba(val)[:3]
        rgb = tuple(map(lambda a: int(a * 255 + 0.5), rbg_map))
        oklab = self.rgb_to_oklab(rgb)
        oklch = self.oklab_to_oklch(oklab)
        oklch = (0.75, 0.1275, oklch[2])
        oklab = self.oklch_to_oklab(oklch)
        srgb = self.oklab_to_srgb(oklab)
        string = 'rgb('
        for val in srgb:
            string += str(val) + ','
        string = string[:-1] + ')'
        return string

    @staticmethod
    def rgb_get_hue(rgb):
        # rgb /= 255
        rgb = (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
        maxi = max(rgb)
        mini = min(rgb)
        max_index = rgb.index(maxi)
        if not max_index:
            hue = (rgb[1] - rgb[2]) / (maxi - mini)
        elif max_index == 1:
            hue = 2 + (rgb[1] - rgb[0]) / (maxi - mini)
        else:
            hue = 4 + (rgb[0] - rgb[1]) / (maxi - mini)
        if hue < 0:
            hue += 6
        hue /= 6
        return hue

    def rgb_to_oklab(self, rgb):
        r = self.gamma_to_linear(rgb[0] / 255)
        g = self.gamma_to_linear(rgb[1] / 255)
        b = self.gamma_to_linear(rgb[2] / 255)
        el = m.sqrt(m.sqrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b))
        em = m.sqrt(m.sqrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b))
        es = m.sqrt(m.sqrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b))
        return (el * 0.2104542553 + em * 0.7936177850 + es * -0.0040720468,
                el * 1.9779984951 + em * -2.4285922050 + es * 0.4505937099,
                el * 0.0259040371 + em * 0.7827717662 + es * -0.8086757660)

    def oklab_to_srgb(self, oklab):
        el = (oklab[0] + oklab[1] * 0.3963377774 + oklab[2] * 0.2158037573) ** 3
        em = (oklab[0] + oklab[1] * -0.1055613458 + oklab[2] * -0.0638541728) ** 3
        es = (oklab[0] + oklab[1] * -0.0894841775 + oklab[2] * -1.2914855480) ** 3
        r = el * 4.0767416621 + em * -3.3077115913 + es * 0.2309699292
        g = el * -1.2684380046 + em * 2.6097574011 + es * -0.3413193965
        b = el * -0.0041960863 + em * -0.7034186147 + es * 1.7076147010
        return (min(max(int(255 * self.linear_to_gamma(r) + 0.5), 0), 255),
                min(max(int(255 * self.linear_to_gamma(g) + 0.5), 0), 255),
                min(max(int(255 * self.linear_to_gamma(b) + 0.5), 0), 255))

    @staticmethod
    def oklab_to_oklch(oklab):
        c = m.sqrt(oklab[1] ** 2 + oklab[2] ** 2)
        h = (((m.atan2(oklab[2], oklab[1]) * 180) / m.pi % 360) + 360) % 360
        return oklab[0], c, h

    @staticmethod
    def oklch_to_oklab(oklch):
        a = oklch[1] * m.cos(oklch[2] * m.pi / 180)
        b = oklch[1] * m.sin(oklch[2] * m.pi / 180)
        return oklch[0], a, b

    @staticmethod
    def gamma_to_linear(n):
        if n >= 0.04045:
            return ((n + 0.055) / 1.055) ** 2.4
        else:
            return n / 12.92

    @staticmethod
    def linear_to_gamma(n):
        if n >= 0.0031308:
            return 1.055 * (n ** (1 / 2.4)) - 0.055
        else:
            return n * 12.92

    @staticmethod
    @jit(nopython=True)
    def get_oklch_arr(arr, lightness, chroma):
        for i in range(arr.shape[0]):
            if arr[i, 0] >= 0.04045:
                arr[i, 0] = ((arr[i, 0] + 0.055) / 1.055) ** 2.4
            else:
                arr[i, 0] = arr[i, 0] / 12.92
            if arr[i, 1] >= 0.04045:
                arr[i, 1] = ((arr[i, 1] + 0.055) / 1.055) ** 2.4
            else:
                arr[i, 1] = arr[i, 1] / 12.92
            if arr[i, 2] >= 0.04045:
                arr[i, 2] = ((arr[i, 2] + 0.055) / 1.055) ** 2.4
            else:
                arr[i, 2] = arr[i, 2] / 12.92

            r = m.sqrt(m.sqrt(0.4122214708 * arr[i, 0] + 0.5363325363 * arr[i, 1] + 0.0514459929 * arr[i, 2]))
            g = m.sqrt(m.sqrt(0.2119034982 * arr[i, 0] + 0.6806995451 * arr[i, 1] + 0.1073969566 * arr[i, 2]))
            b = m.sqrt(m.sqrt(0.0883024619 * arr[i, 0] + 0.2817188376 * arr[i, 1] + 0.6299787005 * arr[i, 2]))
            arr[i, 0] = r * 0.2104542553 + g * 0.7936177850 + b * -0.0040720468
            arr[i, 1] = r * 1.9779984951 + g * -2.4285922050 + b * 0.4505937099
            arr[i, 2] = r * 0.0259040371 + g * 0.7827717662 + b * -0.8086757660

            # h = (((m.atan2(arr[i, 2], arr[i, 1]) * 180) / m.pi % 360) + 360) % 360
            # arr[i, 0] = lightness
            # arr[i, 1] = chroma
            # arr[i, 2] = h
            #
            # a = arr[i, 1] * m.cos(arr[i, 2] * m.pi / 180)
            # b = arr[i, 1] * m.sin(arr[i, 2] * m.pi / 180)
            # arr[i, 1] = a
            # arr[i, 2] = b

            r = (arr[i, 0] + arr[i, 1] * 0.3963377774 + arr[i, 2]  * 0.2158037573) ** 3
            g = (arr[i, 0] + arr[i, 1] * -0.1055613458 + arr[i, 2] * -0.0638541728) ** 3
            b = (arr[i, 0] + arr[i, 1] * -0.0894841775 + arr[i, 2] * -1.2914855480) ** 3
            arr[i, 0] = r * 4.0767416621 + g * -3.3077115913 + b * 0.2309699292
            arr[i, 1] = r * -1.2684380046 + g * 2.6097574011 + b * -0.3413193965
            arr[i, 2] = r * -0.0041960863 + g * -0.7034186147 + b * 1.7076147010

            if arr[i, 0] >= 0.0031308:
                arr[i, 0] = 1.055 * (arr[i, 0] ** (1 / 2.4)) - 0.055
            else:
                arr[i, 0] = arr[i, 0] * 12.92
            if arr[i, 1] >= 0.0031308:
                arr[i, 1] = 1.055 * (arr[i, 1] ** (1 / 2.4)) - 0.055
            else:
                arr[i, 1] = arr[i, 1] * 12.92
            if arr[i, 2] >= 0.0031308:
                arr[i, 2] = 1.055 * (arr[i, 2] ** (1 / 2.4)) - 0.055
            else:
                arr[i, 2] = arr[i, 2] * 12.92

            arr[i, 0] = min(max(arr[i, 0], 0), 1)
            arr[i, 1] = min(max(arr[i, 1], 0), 1)
            arr[i, 2] = min(max(arr[i, 2], 0), 1)

        return arr


if __name__ == '__main__':
    print('Running colors...')
