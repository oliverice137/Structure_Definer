# transforms by Oliver Rice


import main
import numpy as np
import math as m
import random as r
from numba import jit


class Transforms:
    @main.tl.log_time_spacer
    def __init__(self):
        self._time_log_init()
        self.magnitude = 2
        self.x_scale = None
        self.y_scale = None
        self.z_scale = None
        self.xyz_scale = None
        self.theta = None
        self.psi = None
        self.phi = None
        self.cutoff_level = None

    @main.tl.log_time
    def value_translate(self, state):
        def fn(n): return n * (1 - 1 / self.magnitude) + 1 if n < 0 else n * (self.magnitude - 1) + 1
        self.xyz_scale = fn(state.get('transforms').get('xyz-scale'))
        self.x_scale = fn(state.get('transforms').get('x-scale')) * self.xyz_scale
        self.y_scale = fn(state.get('transforms').get('y-scale')) * self.xyz_scale
        self.z_scale = fn(state.get('transforms').get('z-scale')) * self.xyz_scale
        self.theta = state.get('transforms').get('theta')
        self.psi = state.get('transforms').get('psi')
        self.phi = state.get('transforms').get('phi')
        self.cutoff_level = state.get('transforms').get('cutoff-level')

    @staticmethod
    @main.tl.log_time
    def crop(array):
        return Transforms._crop(array)

    @staticmethod
    @jit(nopython=True)
    def _crop(array):
        z_start = 0
        z_end = -1
        y_start = 0
        y_end = -1
        x_start = 0
        x_end = -1
        while not np.count_nonzero(array[z_start]):
            z_start += 1
        while not np.count_nonzero(array[z_end]):
            z_end -= 1
        while not np.count_nonzero(array[:, y_start]):
            y_start += 1
        while not np.count_nonzero(array[:, y_end]):
            y_end -= 1
        while not np.count_nonzero(array[:, :, x_start]):
            x_start += 1
        while not np.count_nonzero(array[:, :, x_end]):
            x_end -= 1
        if z_end >= -2:
            z_end = array.shape[0]
        else:
            z_end += 1
        if y_end >= -2:
            y_end = array.shape[1]
        else:
            y_end += 1
        if x_end >= -2:
            x_end = array.shape[2]
        else:
            x_end += 1
        return array[z_start:z_end, y_start:y_end, x_start:x_end]

    @main.tl.log_time
    def cartesian_transform(self, array, scale=None):
        if scale is not None:
            zeros_shape = (m.ceil(array.shape[0] * scale[0]),
                           m.ceil(array.shape[1] * scale[1]),
                           m.ceil(array.shape[2] * scale[2]))
            zeros = np.zeros(zeros_shape, dtype=np.bool_)
            array = Transforms._cartesian_transform(array, zeros, scale)
        else:
            zeros_shape = (m.ceil(array.shape[0] * self.x_scale),
                           m.ceil(array.shape[1] * self.y_scale),
                           m.ceil(array.shape[2] * self.z_scale))
            zeros = np.zeros(zeros_shape, dtype=np.bool_)
            array = Transforms._cartesian_transform(array, zeros, (self.x_scale, self.y_scale, self.z_scale))
        return Transforms._crop(array)

    @staticmethod
    @jit(nopython=True)
    def _cartesian_transform(array, zeros, scale):
        for i in range(zeros.shape[0]):
            var0 = i / scale[0]
            for j in range(zeros.shape[1]):
                var1 = j / scale[1]
                for k in range(zeros.shape[2]):
                    if array[int(min(var0, array.shape[0] - 1)),
                             int(min(var1, array.shape[1] - 1)),
                             int(min(k / scale[2], array.shape[2] - 1))]:
                        zeros[i, j, k] = True
        return zeros

    @main.tl.log_time
    def rotate(self, array):
        shape = int(m.sqrt(array.shape[0] ** 2 + array.shape[1] ** 2 + array.shape[2] ** 2) + 0.5)
        zeros = np.zeros((shape, shape, shape), dtype=np.bool_)
        theta = self.theta * m.pi / 180 * 0.9861111111111111
        psi = self.psi * m.pi / 180 * 0.9861111111111111
        phi = self.phi * m.pi / 180 * 0.9861111111111111
        # noinspection PyTypeChecker
        rx = np.matrix([[1, 0, 0],
                        [0, m.cos(psi), -m.sin(psi)],
                        [0, m.sin(psi), m.cos(psi)]])
        # noinspection PyTypeChecker
        ry = np.matrix([[m.cos(phi), 0, m.sin(phi)],
                        [0, 1, 0],
                        [-m.sin(phi), 0, m.cos(phi)]])
        # noinspection PyTypeChecker
        rz = np.matrix([[m.cos(theta), -m.sin(theta), 0],
                        [m.sin(theta), m.cos(theta), 0],
                        [0, 0, 1]])
        rotation = rx * ry * rz
        array = np.pad(array, ((1, 1), (1, 1), (1, 1)))
        array = Transforms._rotate(array, zeros, rotation)
        return Transforms._crop(array)

    @staticmethod
    @jit(nopython=True)
    def _rotate(array, zeros, rotation):
        zero_bounds = ((0, 0, 0),
                       (0, 0, array.shape[2] - 1),
                       (0, array.shape[1] - 1, 0),
                       (0, array.shape[1] - 1, array.shape[2] - 1),
                       (array.shape[0] - 1, 0, 0),
                       (array.shape[0] - 1, 0, array.shape[2] - 1),
                       (array.shape[0] - 1, array.shape[1] - 1, 0),
                       (array.shape[0] - 1, array.shape[1] - 1, array.shape[2] - 1))
        x_values = []
        y_values = []
        z_values = []
        for x, y, z in zero_bounds:
            x_values.append(x * rotation[0, 0] + y * rotation[1, 0] + z * rotation[2, 0])
            y_values.append(x * rotation[0, 1] + y * rotation[1, 1] + z * rotation[2, 1])
            z_values.append(x * rotation[0, 2] + y * rotation[1, 2] + z * rotation[2, 2])
        x_shape = m.ceil(max(x_values) - min(x_values))
        y_shape = m.ceil(max(y_values) - min(y_values))
        z_shape = m.ceil(max(z_values) - min(z_values))
        zeros = zeros[:x_shape, :y_shape, :z_shape]
        var0 = zeros.shape[0] / 2
        var1 = zeros.shape[1] / 2
        var2 = zeros.shape[2] / 2
        var3 = (zeros.shape[0] - array.shape[0]) / 2
        var4 = (zeros.shape[1] - array.shape[1]) / 2
        var5 = (zeros.shape[2] - array.shape[2]) / 2
        var6 = int(var0 + 0.5)
        var7 = int(var1 + 0.5)
        var8 = int(var2 + 0.5)
        for i, x in enumerate(range(-var6, var6)):
            var9 = x * rotation[0, 0] + var0 - var3
            var10 = x * rotation[1, 0] + var1 - var4
            var11 = x * rotation[2, 0] + var2 - var5
            for j, y in enumerate(range(-var7, var7)):
                var12 = var9 + y * rotation[0, 1]
                var13 = var10 + y * rotation[1, 1]
                var14 = var11 + y * rotation[2, 1]
                for k, z in enumerate(range(-var8, var8)):
                    if array[min(max(int(var12 + z * rotation[0, 2] + 0.5), 0), array.shape[0] - 1),
                             min(max(int(var13 + z * rotation[1, 2] + 0.5), 0), array.shape[1] - 1),
                             min(max(int(var14 + z * rotation[2, 2] + 0.5), 0), array.shape[2] - 1)]:
                        zeros[i, j, k] = True
        return zeros

    @main.tl.log_time
    def cutoff(self, array):
        array = array[:, :, int(self.cutoff_level / 100 * array.shape[2] + 0.5):]
        return Transforms._crop(array)

    @staticmethod
    @main.tl.log_time
    def find_surface(arr, density=1):
        if len(arr.shape) == 2:
            padded_arr = np.pad(arr, pad_width=1)
            zeros = np.zeros_like(padded_arr)
            padded_arr = np.stack([zeros, arr, zeros])
        else:
            padded_arr = np.pad(arr, pad_width=1)
        neighbours_set = {(0, (0, 0, 0))}
        neighbours_set = Transforms._find_surface_neighbours(padded_arr, arr.shape, neighbours_set)
        neighbours_set.remove((0, (0, 0, 0)))
        neighbours = {
            0: set(),
            1: set(),
            2: set(),
            3: set(),
            4: set(),
            5: set(),
            6: set(),
            7: set(),
            8: set(),
            9: set(),
            10: set(),
            11: set(),
            12: set(),
            13: set(),
            14: set(),
            15: set(),
            16: set(),
            17: set(),
            18: set(),
            19: set(),
            20: set(),
            21: set(),
            22: set(),
            23: set(),
            24: set(),
            25: set(),
            26: set(),
        }
        for elem in neighbours_set:
            neighbours.get(elem[0]).add(elem[1])
        output_arr = np.zeros_like(arr)
        mod = 1 / density
        remainder = 0
        for i, elem in enumerate(neighbours_set):
            a, b, c = elem[1]
            remainder += 1
            if remainder >= mod:
                output_arr[a, b, c] = True
                remainder -= mod
            # if r.random() > 1 - density:
            #     output_arr[a, b, c] = True
        return output_arr

    @staticmethod
    @jit(nopython=True)
    def _find_surface_neighbours(arr, shape, neighbours_set):
        for i in range(shape[0]):
            for j in range(shape[1]):
                for k in range(shape[2]):
                    if arr[i+1, j+1, k+1]:
                        total_neighbours = np.sum(arr[i:i+3, j:j+3, k:k+3]) - 1
                        if 17 <= total_neighbours <= 25:
                            neighbours_set.add((total_neighbours, (i, j, k)))
        return neighbours_set

    @staticmethod
    @main.tl.log_time
    def hollow(arr, neighbours=5):
        if len(arr.shape) == 2:
            arr = np.pad(arr, pad_width=1)
            zeros = np.zeros_like(arr)
            arr = np.stack([zeros, arr, zeros])
        else:
            arr = np.pad(arr, pad_width=1)
        return Transforms._hollow(arr, neighbours)[1:-1, 1:-1, 1:-1]

    @staticmethod
    @jit(nopython=True)
    def _hollow(arr, neighbours):
        output_arr = np.zeros_like(arr)
        for i in range(arr.shape[0]):
            var0 = (i + 1) % arr.shape[0]
            var1 = (i - 1) % arr.shape[0]
            for j in range(arr.shape[1]):
                var2 = (j + 1) % arr.shape[1]
                var3 = (j - 1) % arr.shape[1]
                for k in range(arr.shape[2]):
                    if arr[i, j, k] and int(arr[var0, j, k]) + \
                            int(arr[var1, j, k]) + \
                            int(arr[i, var2, k]) + \
                            int(arr[i, var3, k]) + \
                            int(arr[i, j, (k + 1) % arr.shape[2]]) + \
                            int(arr[i, j, (k - 1) % arr.shape[2]]) <= neighbours:
                        output_arr[i, j, k] = True
        return output_arr

    @staticmethod
    def structure_hologram(arr, hologram, target):
        p = 1.6075
        count = np.count_nonzero(hologram)
        # surface_area = 4 * m.pi * (((x * y) ** p + (x * z) ** p + (y * z) ** p) / 3) ** (1 / p)
        # scaling = 1 / (2 ** -(m.log10(target / surface_area) / m.log10(4)))
        scaling = m.sqrt(target / count)
        zeros_shape = (m.ceil(arr.shape[0] * scaling), m.ceil(arr.shape[1] * scaling), m.ceil(arr.shape[2] * scaling))
        zeros = np.zeros(zeros_shape, dtype=np.bool_)
        arr = Transforms._cartesian_transform(arr, zeros, (scaling, scaling, scaling))
        arr = np.pad(arr, pad_width=1)
        return Transforms._hollow(arr, 5)[1:-1, 1:-1, 1:-1]

    @staticmethod
    def _time_log_init():
        main.tl.class_list.append(len(str(__class__).split('.')[-1][:-2]))
        main.tl.method_list.append(len(max([a for a in dir(Transforms)
                                            if callable(getattr(Transforms, a))
                                            and not a.startswith('_')], key=len)))
        main.tl.set_length()


if __name__ == '__main__':
    print('Running transforms')
