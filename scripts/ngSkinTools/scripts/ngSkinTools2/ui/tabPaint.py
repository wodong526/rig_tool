# coding=gbk
from PySide2 import QtGui, QtWidgets

from ngSkinTools2 import signal
from ngSkinTools2.api import BrushShape, PaintMode, PaintTool, WeightsDisplayMode
from ngSkinTools2.api import eventtypes as et
from ngSkinTools2.api.log import getLogger
from ngSkinTools2.api.paint import BrushProjectionMode, MaskDisplayMode
from ngSkinTools2.api.session import session
from ngSkinTools2.ui import qt, widgets
from ngSkinTools2.ui.layout import TabSetup, createTitledRow
from ngSkinTools2.ui.qt import bind_action_to_button

log = getLogger("tab paint")


# noinspection PyShadowingNames
def build_ui(parent, global_actions):
    """
    :type parent: PySide2.QtWidgets.QWidget
    :type global_actions: ngSkinTools2.ui.actions.Actions
    """
    paint = session.paint_tool
    # TODO: move paint model to session maybe?

    on_signal = session.signal_hub.on

    def update_ui():
        pass  # noop until it's defined

    def build_brush_settings_group():
        def brush_mode_row3():
            row = QtWidgets.QVBoxLayout()

            group = QtWidgets.QActionGroup(parent)

            actions = {}

            # noinspection PyShadowingNames
            def create_brush_mode_button(t, mode, label, tooltip):
                a = QtWidgets.QAction(label, parent)
                a.setToolTip(tooltip)
                a.setCheckable(True)
                actions[mode] = a
                group.addAction(a)

                @qt.on(a.toggled)
                def toggled(checked):
                    if checked and paint.paint_mode != mode:
                        paint.paint_mode = mode

                t.addAction(a)

            t = QtWidgets.QToolBar()
            create_brush_mode_button(t, PaintMode.replace, u"�滻", u"����")
            create_brush_mode_button(t, PaintMode.add, u"���", "")
            row.addWidget(t)

            t = QtWidgets.QToolBar()
            create_brush_mode_button(t, PaintMode.scale, u"��ȥ", "")
            create_brush_mode_button(t, PaintMode.smooth, u"ƽ��", "")
            create_brush_mode_button(t, PaintMode.sharpen, u"��", "")
            row.addWidget(t)

            @on_signal(et.tool_settings_changed, scope=row)
            def update_current_brush_mode():
                actions[paint.paint_mode].setChecked(True)

            update_current_brush_mode()

            return row

        # noinspection DuplicatedCode
        def brush_shape_row():
            # noinspection PyShadowingNames
            result = QtWidgets.QToolBar()
            group = QtWidgets.QActionGroup(parent)

            def add_brush_shape_action(icon, title, shape, checked=False):
                a = QtWidgets.QAction(title, parent)
                a.setCheckable(True)
                a.setIcon(QtGui.QIcon(icon))
                a.setChecked(checked)
                result.addAction(a)
                group.addAction(a)

                # noinspection PyShadowingNames
                def toggled(checked):
                    if checked:
                        paint.brush_shape = shape
                        update_ui()

                # noinspection PyShadowingNames
                @on_signal(et.tool_settings_changed, scope=a)
                def update_to_tool():
                    a.setChecked(paint.brush_shape == shape)

                update_to_tool()
                qt.on(a.toggled)(toggled)

            add_brush_shape_action(':/circleSolid.png', 'Solid', BrushShape.solid, checked=True)
            add_brush_shape_action(':/circlePoly.png', 'Smooth', BrushShape.smooth)
            add_brush_shape_action(':/circleGaus.png', 'Gaus', BrushShape.gaus)

            return result

        # noinspection DuplicatedCode
        def brush_projection_mode_row():
            # noinspection PyShadowingNames
            result = QtWidgets.QToolBar()
            group = QtWidgets.QActionGroup(parent)

            def add(title, tooltip, mode, use_volume, checked):
                a = QtWidgets.QAction(title, parent)
                a.setCheckable(True)
                a.setChecked(checked)
                a.setToolTip(tooltip)
                a.setStatusTip(tooltip)
                result.addAction(a)
                group.addAction(a)

                # noinspection PyShadowingNames
                @qt.on(a.toggled)
                def toggled(checked):
                    if checked:
                        paint.brush_projection_mode = mode
                        paint.use_volume_neighbours = use_volume
                        update_ui()

                # noinspection PyShadowingNames
                @on_signal(et.tool_settings_changed, scope=a)
                def update_to_tool():
                    a.setChecked(
                        paint.brush_projection_mode == mode and (mode != BrushProjectionMode.surface or paint.use_volume_neighbours == use_volume)
                    )

                with qt.signals_blocked(a):
                    update_to_tool()

            add(
                u'����',
                'Using first surface hit under the mouse, update all nearby vertices that are connected by surface to the hit location. '
                + 'Only current shell will be updated.',
                BrushProjectionMode.surface,
                use_volume=False,
                checked=True,
            )
            add(
                u'���',
                'Using first surface hit under the mouse, update all nearby vertices, including those from other shells.',
                BrushProjectionMode.surface,
                use_volume=True,
                checked=False,
            )
            add(
                u'��Ļ',
                'Use screen projection of a brush, updating all vertices on all surfaces that are within the brush radius.',
                BrushProjectionMode.screen,
                use_volume=False,
                checked=False,
            )

            return result

        def stylus_pressure_selection():
            # noinspection PyShadowingNames
            result = QtWidgets.QComboBox()
            result.addItem("Unused")
            result.addItem("Multiply intensity")
            result.addItem("Multiply opacity")
            result.addItem("Multiply radius")
            return result

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(createTitledRow(u"��ˢӳ�䷽ʽ:", brush_projection_mode_row()))
        layout.addLayout(createTitledRow(u"��ˢģʽ:", brush_mode_row3()))
        layout.addLayout(createTitledRow(u"������״:", brush_shape_row()))
        intensity = widgets.NumberSliderGroup()
        radius = widgets.NumberSliderGroup(
            max_value=100, tooltip=u"Ҳ����ͨ����ס<b>B</b>�����ӿ����϶���������ñ�ˢ�뾶"
        )
        iterations = widgets.NumberSliderGroup(value_type=int, min_value=1, max_value=100)
        layout.addLayout(createTitledRow(u"ǿ��:", intensity.layout()))
        layout.addLayout(createTitledRow(u"���ʰ뾶:", radius.layout()))
        layout.addLayout(createTitledRow(u"���ʵ�������:", iterations.layout()))

        influences_limit = widgets.NumberSliderGroup(value_type=int, min_value=0, max_value=10)
        layout.addLayout(createTitledRow(u"����Ӱ��:", influences_limit.layout()))

        @signal.on(influences_limit.valueChanged)
        def influences_limit_changed():
            paint.influences_limit = influences_limit.value()
            update_ui()

        fixed_influences = QtWidgets.QCheckBox(u"���������ж���Ӱ��")
        fixed_influences.setToolTip(
            u"���ô�ѡ���ƽ����������ÿ�����������Ӱ��, "
            u"���Ҳ���������Ը������������Ӱ��"
        )
        layout.addLayout(createTitledRow(u"Ȩ������:", fixed_influences))

        @qt.on(fixed_influences.stateChanged)
        def fixed_influences_changed():
            paint.fixed_influences_per_vertex = fixed_influences.isChecked()

        limit_to_component_selection = QtWidgets.QCheckBox(u"���ѡ������")
        limit_to_component_selection.setToolTip(u"���ô�ѡ���ƽ��������ѡ�����֮�䷢��")
        layout.addLayout(createTitledRow(u"���:", limit_to_component_selection))

        @qt.on(limit_to_component_selection.stateChanged)
        def limit_to_component_selection_changed():
            paint.limit_to_component_selection = limit_to_component_selection.isChecked()

        interactive_mirror = QtWidgets.QCheckBox(u"����ʽ����")
        layout.addLayout(createTitledRow("", interactive_mirror))

        @qt.on(interactive_mirror.stateChanged)
        def interactive_mirror_changed():
            paint.mirror = interactive_mirror.isChecked()
            update_ui()

        sample_joint_on_stroke_start = QtWidgets.QCheckBox("Sample current joint on stroke start")
        layout.addLayout(createTitledRow("", sample_joint_on_stroke_start))

        @qt.on(sample_joint_on_stroke_start.stateChanged)
        def interactive_mirror_changed():
            paint.sample_joint_on_stroke_start = sample_joint_on_stroke_start.isChecked()
            update_ui()

        redistribute_removed_weight = QtWidgets.QCheckBox(u"���ݸ�����Ӱ��")
        layout.addLayout(createTitledRow(u"�Ƴ�����:", redistribute_removed_weight))

        @qt.on(redistribute_removed_weight.stateChanged)
        def redistribute_removed_weight_changed():
            paint.distribute_to_other_influences = redistribute_removed_weight.isChecked()
            update_ui()

        stylus = stylus_pressure_selection()
        layout.addLayout(createTitledRow(u"����ѹ��:", stylus))

        @on_signal(et.tool_settings_changed, scope=layout)
        def update_ui():
            log.info(u"���»�ͼ���� UI")
            log.info(u"��ˢģʽ:{}, ��ˢ��״: %s".format(paint.mode, paint.brush_shape))
            paint.update_plugin_brush_radius()

            with qt.signals_blocked(intensity):
                intensity.set_value(paint.intensity)
                widgets.set_paint_expo(intensity, paint.paint_mode)

            with qt.signals_blocked(radius):
                radius.set_range(0, 1000 if paint.brush_projection_mode == BrushProjectionMode.screen else 100, soft_max=True)
                radius.set_value(paint.brush_radius)

            with qt.signals_blocked(iterations):
                iterations.set_value(paint.iterations)
                iterations.set_enabled(paint.paint_mode in [PaintMode.smooth, PaintMode.sharpen])

            with qt.signals_blocked(stylus):
                stylus.setCurrentIndex(paint.tablet_mode)

            with qt.signals_blocked(interactive_mirror):
                interactive_mirror.setChecked(paint.mirror)

            with qt.signals_blocked(redistribute_removed_weight):
                redistribute_removed_weight.setChecked(paint.distribute_to_other_influences)

            with qt.signals_blocked(influences_limit):
                influences_limit.set_value(paint.influences_limit)

            with qt.signals_blocked(sample_joint_on_stroke_start):
                sample_joint_on_stroke_start.setChecked(paint.sample_joint_on_stroke_start)

            with qt.signals_blocked(fixed_influences):
                fixed_influences.setChecked(paint.fixed_influences_per_vertex)
                fixed_influences.setEnabled(paint.paint_mode == PaintMode.smooth)

            with qt.signals_blocked(limit_to_component_selection):
                limit_to_component_selection.setChecked(paint.limit_to_component_selection)
                limit_to_component_selection.setEnabled(fixed_influences.isEnabled())

        @signal.on(radius.valueChanged, qtParent=layout)
        def radius_edited():
            log.info(u"���±�ˢ�뾶")
            paint.brush_radius = radius.value()
            update_ui()

        @signal.on(intensity.valueChanged, qtParent=layout)
        def intensity_edited():
            paint.intensity = intensity.value()
            update_ui()

        @signal.on(iterations.valueChanged, qtParent=layout)
        def iterations_edited():
            paint.iterations = iterations.value()
            update_ui()

        @qt.on(stylus.currentIndexChanged)
        def stylus_edited():
            paint.tablet_mode = stylus.currentIndex()
            update_ui()

        update_ui()

        result = QtWidgets.QGroupBox(u"��ˢ����")
        result.setLayout(layout)
        return result

    def build_display_settings():
        result = QtWidgets.QGroupBox(u"��ʾ����")
        layout = QtWidgets.QVBoxLayout()

        influences_display = QtWidgets.QComboBox()
        influences_display.addItem(u"����Ӱ�죬������ɫ", WeightsDisplayMode.allInfluences)
        influences_display.addItem(u"��ǰӰ�죬�Ҷ�", WeightsDisplayMode.currentInfluence)
        influences_display.addItem(u"��ǰӰ�죬��ɫ", WeightsDisplayMode.currentInfluenceColored)
        influences_display.setMinimumWidth(1)
        influences_display.setCurrentIndex(paint.display_settings.weights_display_mode)

        display_toolbar = QtWidgets.QToolBar()
        display_toolbar.addAction(global_actions.randomizeInfluencesColors)

        @qt.on(influences_display.currentIndexChanged)
        def influences_display_changed():
            paint.display_settings.weights_display_mode = influences_display.currentData()
            update_ui_to_tool()

        display_layout = QtWidgets.QVBoxLayout()
        display_layout.addWidget(influences_display)
        display_layout.addWidget(display_toolbar)
        layout.addLayout(createTitledRow(u"Ȩ��Ӱ����ʾ:", display_layout))

        mask_display = QtWidgets.QComboBox()
        mask_display.addItem(u"Ĭ��", MaskDisplayMode.default_)
        mask_display.addItem(u"��ɫ����", MaskDisplayMode.color_ramp)
        mask_display.setMinimumWidth(1)
        mask_display.setCurrentIndex(paint.display_settings.weights_display_mode)

        @qt.on(mask_display.currentIndexChanged)
        def influences_display_changed():
            paint.display_settings.mask_display_mode = mask_display.currentData()
            update_ui_to_tool()

        layout.addLayout(createTitledRow(u"������ʾ:", mask_display))

        show_effects = QtWidgets.QCheckBox(u"��ʾͼ��Ч��")
        layout.addLayout(createTitledRow("", show_effects))
        show_masked = QtWidgets.QCheckBox(u"��ʾ���ֵ�Ȩ��")
        layout.addLayout(createTitledRow("", show_masked))

        show_selected_verts_only = QtWidgets.QCheckBox(u"����δѡ���Ķ���")
        layout.addLayout(createTitledRow("", show_selected_verts_only))

        @qt.on(show_effects.stateChanged)
        def show_effects_changed():
            paint.display_settings.layer_effects_display = show_effects.isChecked()

        @qt.on(show_masked.stateChanged)
        def show_masked_changed():
            paint.display_settings.display_masked = show_masked.isChecked()

        @qt.on(show_selected_verts_only.stateChanged)
        def show_selected_verts_changed():
            paint.display_settings.show_selected_verts_only = show_selected_verts_only.isChecked()

        mesh_toolbar = QtWidgets.QToolBar()
        toggle_original_mesh = QtWidgets.QAction(u"��ʾԭʼ����", mesh_toolbar)
        toggle_original_mesh.setCheckable(True)
        mesh_toolbar.addAction(toggle_original_mesh)
        layout.addLayout(createTitledRow("", mesh_toolbar))

        @qt.on(toggle_original_mesh.triggered)
        def toggle_display_node_visible():
            paint.display_settings.display_node_visible = not toggle_original_mesh.isChecked()
            update_ui_to_tool()

        wireframe_color_button = widgets.ColorButton()
        layout.addLayout(createTitledRow(u"�߿���ɫ:", wireframe_color_button))

        @signal.on(wireframe_color_button.color_changed)
        def update_wireframe_color():
            if paint.display_settings.weights_display_mode == WeightsDisplayMode.allInfluences:
                paint.display_settings.wireframe_color = wireframe_color_button.get_color_3f()
            else:
                paint.display_settings.wireframe_color_single_influence = wireframe_color_button.get_color_3f()

        @signal.on(session.events.toolChanged, qtParent=tab.tabContents)
        def update_ui_to_tool():
            ds = paint.display_settings
            toggle_original_mesh.setChecked(PaintTool.is_painting() and not ds.display_node_visible)

            qt.select_data(influences_display, ds.weights_display_mode)
            qt.select_data(mask_display, ds.mask_display_mode)
            show_effects.setChecked(ds.layer_effects_display)
            show_masked.setChecked(ds.display_masked)
            show_selected_verts_only.setChecked(ds.show_selected_verts_only)
            global_actions.randomizeInfluencesColors.setEnabled(ds.weights_display_mode == WeightsDisplayMode.allInfluences)
            display_toolbar.setVisible(global_actions.randomizeInfluencesColors.isEnabled())

            if ds.weights_display_mode == WeightsDisplayMode.allInfluences:
                wireframe_color_button.set_color(ds.wireframe_color)
            else:
                wireframe_color_button.set_color(ds.wireframe_color_single_influence)

        update_ui_to_tool()

        result.setLayout(layout)
        return result

    tab = TabSetup()
    tab.innerLayout.addWidget(build_brush_settings_group())
    tab.innerLayout.addWidget(build_display_settings())
    tab.innerLayout.addStretch()

    tab.lowerButtonsRow.addWidget(bind_action_to_button(global_actions.paint, QtWidgets.QPushButton()))
    tab.lowerButtonsRow.addWidget(bind_action_to_button(global_actions.flood, QtWidgets.QPushButton()))

    @signal.on(session.events.toolChanged, qtParent=tab.tabContents)
    def update_to_tool():
        tab.scrollArea.setEnabled(PaintTool.is_painting())

    @signal.on(session.events.targetChanged, qtParent=tab.tabContents)
    def update_tab_enabled():
        tab.tabContents.setEnabled(session.state.layersAvailable)

    update_to_tool()
    update_tab_enabled()

    return tab.tabContents
