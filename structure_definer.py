# structure_definer by Oliver Rice


import main
import numpy as np
import math as m
import itertools as it
from colors import Colors
from numba import jit
from tqdm import tqdm
from skspatial.objects import Plane, Points


class StructureDefiner:
    @main.tl.log_time_spacer
    def __init__(self):
        self._time_log_init()
        self.shape = None
        self.face_add = False
        self.face_new = True
        self.face_number = 0
        self.face_delete = False
        self.faces_updated = False
        self.faces = {}

    @main.tl.log_time
    def add_face(self, clickdata):
        if self.face_new:
            i = 0
            while self.faces.get(f'face_{i}') is not None:
                i += 1
            self.faces.update({f'face_{i}': {'initialised_plane': False, 'original_points': set()}})
            self.face_number = i
            self.faces_updated = True
            self.face_new = False

        if clickdata is not None:
            if clickdata.get('points')[0].get('curveNumber') == 0:
                x = clickdata.get('points')[0].get('x')
                y = clickdata.get('points')[0].get('y')
                z = clickdata.get('points')[0].get('z')
                self.faces.get(f'face_{self.face_number}').get('original_points').add((x, y, z))

                if len(self.faces.get(f'face_{self.face_number}').get('original_points')) == 3:
                    points = tuple(self.faces.get(f'face_{self.face_number}').get('original_points'))
                    plane = StructureDefiner._plane_equation(points)
                    base_point = (self.shape[0] / 2, self.shape[1] / 2, 0)

                    if not self._positive_polarity(plane, base_point):
                        plane = (-plane[0], -plane[1], -plane[2], -plane[3])

                    x, y, z = self._intercepts(plane)
                    self.faces.get(f'face_{self.face_number}').update({
                        'intercepts': (x, y, z),
                        'plane_equation': plane,
                        'distance': self._distance((0, 0, 0), plane),
                        'group': 0,
                        'color': None,
                        'adjacent_faces': [],
                        'initialised_plane': True,
                    })
                    self.update_colors()
                    self.adjacent_faces()
                    self.face_add = False
                    self.face_new = True
                    self.faces_updated = False

    @main.tl.log_time
    def delete_face(self, clickdata):
        if self.face_delete:
            if clickdata is not None:
                face = clickdata.get('points')[0].get('curveNumber')
                if face:
                    self.faces.pop(f'face_{face - 1}')
                    self.face_delete = False
                    self.update_colors()
                    self.update_indexes()
                    self.adjacent_faces()
                    self.faces_updated = True

    def update_colors(self):
        colors = Colors('hsv', 0, len(self.faces))
        for i, key in enumerate(self.faces.keys()):
            self.faces.get(key).update({'color': colors.get_rgb(i)})

    def update_indexes(self):
        swap = {}
        for i, (key, value) in enumerate(self.faces.items()):
            swap.update({key: value})
        self.faces = {}
        for i, value in enumerate(swap.values()):
            self.faces.update({f'face_{i}': value})
        # swap = {}
        # for i, (key, value) in enumerate(self.faces_simulated.items()):
        #     swap.update({key: value})
        # self.faces_simulated = {}
        # for i, value in enumerate(swap.values()):
        #     self.faces_simulated.update({f'face_{i}': value})

    def check_initialised_plane(self):
        lst = []
        for key in self.faces.keys():
            lst.append(self.faces.get(key).get('initialised_plane'))
        return sum(lst)

    @main.tl.log_time
    def adjacent_faces(self):
        low_res = 128
        high_res = low_res * 4
        for key, value in self.faces.items():
            if value.get('initialised_plane'):
                intercepts = value.get('intercepts')
                x = (low_res / self.shape[2]) * intercepts[0]
                y = (low_res / self.shape[1]) * intercepts[1]
                z = (low_res / self.shape[0]) * intercepts[2]
                lr_plane = StructureDefiner._plane_equation(((x, 0, 0), (0, y, 0), (0, 0, z)))
                outside = StructureDefiner._outside(lr_plane, low_res)
                x = (high_res / self.shape[2]) * intercepts[0]
                y = (high_res / self.shape[1]) * intercepts[1]
                z = (high_res / self.shape[0]) * intercepts[2]
                hr_plane = StructureDefiner._plane_equation(((x, 0, 0), (0, y, 0), (0, 0, z)))
                distance = self._distance((0, 0, 0), hr_plane)
                self.faces.get(key).update({
                    'outside_lr': outside,
                    'plane_hr': StructureDefiner._plane(hr_plane, distance, high_res),
                    'intersections': {},
                    'initialised_plane': True
                })

        intersections = {}
        for i, keys in enumerate(it.combinations(self.faces.keys(), 2)):
            intersection = self.faces.get(keys[0]).get('outside_lr').intersection(
                self.faces.get(keys[1]).get('outside_lr'))
            if intersection:
                intersections.update({f'intersection_{i}': {'faces': {keys[0], keys[1]},
                                                            'points': intersection}})
                i += 1

        for keys in it.permutations(intersections.keys(), 2):
            if keys[0] in intersections.keys() and keys[1] in intersections.keys() and \
                    intersections.get(keys[0]).get('points').issubset(
                        intersections.get(keys[1]).get('points')):
                intersections.pop(keys[0])

        for key in self.faces.keys():
            for value in intersections.values():
                if key in value.get('faces'):
                    faces = value.get('faces').copy()
                    faces.remove(key)
                    self.faces.get(key).get('intersections').update({list(faces)[0]: value.get('points')})

        for key0 in self.faces.keys():
            if len(self.faces.get(key0).get('intersections').keys()) >= 3:
                intersections = [*self.faces.get(key0).get('intersections').keys()]
                for intersection in intersections:
                    cutoff_0 = set()
                    for point in self.faces.get(key0).get('plane_hr'):
                        point_lr = (point[0] // 4, point[1] // 4, point[2] // 4)
                        if point_lr not in self.faces.get(intersection).get('outside_lr'):
                            cutoff_0.add(point)
                    cutoff_1 = set()
                    for point in self.faces.get(intersection).get('plane_hr'):
                        point_lr = (point[0] // 4, point[1] // 4, point[2] // 4)
                        if point_lr not in self.faces.get(key0).get('outside_lr'):
                            cutoff_1.add(point)
                    remaining = [elem for elem in intersections if elem != intersection]
                    for combos in it.combinations(remaining, 2):
                        if intersection in self.faces.get(key0).get('intersections'):
                            plane_intersection = self.faces.get(combos[0]).get('plane_hr') \
                                .intersection(self.faces.get(combos[1]).get('plane_hr'))
                            if len(plane_intersection.intersection(cutoff_0)) and \
                                    len(plane_intersection.intersection(cutoff_1)):
                                self.faces.get(key0).get('intersections').pop(intersection)
                                self.faces.get(intersection).get('intersections').pop(key0)

        for key in self.faces.keys():
            self.faces.get(key).update({'adjacent_faces': list(self.faces.get(key).get('intersections'))})

    @main.tl.log_time
    def form_sample(self, hollow):
        x, y, z = hollow.nonzero()
        print(len(x))
        print(len(y))
        print(len(z))

    @main.tl.log_time_spacer
    def polyhedralise(self, figure):
        factor = 1
        scale = (1 / factor, 1 / factor, 1 / factor)
        figure = main.tf.cartesian_transform(figure, scale)
        # hollow = main.tf.hollow(figure, 5)
        # hollow[:, :, 0] = main.tf.hollow(hollow[:, :, 0], 3)
        hollow = figure
        # hollow[:, :, 0] = main.tf.hollow(hollow[:, :, 0], 3)
        search_radius = 6
        normal_dict, neighbour_dict = StructureDefiner.normals(hollow, search_radius)
        regions = StructureDefiner.create_regions(normal_dict, neighbour_dict)
        base_point = (figure.shape[0] / 2, figure.shape[1] / 2, 0)
        colors = Colors('hsv', 0, len(regions.keys()))
        self.faces = {}
        for i, key in tqdm(enumerate(regions.keys())):
            # intercepts = StructureDefiner._intercepts(StructureDefiner.p_fit(tuple(regions.get(key)[1])))
            # print(intercepts)
            # intercept_x = int(intercepts[0] / scale[0] + 0.5)
            # intercept_y = int(intercepts[1] / scale[1] + 0.5)
            # intercept_z = int(intercepts[2] / scale[2] + 0.5)
            # plane = StructureDefiner._plane_equation(((intercept_x, 0, 0), (0, intercept_y, 0), (0, 0, intercept_z)))
            plane = StructureDefiner._plane_fit(tuple(regions.get(key).get('region')))
            base_point = (self.shape[0] / 2, self.shape[1] / 2, 0)
            if not self._positive_polarity(plane, base_point):
                plane = (-plane[0], -plane[1], -plane[2], -plane[3])
            x, y, z = self._intercepts(plane)
            self.faces.update({f'face_{i}': {
                'intercepts': (x, y, z),
                'plane_equation': plane,
                'distance': self._distance((0, 0, 0), plane),
                'group': 0,
                'color': colors.get_rgb(i),
                'adjacent_faces': [],
                'size': regions.get(key).get('size'),
                'region': regions.get(key).get('region'),
                'point': regions.get(key).get('point'),
                'initialised_plane': True,
            }})
        self.faces_updated = True
        self.adjacent_faces()

    @staticmethod
    @main.tl.log_time
    def create_regions(normal_dict, neighbour_dict):
        curvature = 30
        minimum_size = 64
        maximum_regions = 6
        angles = {}
        for key in normal_dict.keys():
            angles.update({key: set()})
        for keys in it.combinations(normal_dict.keys(), 2):
            angle = StructureDefiner.vector_angle(
                    normal_dict.get(keys[0]), normal_dict.get(keys[1]))
            if angle <= curvature:
                angles.get(keys[0]).add(keys[1])
                angles.get(keys[1]).add(keys[0])
        regions = {}
        points = set(normal_dict.keys())
        all_regions_found = False
        region_n = 0
        while not all_regions_found and len(regions) < maximum_regions:
            no_regions_found = True
            maximum = 0
            for point in points:
                neighbours = neighbour_dict.get(point).copy()
                region = {point}
                searched = {point}
                search_exhausted = False
                while not search_exhausted:
                    none_found = True
                    new_neighbours = neighbours.difference(searched)
                    for neighbour in new_neighbours:
                        if neighbour in angles.get(point):
                            region.add(neighbour)
                            neighbours.update(neighbour_dict.get(neighbour).copy())
                            none_found = False
                        searched.add(neighbour)
                    if none_found:
                        search_exhausted = True
                size = len(region) - 1
                if size > maximum and size >= minimum_size:
                    regions.update({f'face_{region_n}': {'size': size, 'region': region, 'point': point}})
                    maximum = size
                    no_regions_found = False
            if no_regions_found:
                all_regions_found = True
            else:
                intersection = points.intersection(regions.get(f'face_{region_n}').get('region'))
                points.difference_update(regions.get(f'face_{region_n}').get('region'))
                for point in points:
                    angles.get(point).difference_update(intersection)
                region_n += 1
        return regions

    @staticmethod
    def vector_angle(vec_0, vec_1):
        tolerance = 1e-9
        if abs(abs(vec_0[0]) - abs(vec_1[0])) > tolerance or \
                abs(abs(vec_0[1]) - abs(vec_1[1])) > tolerance or abs(abs(vec_0[2]) - abs(vec_1[2])) > tolerance:
            return m.acos((vec_0[0] * vec_1[0] + vec_0[1] * vec_1[1] + vec_0[2] * vec_1[2]) /
                          (m.sqrt(vec_0[0] ** 2 + vec_0[1] ** 2 + vec_0[2] ** 2) *
                           m.sqrt(vec_1[0] ** 2 + vec_1[1] ** 2 + vec_1[2] ** 2))) * 180 / m.pi
        return 0

    @staticmethod
    @main.tl.log_time
    def normals(hollow, search_radius):
        sphere = np.zeros((search_radius * 2 + 1, search_radius * 2 + 1, search_radius * 2 + 1), dtype=np.bool_)
        hollow_shape = hollow.shape
        hollow = np.pad(hollow, search_radius)
        normals = StructureDefiner._normals(hollow, hollow_shape, search_radius, sphere)
        normal_dict = {}
        neighbour_dict = {}
        for elem in normals:
            normal_dict.update({elem[0]: StructureDefiner._p_fit(tuple(elem[1]))[:3]})
            neighbour_dict.update({elem[0]: elem[1]})
        return normal_dict, neighbour_dict

    @staticmethod
    @jit(nopython=True)
    def _normals(hollow, hollow_shape, search_radius, sphere):
        for x in range(sphere.shape[0]):
            s0 = (x - search_radius) ** 2
            for y in range(sphere.shape[1]):
                s1 = (y - search_radius) ** 2
                for z in range(sphere.shape[2]):
                    if s0 + s1 + (z - search_radius) ** 2 <= search_radius ** 2:
                        sphere[x, y, z] = True
        normals = []
        for i in range(hollow_shape[0]):
            i_s = i + search_radius
            for j in range(hollow_shape[1]):
                j_s = j + search_radius
                for k in range(hollow_shape[2]):
                    if hollow[i_s, j_s, k + search_radius]:
                        samples = set()
                        for x in range(sphere.shape[0]):
                            i_x = i + x
                            i_x_s = i_x - search_radius
                            for y in range(sphere.shape[1]):
                                j_y = j + y
                                j_y_s = j_y - search_radius
                                for z in range(sphere.shape[2]):
                                    k_z = k + z
                                    if hollow[i_x, j_y, k_z] and sphere[x, y, z]:
                                        samples.add((i_x_s, j_y_s, k_z - search_radius))
                        if len(samples) >= 3:
                            normals.append(((i, j, k), samples))
        return normals

    @staticmethod
    def _plane_equation(points):
        ab = np.array((points[0][0] - points[1][0], points[0][1] - points[1][1], points[0][2] - points[1][2]))
        ac = np.array((points[0][0] - points[2][0], points[0][1] - points[2][1], points[0][2] - points[2][2]))
        n = np.cross(ab, ac)
        d = np.dot(n, points[0])
        if n[0].is_integer() and n[1].is_integer() and n[2].is_integer() and d.is_integer():
            return int(n[0]), int(n[1]), int(n[2]), int(d)
        return float(n[0]), float(n[1]), float(n[2]), float(d)

    @staticmethod
    def _p_fit(points):
        points = Points(points)
        plane = Plane.best_fit(points)
        normal = plane.normal
        return normal[0], normal[1], normal[2], plane.distance_point((0, 0, 0))

    @staticmethod
    def _plane_fit(points):
        centroid = np.mean(points, axis=0)
        points = points - centroid
        u, s, vh = np.linalg.svd(points)
        n = vh[2, :]
        d = np.dot(n, centroid)
        return float(n[0]), float(n[1]), float(n[2]), float(d)

    @staticmethod
    def _positive_polarity(plane, point):
        if plane[0] * point[0] + plane[1] * point[1] + plane[2] * point[2] - plane[3] >= 0:
            return True
        return False

    @staticmethod
    def _intercepts_int(plane):
        x = 0 if not plane[0] else int(plane[3] / plane[0] + 0.5)
        y = 0 if not plane[1] else int(plane[3] / plane[1] + 0.5)
        z = 0 if not plane[2] else int(plane[3] / plane[2] + 0.5)
        return x, y, z

    @staticmethod
    def _intercepts(plane):
        x = 0 if not plane[0] else plane[3] / plane[0]
        y = 0 if not plane[1] else plane[3] / plane[1]
        z = 0 if not plane[2] else plane[3] / plane[2]
        return x, y, z

    @staticmethod
    def _distance(point, plane):
        if not plane[0] and not plane[1] and not plane[2]:
            return 1
        return abs(plane[0] * point[0] + plane[1] * point[1] + plane[2] * point[2] - plane[3]) / \
            m.sqrt(abs(plane[0] ** 2 + plane[1] ** 2 + plane[2] ** 2))

    # preliminary checks
    @staticmethod
    @jit(nopython=True)
    def _plane(plane, distance, resolution):
        margin = (abs(plane[3]) / distance) / 2
        result = set()
        for x in range(resolution):
            var0 = x * plane[0]
            for y in range(resolution):
                var1 = var0 + y * plane[1]
                for z in range(resolution):
                    if -margin <= var1 + z * plane[2] - plane[3] < margin:
                        result.add((x, y, z))
        return result

    @staticmethod
    @jit(nopython=True)
    def _outside(plane, resolution):
        outside = set()
        for x in range(resolution):
            var0 = x * plane[0]
            for y in range(resolution):
                var1 = var0 + y * plane[1]
                for z in range(resolution):
                    if var1 + z * plane[2] - plane[3] < 0:
                        outside.add((x, y, z))
        return outside

    @staticmethod
    def _time_log_init():
        main.tl.class_list.append(len(str(__class__).split('.')[-1][:-2]))
        main.tl.method_list.append(len(max([a for a in dir(StructureDefiner)
                                            if callable(getattr(StructureDefiner, a))
                                            and not a.startswith('_')], key=len)))
        main.tl.set_length()


if __name__ == '__main__':
    print('Running structure_definer...')
