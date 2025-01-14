# ec0rypt by Oliver Rice


import copy


polyhedralise_flip = False
face_add_flip = False
face_delete_flip = False
save_flip = False
torus_flip = False
sphere_flip = False
cube_flip = False
update_flip = False
undo_flip = False
redo_flip = False


def main():
    from figure_updater import FigureUpdater
    from structure_definer import StructureDefiner
    from segmentation import Segmentation
    from dash import Dash, dcc, html, ctx, callback
    from dash.dependencies import Input, State, Output
    import dash_daq as daq

    fs = FigureUpdater()
    sd = StructureDefiner()
    se = Segmentation()

    point_cloud = fs.point_cloud

    app = Dash(__name__)

    app.layout = html.Div(
        children=[


            # /////////////////////////////////////////////////////////////////////////////////////////////////// HEADER
            html.Div(
                children=[html.H1(children='ec0rypt', className='header-title')],
                className='header'
            ),
            html.Div(
                className='h24 black_1',
            ),


            # ///////////////////////////////////////////////////////////////////////////////////////////////////// MESH

            # ----------------------------------------------------------------------------------------- collapse control
            html.Div(
                children=[
                    dcc.Checklist(
                        [{'label': 'Mesh', 'value': 'show'}],
                        [],
                        className='checklist',
                        labelClassName='checklist_label',
                        id='toggle-mesh'
                    )
                ],
                className='section_gray_0'
            ),

            # ----------------------------------------------------------------------------------------------------- body

            html.Div(
                children=[
                    # ---------------------------------------------------------------- display settings collapse control
                    html.Div(
                        children=[
                            dcc.Checklist(
                                [{'label': 'Display Settings', 'value': 'show'}],
                                [],
                                className='checklist',
                                labelClassName='checklist_label',
                                id='toggle-mesh-display-settings'
                            )
                        ],
                        className='section_gray_1'
                    ),
                    html.Div(
                        children=[

                        ],
                        className='h12 gray_1',
                        id='mesh-display-settings-body'
                    )
                ],
                id='mesh-body'
            ),


            # /////////////////////////////////////////////////////////////////////////////////////// TRANSFORM CONTROLS

            # ----------------------------------------------------------------------------------------- collapse control
            html.Div(
                children=[
                    dcc.Checklist(
                        [{'label': 'Transform Controls', 'value': 'show'}],
                        ['show'],
                        className='checklist',
                        labelClassName='checklist_label',
                        id='toggle-transform-controls'
                    )
                ],
                className='section_gray_0'
            ),

            # ----------------------------------------------------------------------------------------------------- body
            html.Div(
                children=[

                    # -------------------------------------------------------------------------------------- point cloud
                    dcc.Graph(
                        figure=point_cloud,
                        id='point-cloud',
                        style={
                            'title': 'Point_Cloud',
                            'width': '100%',
                            'height': '60vh',
                            'background-color': '#EBEBEB'
                        },
                    ),

                    # ---------------------------------------------------- point cloud display settings collapse control
                    html.Div(
                        children=[
                            dcc.Checklist(
                                [{'label': 'Display Settings', 'value': 'show'}],
                                [],
                                className='checklist',
                                labelClassName='checklist_label',
                                id='toggle-point-cloud-display-settings'
                            )
                        ],
                        className='section_gray_1'
                    ),

                    # ----------------------------------------------------------------------------------- transform lock
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Div(style={'height': '13px'}),
                                    daq.BooleanSwitch(
                                        on=False,
                                        label='Lock',
                                        color='#FF0000',
                                        id='transform-lock'
                                    ),
                                    html.Div(style={'height': '14px'})
                                ],
                                className='flex_1'
                            ),
                        ],
                        className='flex_row p12 center'
                    ),

                    # --------------------------------------------------------------------- point cloud display settings
                    html.Div(
                        children=[
                            html.Div(className='h12 gray_1')
                        ],
                        id='point-cloud-display-settings-body',
                    ),

                    # -------------------------------------------------------------------------- cartesian scale sliders
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.P(children='X Scale', className='text_center f24'),
                                    dcc.Slider(
                                        min=-1,
                                        max=1,
                                        step=0.05,
                                        value=0,
                                        included=False,
                                        marks={i / 20 - 1: "|" for i in range(41)},
                                        id='x-slider'
                                    ),
                                ],
                                className='flex_1'
                            ),
                            html.Div(
                                children=[
                                    html.P(children='Y Scale', className='text_center f24'),
                                    dcc.Slider(
                                        min=-1,
                                        max=1,
                                        step=0.05,
                                        value=0,
                                        included=False,
                                        marks={i / 20 - 1: "|" for i in range(41)},
                                        id='y-slider'
                                    ),
                                ],
                                className='flex_1'
                            ),
                            html.Div(
                                children=[
                                    html.P(children='Z Scale', className='text_center f24'),
                                    dcc.Slider(
                                        min=-1,
                                        max=1,
                                        step=0.05,
                                        value=0,
                                        included=False,
                                        marks={i / 20 - 1: "|" for i in range(41)},
                                        id='z-slider'
                                    ),
                                ],
                                className='flex_1'
                            ),
                            html.Div(
                                children=[
                                    html.P(children='Overall Scale', className='text_center f24'),
                                    dcc.Slider(
                                        min=-1,
                                        max=1,
                                        step=0.05,
                                        value=0,
                                        included=False,
                                        marks={i / 20 - 1: "|" for i in range(41)},
                                        id='xyz-slider'
                                    ),
                                ],
                                className='flex_1'
                            )
                        ],
                        className='flex_row p12 center',
                    ),
                    html.Div(className='h12 gray_1'),

                    # --------------------------------------------------------------------------- euler rotation sliders
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.P(children='Yaw', className='text_center f24'),
                                    dcc.Slider(
                                        min=-180,
                                        max=180,
                                        step=5,
                                        value=0,
                                        included=False,
                                        marks={i * 5 - 180: "|" for i in range(73)},
                                        id='yaw-slider'
                                    )
                                ],
                                className='flex_1'
                            ),
                            html.Div(
                                children=[
                                    html.P(children='Pitch', className='text_center f24'),
                                    dcc.Slider(
                                        min=-180,
                                        max=180,
                                        step=5,
                                        value=0,
                                        included=False,
                                        marks={i * 5 - 180: "|" for i in range(73)},
                                        id='pitch-slider'
                                    )
                                ],
                                className='flex_1'
                            ),
                            html.Div(
                                children=[
                                    html.P(children='Roll', className='text_center f24'),
                                    dcc.Slider(
                                        min=-180,
                                        max=180,
                                        step=5,
                                        value=0,
                                        included=False,
                                        marks={i * 5 - 180: "|" for i in range(73)},
                                        id='roll-slider'
                                    )
                                ],
                                className='flex_1'
                            )
                        ],
                        className='flex_row p12 center',
                    ),
                    html.Div(className='h12 gray_1'),

                    # ------------------------------------------------------------------------------ cutoff level slider
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.P(children='Cutoff Level', className='text_center f24'),
                                    dcc.Slider(
                                        min=0,
                                        max=100,
                                        step=5,
                                        value=0,
                                        included=True,
                                        id='cutoff-level-slider'
                                    )
                                ],
                                className='flex_1'
                            )
                        ],
                        className='flex_row p12 center',
                    ),
                ],
                id='transform-controls-body'
            ),


            # /////////////////////////////////////////////////////////////////////////////////////// STRUCTURE CONTROLS

            # ----------------------------------------------------------------------------------------- collapse control
            html.Div(
                children=[
                    dcc.Checklist(
                        [{'label': 'Structure Controls', 'value': 'show'}],
                        [],
                        className='checklist',
                        labelClassName='checklist_label',
                        id='toggle-structure-controls'
                    )
                ],
                className='section_gray_0'
            ),

            # ----------------------------------------------------------------------------------------------------- body

            html.Div(
                children=[

                    # --------------------------------------------------------------------- information collapse control
                    html.Div(
                        children=[
                            dcc.Checklist(
                                [{'label': 'Structure Information', 'value': 'show'}],
                                [],
                                className='checklist',
                                labelClassName='checklist_label',
                                id='toggle-structure-information'
                            )
                        ],
                        className='section_gray_1'
                    ),

                    # ----------------------------------------------------------------------------------- structure lock
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Div(style={'height': '13px'}),
                                    daq.BooleanSwitch(
                                        on=False,
                                        label='Lock',
                                        color='#FF0000',
                                        id='structure-lock'
                                    ),
                                    html.Div(style={'height': '14px'})
                                ],
                                className='flex_1'
                            ),
                        ],
                        className='flex_row p12 center'
                    ),

                    # --------------------------------------------------------------------------------- information body
                    html.Div(
                        children=[
                            html.Div(className='h12'),
                            html.Div(
                                children=[
                                    html.Div(html.Table(id='structure-information-faces'))
                                ],
                                className='flex_row ml12'
                            )
                        ],
                        className='gray_1',
                        id='structure-information-body'
                    ),

                    # ------------------------------------------------------------------------------------ face controls
                    html.Div(
                        children=[
                            html.Button(
                                html.P('Polyhedralise'),
                                n_clicks=0,
                                className='button_gray_0 f18',
                                style={'width': '224px'},
                                id='polyhedralise-button'
                            ),
                            html.Button(
                                html.P('Add Face'),
                                n_clicks=0,
                                className='button_gray_0 f18',
                                style={'width': '224px'},
                                id='face-add-button'
                            ),
                            html.Button(
                                html.P('Delete Face'),
                                n_clicks=0,
                                className='button_gray_0 f18',
                                style={'width': '224px'},
                                id='face-delete-button'
                            ),
                        ],
                        className='flex_row p12 center'
                    ),
                ],
                id='structure-controls-body'
            ),


            # //////////////////////////////////////////////////////////////////////////////////// SEGMENTATION CONTROLS

            # ----------------------------------------------------------------------------------------- collapse control
            html.Div(
                children=[
                    dcc.Checklist(
                        [{'label': 'Segmentation Controls', 'value': 'show'}],
                        [],
                        className='checklist',
                        labelClassName='checklist_label',
                        id='toggle-segmentation-controls'
                    )
                ],
                className='section_gray_0'
            ),

            # ----------------------------------------------------------------------------------------------------- body
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.P(children='Width', className='text_center f24'),
                                    dcc.Slider(
                                        min=1,
                                        max=64,
                                        step=1,
                                        value=8,
                                        included=False,
                                        marks={i + 1: "|" for i in range(64)},
                                        id='segment-width'
                                    ),
                                ],
                                className='flex_1'
                            )
                        ],
                        className='flex_row p12 center',
                    )
                ],
                id='segmentation-controls-body'
            ),


            # /////////////////////////////////////////////////////////////////////////////////////// LOAD/SAVE CONTROLS

            # ----------------------------------------------------------------------------------------- collapse control
            html.Div(
                children=[
                    dcc.Checklist(
                        [{'label': 'Load/Save', 'value': 'show'}],
                        ['show'],
                        className='checklist',
                        labelClassName='checklist_label',
                        id='toggle-load-save'
                    )
                ],
                className='section_gray_0'
            ),

            # ----------------------------------------------------------------------------------------------------- body
            html.Div(
                children=[
                    html.Div(
                        children=[
                            dcc.Upload(
                                html.P('Load Figure'),
                                className='upload_gray_0 f18',
                                style={
                                    'width': '224px',
                                    'height': '57px',
                                },
                                id='loaded-figure'
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Button(
                                html.P('Save Figure'),
                                n_clicks=0,
                                className='button_gray_0 f18',
                                style={'width': '224px'},
                                id='save-button'
                            )
                        ]
                    )
                ],
                className='flex_row p12 center',
                id='load-save-body'
            ),


            # ////////////////////////////////////////////////////////////////////////////////////////////////// PRESETS

            # ----------------------------------------------------------------------------------------- collapse control
            html.Div(
                children=[
                    dcc.Checklist(
                        [{'label': 'Presets', 'value': 'show'}],
                        [],
                        className='checklist',
                        labelClassName='checklist_label',
                        id='toggle-presets'
                    )
                ],
                className='section_gray_0'
            ),

            # ----------------------------------------------------------------------------------------------------- body

            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Button(
                                html.P('Torus'),
                                n_clicks=0,
                                className='button_gray_0 f18',
                                style={'width': '224px'},
                                id='torus-button'
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Button(
                                html.P('Sphere'),
                                n_clicks=0,
                                className='button_gray_0 f18',
                                style={'width': '224px'},
                                id='sphere-button'
                            )
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Button(
                                html.P('Cube'),
                                n_clicks=0,
                                className='button_gray_0 f18',
                                style={'width': '224px'},
                                id='cube-button'
                            )
                        ]
                    )
                ],
                className='flex_row p12 center',
                id='presets-body'
            ),


            # /////////////////////////////////////////////////////////////////////////////////////////// STATE CONTROLS

            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Button(
                                html.P(
                                    children='Update',
                                    className='f24 center'
                                ),
                                n_clicks=0,
                                className='button_blue_0 f30',
                                id='update-button'
                            ),
                            html.Div(className='h12 blue_0')
                        ],
                        className='flex_1'
                    ),
                    html.Div(
                        children=[
                            html.Button(
                                html.P(
                                    children='Undo',
                                    className='f24 center'
                                ),
                                n_clicks=0,
                                className='button_blue_0 f30',
                                id='undo-button'
                            ),
                            html.Div(className='h12 blue_0')
                        ],
                        className='flex_1'
                    ),
                    html.Div(
                        children=[
                            html.Button(
                                html.P(
                                    children='Redo',
                                    className='f24 center'
                                ),
                                n_clicks=0,
                                className='button_blue_0 f30',
                                id='redo-button'
                            ),
                            html.Div(className='h12 blue_0')
                        ],
                        className='flex_1'
                    )
                ],
                className='state_controls'
            ),
            html.Div(style={'height': '76px'}),

            html.Div(children=False, style={'display': 'none'}, id='polyhedralise-bus'),
            html.Div(children=False, style={'display': 'none'}, id='face-add-bus'),
            html.Div(children=False, style={'display': 'none'}, id='face-delete-bus'),
            html.Div(children=False, style={'display': 'none'}, id='save-bus'),
            html.Div(children=False, style={'display': 'none'}, id='torus-bus'),
            html.Div(children=False, style={'display': 'none'}, id='sphere-bus'),
            html.Div(children=False, style={'display': 'none'}, id='cube-bus'),
            html.Div(children=False, style={'display': 'none'}, id='update-bus'),
            html.Div(children=False, style={'display': 'none'}, id='undo-bus'),
            html.Div(children=False, style={'display': 'none'}, id='redo-bus'),
        ]
    )

    # ///////////////////////////////////////////////////////////////////////////////////////////////// primary callback
    if True:
        @callback(
            Output('point-cloud-display-settings-body', 'style'),
            Output('mesh-body', 'style'),
            Output('mesh-display-settings-body', 'style'),
            Output('transform-controls-body', 'style'),
            Output('structure-controls-body', 'style'),
            Output('structure-information-body', 'style'),
            Output('segmentation-controls-body', 'style'),
            Output('load-save-body', 'style'),
            Output('presets-body', 'style'),

            Output('structure-information-faces', 'children'),

            Output('point-cloud', 'figure'),
            Output('point-cloud', 'clickData'),
            Output('transform-lock', 'on'),
            Output('x-slider', 'value'),
            Output('y-slider', 'value'),
            Output('z-slider', 'value'),
            Output('xyz-slider', 'value'),
            Output('yaw-slider', 'value'),
            Output('pitch-slider', 'value'),
            Output('roll-slider', 'value'),
            Output('cutoff-level-slider', 'value'),
            Output('loaded-figure', 'contents'),

            Output('toggle-point-cloud-display-settings', 'options', allow_duplicate=True),
            Output('toggle-mesh', 'options', allow_duplicate=True),
            Output('toggle-mesh-display-settings', 'options', allow_duplicate=True),
            Output('toggle-transform-controls', 'options', allow_duplicate=True),
            Output('toggle-structure-controls', 'options', allow_duplicate=True),
            Output('toggle-segmentation-controls', 'options', allow_duplicate=True),
            Output('toggle-load-save', 'options', allow_duplicate=True),
            Output('toggle-presets', 'options', allow_duplicate=True),

            Output('transform-lock', 'disabled', allow_duplicate=True),
            Output('x-slider', 'disabled', allow_duplicate=True),
            Output('y-slider', 'disabled', allow_duplicate=True),
            Output('z-slider', 'disabled', allow_duplicate=True),
            Output('xyz-slider', 'disabled', allow_duplicate=True),
            Output('yaw-slider', 'disabled', allow_duplicate=True),
            Output('pitch-slider', 'disabled', allow_duplicate=True),
            Output('roll-slider', 'disabled', allow_duplicate=True),
            Output('cutoff-level-slider', 'disabled', allow_duplicate=True),
            Output('structure-lock', 'disabled', allow_duplicate=True),
            Output('polyhedralise-button', 'disabled', allow_duplicate=True),
            Output('face-add-button', 'disabled', allow_duplicate=True),
            Output('face-delete-button', 'disabled', allow_duplicate=True),
            Output('loaded-figure', 'disabled', allow_duplicate=True),
            Output('save-button', 'disabled', allow_duplicate=True),
            Output('torus-button', 'disabled', allow_duplicate=True),
            Output('sphere-button', 'disabled', allow_duplicate=True),
            Output('cube-button', 'disabled', allow_duplicate=True),
            Output('update-button', 'disabled', allow_duplicate=True),
            Output('undo-button', 'disabled', allow_duplicate=True),
            Output('redo-button', 'disabled', allow_duplicate=True),

            Output('point-cloud', 'clickData', allow_duplicate=True),

            State('transform-lock', 'on'),
            State('x-slider', 'value'),
            State('y-slider', 'value'),
            State('z-slider', 'value'),
            State('xyz-slider', 'value'),
            State('yaw-slider', 'value'),
            State('pitch-slider', 'value'),
            State('roll-slider', 'value'),
            State('cutoff-level-slider', 'value'),
            State('structure-lock', 'on'),
            State('segment-width', 'value'),
            State('loaded-figure', 'contents'),

            Input('toggle-point-cloud-display-settings', 'value'),
            Input('toggle-mesh', 'value'),
            Input('toggle-mesh-display-settings', 'value'),
            Input('toggle-transform-controls', 'value'),
            Input('toggle-structure-controls', 'value'),
            Input('toggle-structure-information', 'value'),
            Input('toggle-segmentation-controls', 'value'),
            Input('toggle-load-save', 'value'),
            Input('toggle-presets', 'value'),

            Input('point-cloud', 'clickData'),

            Input('polyhedralise-bus', 'children'),
            Input('face-add-bus', 'children'),
            Input('face-delete-bus', 'children'),
            Input('save-bus', 'children'),
            Input('torus-bus', 'children'),
            Input('sphere-bus', 'children'),
            Input('cube-bus', 'children'),
            Input('update-bus', 'children'),
            Input('undo-bus', 'children'),
            Input('redo-bus', 'children'),
            config_prevent_initial_callbacks=True
        )
        def callback_0(
                transform_lock_on,
                x_value, y_value, z_value, xyz_value,
                theta_value, psi_value, phi_value,
                cutoff_level_value,

                structure_lock_on,

                segment_width,

                figure_key,

                toggle_point_cloud_display_settings,
                toggle_mesh,
                toggle_mesh_display_settings,
                toggle_transform_controls,
                toggle_structure_controls, toggle_structure_information,
                toggle_segmentation_controls,
                toggle_load_save,
                toggle_presets,

                clickdata,

                polyhedralise_bus, face_add_bus, face_delete_bus,
                save_bus,
                torus_bus, sphere_bus, cube_bus,
                update_bus, undo_bus, redo_bus
        ):

            # ------------------------------------------------------------------------------------------ display toggles
            if True:
                if toggle_point_cloud_display_settings == ['show']:
                    point_cloud_display_settings_style = {'display': ''}
                else:
                    point_cloud_display_settings_style = {'display': 'none'}
                if toggle_mesh == ['show']:
                    mesh_style = {'display': ''}
                else:
                    mesh_style = {'display': 'none'}
                if toggle_mesh_display_settings == ['show']:
                    mesh_display_settings_style = {'display': ''}
                else:
                    mesh_display_settings_style = {'display': 'none'}
                if toggle_transform_controls == ['show']:
                    transform_controls_style = {'display': ''}
                else:
                    transform_controls_style = {'display': 'none'}
                if toggle_structure_controls == ['show']:
                    structure_controls_style = {'display': ''}
                else:
                    structure_controls_style = {'display': 'none'}
                if toggle_structure_information == ['show']:
                    structure_information_style = {'display': ''}
                else:
                    structure_information_style = {'display': 'none'}
                if toggle_segmentation_controls == ['show']:
                    segmentation_controls_style = {'display': ''}
                else:
                    segmentation_controls_style = {'display': 'none'}
                if toggle_load_save == ['show']:
                    load_save_style = {'display': ''}
                else:
                    load_save_style = {'display': 'none'}
                if toggle_presets == ['show']:
                    presets_style = {'display': ''}
                else:
                    presets_style = {'display': 'none'}

            # ---------------------------------------------------------------------------------------- structure updates
            if True:
                if transform_lock_on:
                    if sd.face_add:
                        sd.add_face(clickdata)
                    if face_delete_bus or sd.face_delete:
                        sd.delete_face(clickdata)
                else:
                    sd.face_add = False
                    sd.face_delete = False

                if sd.faces_updated:
                    fs.faces_updated = True

            # ---------------------------------------------------------------------------------------- structure buttons
            if True:
                global polyhedralise_flip
                if polyhedralise_flip is not polyhedralise_bus:
                    polyhedralise_flip = polyhedralise_bus
                    # sd.polyhedralise(fs.point_cloud_dict.get('hologram'))
                    sd.form_sample(fs.point_cloud_dict.get('hologram'))

                global face_add_flip
                if face_add_flip is not face_add_bus:
                    face_add_flip = face_add_bus
                    if not sd.face_add:
                        sd.face_add = True
                elif not transform_lock_on:
                    sd.face_add = False

                global face_delete_flip
                if face_delete_flip is not face_delete_bus:
                    face_delete_flip = face_delete_bus
                    if not sd.face_delete:
                        sd.face_delete = True
                elif not transform_lock_on:
                    sd.face_delete = False

            # ------------------------------------------------------------------------------------- segmentation buttons
            if True:
                ...

            # ------------------------------------------------------------------------------------------- preset buttons
            if True:
                global torus_flip
                if torus_flip is not torus_bus:
                    torus_flip = torus_bus
                    fs.load('figures/presets_saves/torus.txt')

                global sphere_flip
                if sphere_flip is not sphere_bus:
                    sphere_flip = sphere_bus
                    fs.load('figures/presets_saves/sphere.txt')

                global cube_flip
                if cube_flip is not cube_bus:
                    cube_flip = cube_bus
                    fs.load('figures/presets_saves/cube.txt')

            # ---------------------------------------------------------------------------------------------- save button
            if True:
                global save_flip
                if save_flip is not save_bus:
                    save_flip = save_bus
                    fs.save()

            # ------------------------------------------------------------------------------------------ history buttons
            if True:
                global undo_flip
                if undo_flip is not undo_bus:
                    undo_flip = undo_bus
                    fs.undo()
                    sd.faces = fs.state.get('structure').get('faces').copy()

                global redo_flip
                if redo_flip is not redo_bus:
                    redo_flip = redo_bus
                    fs.redo()
                    sd.faces = fs.state.get('structure').get('faces').copy()

            # -------------------------------------------------------------------------------------------- update button
            if True:
                global update_flip
                if update_flip is not update_bus:
                    update_flip = update_bus

                    if transform_lock_on:
                        figure_key = None

                        # if not fs.state.get('transforms').get('lock-on'):
                        #     fs.update_form_display = True
                        #
                        #     if fs.form is not None:
                        #         sd.faces = {}
                        #         fs.state.update({'structure': {'faces': {}}})

                        if sd.face_add:
                            sd.face_add = False
                            sd.face_new = True

                            for key in [*sd.faces.keys()]:
                                if not sd.faces.get(key).get('initialised_plane'):
                                    sd.faces.pop(key)

                        if sd.face_delete:
                            sd.face_delete = False

                    else:

                        # if fs.state.get('transforms').get('lock-on'):
                        #     fs.update_form_display = True

                        # sd.shape = None
                        # sd.faces = {}
                        # fs.state.update({'structure': {'faces': {}}})

                        if figure_key is not None:
                            fs.load(figure_key)
                            sd.shape = fs.form.shape
                            figure_key = None

                            if fs.state_load.get('transforms').get('lock-on'):
                                sd.faces = fs.state_load.get('structure').get('faces').copy()
                                sd.faces_simulated = fs.state_load.get('structure').get('faces').copy()

                    fs.update(
                        transform_lock_on,
                        x_value, y_value, z_value, xyz_value,
                        theta_value, psi_value, phi_value,
                        cutoff_level_value,
                        structure_lock_on,
                        sd.faces,
                    )

                    sd.face_add = False
                    if fs.form is not None and fs.state.get('transforms').get('lock-on'):
                        sd.shape = fs.form.shape

                    # if fs.state != fs.history[-1]:
                    #     fs.history.append(copy.deepcopy(fs.state))

                print(fs.history_pos)
                print(fs.history.__len__())

            # --------------------------------------------------------------------------------------------- set ui state
            if True:
                if fs.state is not None:
                    x_scale = fs.state.get('transforms').get('x-scale')
                    y_scale = fs.state.get('transforms').get('y-scale')
                    z_scale = fs.state.get('transforms').get('z-scale')
                    scale_multiplier = fs.state.get('transforms').get('xyz-scale')
                    theta = fs.state.get('transforms').get('theta')
                    psi = fs.state.get('transforms').get('psi')
                    phi = fs.state.get('transforms').get('phi')
                    cutoff_level = fs.state.get('transforms').get('cutoff-level')
                else:
                    x_scale = 0
                    y_scale = 0
                    z_scale = 0
                    scale_multiplier = 0
                    theta = 0
                    psi = 0
                    phi = 0
                    cutoff_level = 0

            # ------------------------------------------------------------------------------------------ input disabling
            if True:
                transform_lock_disabled = False
                transforms_controls_disabled = False
                structure_lock_disabled = False
                structure_controls_disabled = False
                segmentation_lock_disabled = False
                segmentation_controls_disabled = False
                load_disabled = False
                save_disabled = False
                presets_disabled = False
                update_disabled = False
                undo_redo_disabled = False

                if fs.form is None:
                    transform_lock_disabled = True
                    structure_lock_disabled = True
                    undo_redo_disabled = True
                    transforms_controls_disabled = True
                    structure_controls_disabled = True
                    save_disabled = True
                else:
                    if fs.state.get('transforms').get('lock-on'):
                        transforms_controls_disabled = True
                        load_disabled = True
                        presets_disabled = True
                        if fs.state.get('structure').get('lock-on'):
                            transform_lock_disabled = True
                            structure_controls_disabled = True
                    else:
                        structure_lock_disabled = True
                        structure_controls_disabled = True
                    if fs.state.get('structure').get('lock-on'):
                        structure_controls_disabled = True

                if sd.face_add or sd.face_delete:
                    transform_lock_disabled = True
                    transforms_controls_disabled = True
                    structure_controls_disabled = True
                    load_disabled = True
                    save_disabled = True
                    presets_disabled = True
                    undo_redo_disabled = True

            return \
                (point_cloud_display_settings_style,
                 mesh_style,
                 mesh_display_settings_style,
                 transform_controls_style,
                 structure_controls_style, structure_information_style,
                 segmentation_controls_style,
                 load_save_style,
                 presets_style,
                 fs.structure_information,
                 fs.point_cloud, clickdata,
                 fs.state.get('transforms').get('lock-on'),
                 x_scale, y_scale, z_scale, scale_multiplier,
                 theta, psi, phi,
                 cutoff_level,
                 figure_key,
                 [{'label': 'Display Settings', 'value': 'show', 'disabled': False}],
                 [{'label': 'Mesh', 'value': 'show', 'disabled': False}],
                 [{'label': 'Display Settings', 'value': 'show', 'disabled': False}],
                 [{'label': 'Transform Controls', 'value': 'show', 'disabled': False}],
                 [{'label': 'Structure Controls', 'value': 'show', 'disabled': False}],
                 [{'label': 'Segmentation Controls', 'value': 'show', 'disabled': False}],
                 [{'label': 'Load/Save', 'value': 'show', 'disabled': False}],
                 [{'label': 'Presets', 'value': 'show', 'disabled': False}],
                 transform_lock_disabled,
                 transforms_controls_disabled, transforms_controls_disabled,
                 transforms_controls_disabled, transforms_controls_disabled,
                 transforms_controls_disabled, transforms_controls_disabled,
                 transforms_controls_disabled, transforms_controls_disabled,
                 structure_lock_disabled,
                 structure_controls_disabled, structure_controls_disabled, structure_controls_disabled,
                 load_disabled, save_disabled,
                 presets_disabled, presets_disabled, presets_disabled,
                 update_disabled, undo_redo_disabled, undo_redo_disabled,
                 None)

    # /////////////////////////////////////////////////////////////////////////////////////////////// secondary callback
    if True:
        @callback(
            Output('toggle-point-cloud-display-settings', 'options'),
            Output('toggle-mesh', 'options'),
            Output('toggle-mesh-display-settings', 'options'),
            Output('toggle-transform-controls', 'options'),
            Output('toggle-structure-controls', 'options'),
            Output('toggle-segmentation-controls', 'options'),
            Output('toggle-load-save', 'options'),
            Output('toggle-presets', 'options'),

            Output('polyhedralise-bus', 'children'),
            Output('face-add-bus', 'children'),
            Output('face-delete-bus', 'children'),
            Output('save-bus', 'children'),
            Output('torus-bus', 'children'),
            Output('sphere-bus', 'children'),
            Output('cube-bus', 'children'),
            Output('update-bus', 'children'),
            Output('undo-bus', 'children'),
            Output('redo-bus', 'children'),

            Output('transform-lock', 'disabled'),
            Output('x-slider', 'disabled'),
            Output('y-slider', 'disabled'),
            Output('z-slider', 'disabled'),
            Output('xyz-slider', 'disabled'),
            Output('yaw-slider', 'disabled'),
            Output('pitch-slider', 'disabled'),
            Output('roll-slider', 'disabled'),
            Output('cutoff-level-slider', 'disabled'),
            Output('structure-lock', 'disabled'),
            Output('polyhedralise-button', 'disabled'),
            Output('face-add-button', 'disabled'),
            Output('face-delete-button', 'disabled'),
            Output('loaded-figure', 'disabled'),
            Output('save-button', 'disabled'),
            Output('torus-button', 'disabled'),
            Output('sphere-button', 'disabled'),
            Output('cube-button', 'disabled'),
            Output('update-button', 'disabled'),
            Output('undo-button', 'disabled'),
            Output('redo-button', 'disabled'),

            Input('polyhedralise-button', 'n_clicks'),
            Input('face-add-button', 'n_clicks'),
            Input('face-delete-button', 'n_clicks'),
            Input('save-button', 'n_clicks'),
            Input('torus-button', 'n_clicks'),
            Input('sphere-button', 'n_clicks'),
            Input('cube-button', 'n_clicks'),
            Input('update-button', 'n_clicks'),
            Input('undo-button', 'n_clicks'),
            Input('redo-button', 'n_clicks'),
        )
        def callback_1(*_):
            polyhedralise_bus = polyhedralise_flip
            face_add_bus = face_add_flip
            face_delete_bus = face_delete_flip
            save_bus = save_flip
            torus_bus = torus_flip
            sphere_bus = sphere_flip
            cube_bus = cube_flip
            update_bus = update_flip
            undo_bus = undo_flip
            redo_bus = redo_flip

            # ------------------------------------------------------------------------------------------- input disabler
            if True:
                disable_inputs = False

                if 'polyhedralise-button' == ctx.triggered_id:
                    polyhedralise_bus = not polyhedralise_bus
                    disable_inputs = True
                elif 'face-add-button' == ctx.triggered_id:
                    face_add_bus = not face_add_bus
                    disable_inputs = True
                elif 'face-delete-button' == ctx.triggered_id:
                    face_delete_bus = not face_delete_bus
                    disable_inputs = True
                elif 'save-button' == ctx.triggered_id:
                    save_bus = not save_bus
                    disable_inputs = True
                elif 'torus-button' == ctx.triggered_id:
                    torus_bus = not torus_bus
                    disable_inputs = True
                elif 'sphere-button' == ctx.triggered_id:
                    sphere_bus = not sphere_bus
                    disable_inputs = True
                elif 'cube-button' == ctx.triggered_id:
                    cube_bus = not cube_bus
                    disable_inputs = True
                elif 'update-button' == ctx.triggered_id:
                    update_bus = not update_bus
                    disable_inputs = True
                elif 'undo-button' == ctx.triggered_id:
                    undo_bus = not undo_bus
                    disable_inputs = True
                elif 'redo-button' == ctx.triggered_id:
                    redo_bus = not redo_bus
                    disable_inputs = True

            # --------------------------------------------------------------------------------------- disable all inputs
            if True:
                if disable_inputs:
                    toggle_point_cloud_display_settings_disabled = True
                    toggle_mesh_disabled = True
                    toggle_mesh_display_settings_disabled = True
                    toggle_transform_controls_disabled = True
                    toggle_structure_controls_disabled = True
                    toggle_segmentation_controls_disabled = True
                    toggle_load_save_disabled = True
                    toggle_presets_disabled = True
                    transform_lock_disabled = True
                    transform_controls_disabled = True
                    structure_lock_disabled = True
                    structure_controls_disabled = True
                    save_disabled = True
                    load_disabled = True
                    torus_disabled = True
                    sphere_disabled = True
                    cube_disabled = True
                    update_disabled = True
                    undo_disabled = True
                    redo_disabled = True
                else:
                    toggle_point_cloud_display_settings_disabled = False
                    toggle_mesh_disabled = False
                    toggle_mesh_display_settings_disabled = False
                    toggle_transform_controls_disabled = False
                    toggle_structure_controls_disabled = False
                    toggle_segmentation_controls_disabled = False
                    toggle_load_save_disabled = False
                    toggle_presets_disabled = False
                    transform_lock_disabled = False
                    transform_controls_disabled = False
                    structure_lock_disabled = False
                    structure_controls_disabled = False
                    save_disabled = False
                    load_disabled = False
                    torus_disabled = False
                    sphere_disabled = False
                    cube_disabled = False
                    update_disabled = False
                    undo_disabled = False
                    redo_disabled = False

            return \
                ([{'label': 'Display Settings', 'value': 'show','disabled': toggle_point_cloud_display_settings_disabled}],
                 [{'label': 'Mesh', 'value': 'show', 'disabled': toggle_mesh_disabled}],
                 [{'label': 'Display Settings', 'value': 'show','disabled': toggle_mesh_display_settings_disabled}],
                 [{'label': 'Transform Controls', 'value': 'show','disabled': toggle_transform_controls_disabled}],
                 [{'label': 'Structure Controls', 'value': 'show','disabled': toggle_structure_controls_disabled}],
                 [{'label': 'Segmentation Controls', 'value': 'show', 'disabled': toggle_segmentation_controls_disabled}],
                 [{'label': 'Load/Save', 'value': 'show', 'disabled': toggle_load_save_disabled}],
                 [{'label': 'Presets', 'value': 'show', 'disabled': toggle_presets_disabled}],
                 polyhedralise_bus, face_add_bus, face_delete_bus,
                 save_bus,
                 torus_bus, sphere_bus, cube_bus,
                 update_bus, undo_bus, redo_bus,
                 transform_lock_disabled,
                 transform_controls_disabled, transform_controls_disabled,
                 transform_controls_disabled, transform_controls_disabled,
                 transform_controls_disabled, transform_controls_disabled,
                 transform_controls_disabled, transform_controls_disabled,
                 structure_lock_disabled,
                 structure_controls_disabled, structure_controls_disabled, structure_controls_disabled,
                 save_disabled, load_disabled,
                 torus_disabled, sphere_disabled, cube_disabled,
                 update_disabled, undo_disabled, redo_disabled)

    app.run_server(debug=True)


if __name__ == '__main__':
    print('Running main...')
    main()
else:
    from time_log import TimeLog

    tl = TimeLog()

    from transforms import Transforms

    tf = Transforms()
