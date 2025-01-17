# figure_updater by Oliver Rice


import main
import numpy as np
import base64
import os
import pickle
import copy
from numba import jit
from plotly import graph_objs as go
# from meshlib import mrmeshpy as mm
# from meshlib import mrmeshnumpy as mn
from dash import html


class FigureUpdater:
    @main.tl.log_time_spacer
    def __init__(self):
        self._time_log_init()
        self.figure_key = None
        self.figure_loaded = False
        self.update_form_display = False
        self.form = None
        self.faces_updated = False
        self.transform_point_cloud = None
        self.transform_point_cloud_dict = {
            'hologram': [],
            'hologram-array': None,
            'hologram-markers': (0.5, 'rgb(40,40,40)'),
            'faces': [],
            'face-markers': (2, 'full_spectrum'),
            'background-color': '#F7F7F7'
        }
        self.structure_point_cloud = None
        self.structure_point_cloud_dict = {
            'hologram': [],
            'hologram-array': None,
            'hologram-markers': (0.5, 'rgb(40,40,40)'),
            'faces': [],
            'face-markers': (2, 'full_spectrum'),
            'background-color': '#F7F7F7'
        }
        self.mesh = None
        self.mesh_dict = {
            
        }
        self.state_default = {
            'transforms': {
                'lock-on': False,
                'display-settings': {},
                'x-scale': 0,
                'y-scale': 0,
                'z-scale': 0,
                'xyz-scale': 0,
                'theta': 0,
                'psi': 0,
                'phi': 0,
                'cutoff-level': 0
            },
            'structure': {
                'lock-on': False,
                'faces': {}
            }
        }
        self.state = copy.deepcopy(self.state_default)
        self.state_load = copy.deepcopy(self.state_default)
        self.history = [copy.deepcopy(self.state_default)]
        self.history_pos = -1
        self.figure_loaded = False
        self.figure_state_saves_default = {
            '000': None,
            '001': None,
            '010': None,
            '011': None,
            '100': None,
            '101': None,
            '110': None,
            '111': None,
        }
        self.figure_state_saves = None
        self.structure_information = \
            [eval(
                '''\
                html.Tr(
                    children=[
                        html.Th("Faces", style={"padding": "4px 15px 4px 15px",
                                                "border": "2px solid black",
                                                "border-collapse": "collapse"}),
                        html.Th("Adjacent Faces", style={"padding": "4px 15px 4px 15px",
                                                         "border": "2px solid black",
                                                         "border-collapse": "collapse"}),
                        html.Th("Population", style={"padding": "4px 15px 4px 15px",
                                                     "border": "2px solid black",
                                                     "border-collapse": "collapse"}),
                    ]
                )\
                '''
            )]
        self.transform_point_cloud_update()
        self.structure_point_cloud_update()

    @main.tl.log_time_spacer
    def update(self,
               transform_lock_on,
               x_scale, y_scale, z_scale, xyz_scale,
               theta, psi, phi,
               cutoff_level,
               structure_lock_on,
               faces,
               history_update=False
               ):

        # ----------------------------------------------------------------------------------------------- loading update
        if self.figure_loaded:
            self.figure_loaded = False

            if self.state_load != self.state_default:

                print('!')

                if (self.state.get('transforms').get('lock-on') !=
                        self.state_load.get('transforms').get('lock-on')):
                    self.state.get('transforms').update(
                        {'lock-on': self.state_load.get('transforms').get('lock-on')})
                    self.update_form_display = True

                self.state.get('structure').update({'faces': self.state_load.get('structure').get('faces')})
                self.update_structure_information()
                self.update_manager(
                    category='transforms',
                    terms=(('x-scale', 'y-scale', 'z-scale', 'xyz-scale'),
                           ('theta', 'psi', 'phi'),
                           'cutoff-level'),
                    values=((self.state_load.get('transforms').get('x-scale'),
                             self.state_load.get('transforms').get('y-scale'),
                             self.state_load.get('transforms').get('z-scale'),
                             self.state_load.get('transforms').get('xyz-scale')),
                            (self.state_load.get('transforms').get('theta'),
                             self.state_load.get('transforms').get('psi'),
                             self.state_load.get('transforms').get('phi')),
                            self.state_load.get('transforms').get('cutoff-level')),
                    fns=('main.tf.cartesian_transform',
                         'main.tf.rotate',
                         'main.tf.cutoff')
                )

                self.state_load = copy.deepcopy(self.state_default)

                if self.update_form_display:
                    self.update_form_display = False

                    if self.state.get('transforms').get('lock-on'):
                        self.transform_point_cloud_dict.update({'hologram-array': main.tf.hollow(self.form, 5)})

                    else:
                        self.transform_point_cloud_dict.update({'hologram-array': main.tf.hollow(self.form, 5)})

                self.history.append(copy.deepcopy(self.state))

            else:

                self.transform_point_cloud_dict.update({'hologram-array': main.tf.hollow(self.form, 5)})

            self.transform_point_cloud_update_faces(faces)
            self.transform_point_cloud_update_form()
            self.transform_point_cloud_update()

        # ---------------------------------------------------------------------------------------------- standard update
        elif self.form is not None:

            self.state.get('transforms').update({'lock-on': transform_lock_on})

            if transform_lock_on:

                if self.update_form_display:
                    self.update_form_display = False
                    self.transform_point_cloud_dict.update({'hologram-array': main.tf.hollow(self.form, 5)})

                if self.faces_updated:
                    self.faces_updated = False
                    self.state.update({'structure': {'faces': faces}})
                    self.transform_point_cloud_update_faces(faces)
                    self.transform_point_cloud_update()
                elif history_update:
                    self.transform_point_cloud_update_faces(faces)
                    self.transform_point_cloud_update()

            else:

                self.update_manager(
                    category='transforms',
                    terms=(('x-scale', 'y-scale', 'z-scale', 'xyz-scale'),
                           ('theta', 'psi', 'phi'),
                           'cutoff-level'),
                    values=((x_scale, y_scale, z_scale, xyz_scale),
                            (theta, psi, phi),
                            cutoff_level),
                    fns=('main.tf.cartesian_transform',
                         'main.tf.rotate',
                         'main.tf.cutoff')
                )
                self.transform_point_cloud_dict.update({'faces': []})

                if self.update_form_display:
                    self.update_form_display = False
                    self.transform_point_cloud_dict.update({'hologram-array': main.tf.hollow(self.form, 5)})
                    self.transform_point_cloud_update_form()

                self.transform_point_cloud_update()

            self.update_structure_information()

            if not history_update:
                if self.history_pos < -1:
                    self.history = self.history[:self.history_pos + 1]
                    self.history_pos = -1
                if self.state != self.history[-1]:
                    self.history.append(copy.deepcopy(self.state))

    @main.tl.log_time
    def load(self, figure_key):
        try:
            self.figure_key = base64.b64decode(figure_key.split(',')[1]).decode('UTF-8')
        except IndexError:
            with open(figure_key, 'r') as figure_key:
                self.figure_key = figure_key.read

        self.form = np.load('figures/save_data/' + self.figure_key + '/form.npy')
        self.form = main.tf.crop(self.form)

        if os.path.exists('figures/save_data/' + self.figure_key + '/transforms.pkl'):
            with open('figures/save_data/' + self.figure_key + '/transforms.pkl', 'rb') as f:
                self.state_load.update({'transforms': pickle.load(f)})
        if os.path.exists('figures/save_data/' + self.figure_key + '/structure.pkl'):
            with open('figures/save_data/' + self.figure_key + '/structure.pkl', 'rb') as f:
                self.state_load.update({'structure': pickle.load(f)})

        self.history = [copy.deepcopy(self.state_default)]
        self.history_pos = -1
        self.state = copy.deepcopy(self.state_default)
        self.figure_state_saves = self.figure_state_saves_default.copy()
        self.figure_state_saves.update({'000': self.form.copy()})
        self.figure_loaded = True

    @main.tl.log_time_spacer
    def save(self):
        if self.figure_key is not None:
            with open('figures/save_data/' + self.figure_key + '/transforms.pkl', 'wb') as f:
                pickle.dump(self.state.get('transforms'), f)
            with open('figures/save_data/' + self.figure_key + '/structure.pkl', 'wb') as f:
                pickle.dump(self.state.get('structure'), f)

    @main.tl.log_time_spacer
    def undo(self):
        if len(self.history) >= abs(self.history_pos) + 1:
            self.history_pos -= 1

            transform_lock_on = self.history[self.history_pos].get('transforms').get('lock-on')
            x_scale = self.history[self.history_pos].get('transforms').get('x-scale')
            y_scale = self.history[self.history_pos].get('transforms').get('y-scale')
            z_scale = self.history[self.history_pos].get('transforms').get('z-scale')
            xyz_scale = self.history[self.history_pos].get('transforms').get('xyz-scale')
            theta = self.history[self.history_pos].get('transforms').get('theta')
            psi = self.history[self.history_pos].get('transforms').get('psi')
            phi = self.history[self.history_pos].get('transforms').get('phi')
            cutoff_level = self.history[self.history_pos].get('transforms').get('cutoff-level')

            structure_lock_on = self.history[self.history_pos].get('structure').get('lock-on')
            faces = self.history[self.history_pos].get('structure').get('faces')

            self.state.get('transforms').update({'lock-on': transform_lock_on})
            self.state.get('structure').update({'lock-on': structure_lock_on})
            self.state.get('structure').update({'faces': faces})
            self.transform_point_cloud_dict.update({'faces': []})

            self.update(
                transform_lock_on,
                x_scale, y_scale, z_scale, xyz_scale,
                theta, psi, phi,
                cutoff_level,
                structure_lock_on,
                faces,
                history_update=True
            )

    @main.tl.log_time_spacer
    def redo(self):
        if self.history_pos < -1:
            self.history_pos += 1
            transform_lock_on = self.history[self.history_pos].get('transforms').get('lock-on')
            x_scale = self.history[self.history_pos].get('transforms').get('x-scale')
            y_scale = self.history[self.history_pos].get('transforms').get('y-scale')
            z_scale = self.history[self.history_pos].get('transforms').get('z-scale')
            xyz_scale = self.history[self.history_pos].get('transforms').get('xyz-scale')
            theta = self.history[self.history_pos].get('transforms').get('theta')
            psi = self.history[self.history_pos].get('transforms').get('psi')
            phi = self.history[self.history_pos].get('transforms').get('phi')
            cutoff_level = self.history[self.history_pos].get('transforms').get('cutoff-level')
            structure_lock_on = self.history[self.history_pos].get('structure').get('lock-on')
            faces = self.history[self.history_pos].get('structure').get('faces')
            self.state.update({'structure': {'faces': faces}})
            self.transform_point_cloud_dict.update({'faces': []})

            self.update(
                transform_lock_on,
                x_scale, y_scale, z_scale, xyz_scale,
                theta, psi, phi,
                cutoff_level,
                structure_lock_on,
                faces,
                history_update=True
            )

    @main.tl.log_time
    def update_manager(self, category, terms, values, fns, level=0, changes=None):
        def recursive_fn(r_terms, r_values, r_fns, r_level, r_changes):
            if r_changes is None:
                r_changes = []
            if r_level == len(r_terms):
                if 'default changed' in r_changes or 'changed' in r_changes:
                    main.tf.value_translate(self.state)
                    figure_code = []
                    update_code = []
                    for i in range(r_level):
                        if r_changes[i] == 'unchanged':
                            figure_code.append(1)
                            if 'default changed' in r_changes[:i + 1]:
                                update_code.append(1)
                            else:
                                update_code.append(2)
                        elif r_changes[i] == 'changed':
                            figure_code.append(0)
                            update_code.append(1)
                        elif r_changes[i] == 'default changed':
                            figure_code.append(0)
                            update_code.append(0)
                            for key in self.figure_state_saves.keys():
                                if int(list(key)[i]):
                                    self.figure_state_saves.update({key: None})
                        else:
                            figure_code.append(0)
                            update_code.append(0)
                    update_mod = False
                    for i in range(r_level):
                        if update_code[i] == 2:
                            if update_mod:
                                update_code[i] = 1
                            else:
                                update_code[i] = 0
                        if update_code[i] == 1:
                            update_mod = True
                    load_code = []
                    i = 0
                    while i < len(r_terms) and figure_code[i]:
                        load_code.append(1)
                        i += 1
                    load_code = load_code + [0] * (r_level - len(load_code))
                    for i in range(len(r_terms)):
                        if figure_code[i] and not load_code[i]:
                            update_code[i] = 1
                    load_string = ''.join(str(a) for a in load_code)
                    self.form = self.figure_state_saves.get(load_string).copy()
                    save_code = load_code.copy()
                    strings = [load_string]
                    for i in range(r_level):
                        if update_code[i]:
                            self.form = eval(r_fns[i] + '(self.form)')
                            save_code[i] = 1
                            save_string = ''.join(str(a) for a in save_code)
                            strings.append(save_string)
                            self.figure_state_saves.update({save_string: self.form.copy()})
                    self.update_form_display = True
                    # end
            else:
                zero = True
                try:
                    for value in r_values[r_level]:
                        if value != 0:
                            zero = False
                except TypeError:
                    if r_values[r_level] != 0:
                        zero = False
                changed = False
                try:
                    if isinstance(r_terms[r_level], str):
                        if r_values[r_level] != self.state.get(category).get(r_terms[r_level]):
                            changed = True
                    else:
                        for term, value in zip(r_terms[r_level], r_values[r_level]):
                            if value != self.state.get(category).get(term):
                                changed = True
                except TypeError:
                    if r_values[r_level] != self.state.get(category).get(r_terms[r_level]):
                        changed = True
                if zero and changed:
                    try:
                        if isinstance(r_terms[r_level], str):
                            self.state.get(category).update({r_terms[r_level]: 0})
                        else:
                            for term in r_terms[r_level]:
                                self.state.get(category).update({term: 0})
                    except TypeError:
                        self.state.get(category).update({r_terms[r_level]: 0})
                    r_level += 1
                    r_changes.append('default changed')
                    recursive_fn(r_terms, r_values, r_fns, r_level, r_changes)
                elif zero and not changed:
                    r_level += 1
                    r_changes.append('default unchanged')
                    recursive_fn(r_terms, r_values, r_fns, r_level, r_changes)
                elif changed:
                    try:
                        if isinstance(r_terms[r_level], str):
                            self.state.get(category).update({r_terms[r_level]: r_values[r_level]})
                        else:
                            for term, value in zip(r_terms[r_level], r_values[r_level]):
                                self.state.get(category).update({term: value})
                    except TypeError:
                        self.state.get(category).update({r_terms[r_level]: r_values[r_level]})
                    r_level += 1
                    r_changes.append('changed')
                    recursive_fn(r_terms, r_values, r_fns, r_level, r_changes)
                else:
                    r_level += 1
                    r_changes.append('unchanged')
                    recursive_fn(r_terms, r_values, r_fns, r_level, r_changes)
        recursive_fn(terms, values, fns, level, changes)

    @staticmethod
    @main.tl.log_time
    @jit(nopython=True)
    def construct_plane_hologram(shape, plane, distance, restrictions=None):
        if distance:
            p = abs(plane[3]) / distance / 4
        else:
            p = 1
        on_plane = np.zeros(shape, dtype=np.bool_)
        for x in range(shape[0]):
            v0 = x * plane[0]
            for y in range(shape[1]):
                v1 = y * plane[1]
                for z in range(shape[2]):
                    if -p <= v0 + v1 + z * plane[2] - plane[3] <= p:
                        on_plane[x, y, z] = True
                        if restrictions is not None:
                            for restriction in restrictions:
                                if x * restriction[0] + \
                                   y * restriction[1] + \
                                   z * restriction[2] - restriction[3] < 0:
                                    on_plane[x, y, z] = False
        return on_plane

    # possibly redundant
    @main.tl.log_time
    def transform_point_cloud_update_form(self):
        if self.transform_point_cloud_dict.get('hologram-array') is None:
            x = y = z = []
        else:
            x, y, z = self.transform_point_cloud_dict.get('hologram-array').nonzero()
        # noinspection PyTypeChecker
        self.transform_point_cloud_dict.update({'hologram': [go.Scatter3d(x=x, y=y, z=z, mode='markers', name='hologram',
                                     marker=dict(size=self.transform_point_cloud_dict.get('hologram-markers')[0],
                                                 color=self.transform_point_cloud_dict.get('hologram-markers')[1]))]})

    @main.tl.log_time
    def transform_point_cloud_update_faces(self, faces):
        self.transform_point_cloud_dict.update({'faces': []})
        planes = [value.get('plane_equation')
                  for value in faces.values() if value.get('initialised_plane')]
        for i, (key, value) in enumerate(faces.items()):
            if value.get('initialised_plane'):
                plane = value.get('plane_equation')
                restrictions = tuple([x for x in planes if x[0] != plane])
                if not restrictions:
                    restrictions = None
                x, y, z = self.construct_plane_hologram(
                    self.form.shape, plane, value.get('distance'), restrictions).nonzero()
                self.transform_point_cloud_dict.get('faces').append(
                    go.Scatter3d(x=x, y=y, z=z, mode='markers', name=key, marker=dict(
                        size=self.transform_point_cloud_dict.get('face-markers')[0], color=value.get('color'))))

    @main.tl.log_time
    def transform_point_cloud_update(self):
        # noinspection PyTypeChecker
        layout = go.Layout(scene_aspectmode='data',
                           paper_bgcolor=self.transform_point_cloud_dict.get('background-color'),
                           showlegend=False)
        flat_lst = []
        for elem in self.transform_point_cloud_dict.get('hologram'):
            flat_lst.append(elem)
        for elem in self.transform_point_cloud_dict.get('faces'):
            flat_lst.append(elem)
        self.transform_point_cloud = go.Figure(data=flat_lst, layout=layout)

    @main.tl.log_time
    def structure_point_cloud_update(self):
        # noinspection PyTypeChecker
        layout = go.Layout(scene_aspectmode='data',
                           paper_bgcolor=self.structure_point_cloud_dict.get('background-color'),
                           showlegend=False)
        flat_lst = []
        for elem in self.structure_point_cloud_dict.get('hologram'):
            flat_lst.append(elem)
        for elem in self.structure_point_cloud_dict.get('faces'):
            flat_lst.append(elem)
        self.structure_point_cloud = go.Figure(data=flat_lst, layout=layout)

    @main.tl.log_time
    def update_structure_information(self):
        self.structure_information = [eval(
            '''\
            html.Tr(
                children=[
                    html.Th("Faces", style={"padding": "4px 15px 4px 15px",
                                            "border": "2px solid black",
                                            "border-collapse": "collapse"}),
                    html.Th("Adjacent Faces", style={"padding": "4px 15px 4px 15px",
                                                     "border": "2px solid black",
                                                     "border-collapse": "collapse"}),
                    html.Th("Population", style={"padding": "4px 15px 4px 15px",
                                                 "border": "2px solid black",
                                                 "border-collapse": "collapse"})
                ]
            )\
            '''
        )]

        for key0, value in self.state.get('structure').get('faces').items():
            if self.state.get('structure').get('faces').get(key0).get('initialised_plane'):
                string = ''.join('html.Label(children=["' + key1 + '"], ' +
                                 f'style=\u007b"color": "{self.state.get("structure").get("faces").get(key1).get("color")}"\u007d),' +
                                 'html.Br(),'
                                 for key1 in self.state.get('structure').get('faces').get(key0).get('adjacent_faces'))
                if string == '':
                    string = 'html.Label("N/A")'
                if self.state.get('structure').get('faces').get(key0).get('size') is None:
                    size = 'N/A'
                else:
                    size = self.state.get('structure').get('faces').get(key0).get('size')
                self.structure_information.append(
                    eval(
                        f'''\
                        html.Tr(
                            children=[
                                html.Td(html.Label("{key0}", style=\u007b"color": "{value.get('color')}"\u007d),
                                    style=\u007b"padding": "4px 15px 4px 15px",
                                                "border": "1px dotted black",
                                                "border-collapse": "collapse"\u007d),
                                html.Td(
                                    html.Label(
                                        children=[
                        {string}
                                        ],
                                    ),
                                    style=\u007b"padding": "4px 15px 4px 15px",
                                                "border": "1px dotted black",
                                                "border-collapse": "collapse"\u007d
                                ),
                                html.Td(html.Label("{size}"),
                                    style=\u007b"padding": "4px 15px 4px 15px",
                                                "border": "1px dotted black",
                                                "border-collapse": "collapse"\u007d
                                )
                            ],
                        )\
                        '''
                    )
                )

    @staticmethod
    def _time_log_init():
        main.tl.class_list.append(len(str(__class__).split('.')[-1][:-2]))
        main.tl.method_list.append(len(max([a for a in dir(FigureUpdater)
                                            if callable(getattr(FigureUpdater, a))
                                            and not a.startswith('_')], key=len)))
        main.tl.set_length()


if __name__ == '__main__':
    print('Running figure_state_updater...')
