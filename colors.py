# colors by Oliver Rice


import math as m
from matplotlib import cm
from matplotlib import colors as col
from matplotlib import pyplot as plt


class Colors:
    def __init__(self, cmap, start, stop):
        self.cmap = plt.get_cmap(cmap)
        self.norm = col.Normalize(vmin=start, vmax=stop)
        self.map = cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

    def get_rgb(self, val):
        var = self.map.to_rgba(val)[:3]
        rgb = tuple(map(lambda a: int(a * 255 + 0.5), var))
        oklab = self.rgb_to_oklab(rgb)
        oklab = (0.70, oklab[1], oklab[2])
        srgb = self.oklab_to_srgb(oklab)
        string = 'rgb('
        for val in srgb:
            string += str(val) + ','
        string = string[:-1] + ')'
        return string

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


if __name__ == '__main__':
    print('Running colors...')
