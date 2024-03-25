# coding=gbk
from PySide2 import QtWidgets

from ngSkinTools2 import signal
from ngSkinTools2.api import Mirror, MirrorOptions, VertexTransferMode
from ngSkinTools2.api.log import getLogger
from ngSkinTools2.api.mirror import set_reference_mesh_from_selection
from ngSkinTools2.api.session import session
from ngSkinTools2.ui import qt
from ngSkinTools2.ui.layout import TabSetup, createTitledRow
from ngSkinTools2.ui.options import bind_checkbox, config
from ngSkinTools2.ui.widgets import NumberSliderGroup

log = getLogger("tab paint")


def buildUI(parent_window):
    def build_mirroring_options_group():
        def get_mirror_direction():
            mirror_direction = QtWidgets.QComboBox()
            mirror_direction.addItem(u"���ݱ�ˢ���в²�e", MirrorOptions.directionGuess)
            mirror_direction.addItem(u"��������", MirrorOptions.directionPositiveToNegative)
            mirror_direction.addItem(u"�Ӹ�����", MirrorOptions.directionNegativeToPositive)
            mirror_direction.addItem(u"��ת", MirrorOptions.directionFlip)
            mirror_direction.setMinimumWidth(1)
            qt.select_data(mirror_direction, config.mirror_direction())

            @qt.on(mirror_direction.currentIndexChanged)
            def value_changed():
                config.mirror_direction.set(mirror_direction.currentData())

            return mirror_direction

        def axis():
            mirror_axis = QtWidgets.QComboBox()
            mirror_axis.addItem("X", 'x')
            mirror_axis.addItem("Y", 'y')
            mirror_axis.addItem("Z", 'z')

            @qt.on(mirror_axis.currentIndexChanged)
            def value_changed():
                session.state.mirror().axis = mirror_axis.currentData()

            @signal.on(session.events.targetChanged)
            def target_changed():
                if session.state.layersAvailable:
                    qt.select_data(mirror_axis, session.state.mirror().axis)

            target_changed()

            return mirror_axis

        def mirror_seam_width():
            seam_width_ctrl = NumberSliderGroup(max_value=100)

            @signal.on(seam_width_ctrl.valueChanged)
            def value_changed():
                session.state.mirror().seam_width = seam_width_ctrl.value()

            @signal.on(session.events.targetChanged)
            def update_values():
                if session.state.layersAvailable:
                    seam_width_ctrl.set_value(session.state.mirror().seam_width)

            update_values()

            return seam_width_ctrl.layout()

        def elements():
            influences = bind_checkbox(QtWidgets.QCheckBox(u"Ӱ��Ȩ��"), config.mirror_weights)
            mask = bind_checkbox(QtWidgets.QCheckBox(u"ͼ���ɰ�"), config.mirror_mask)
            dq = bind_checkbox(QtWidgets.QCheckBox(u"˫��Ԫ��Ȩ��"), config.mirror_dq)

            return influences, mask, dq

        result = QtWidgets.QGroupBox(u"����ѡ��")
        layout = QtWidgets.QVBoxLayout()
        result.setLayout(layout)
        layout.addLayout(createTitledRow(u"��:", axis()))
        layout.addLayout(createTitledRow(u"����:", get_mirror_direction()))
        layout.addLayout(createTitledRow(u"�ӷ���:", mirror_seam_width()))
        layout.addLayout(createTitledRow(u"Ҫ�����Ԫ��:", *elements()))

        return result

    def vertex_mapping_group():
        # noinspection PyShadowingNames
        def mirror_mesh_group():
            mesh_name_edit = QtWidgets.QLineEdit(u"����1")
            mesh_name_edit.setReadOnly(True)
            select_button = QtWidgets.QPushButton(u"ѡ��")
            create_button = QtWidgets.QPushButton(u"����")
            set_button = QtWidgets.QPushButton(u"����")
            set_button.setToolTip(u"����ѡ��Գ��������ƤĿ��")

            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(mesh_name_edit)
            layout.addWidget(create_button)
            layout.addWidget(select_button)
            layout.addWidget(set_button)

            @signal.on(session.events.targetChanged, qtParent=tab.tabContents)
            def update_ui():
                if not session.state.layersAvailable:
                    return

                mesh = Mirror(session.state.selectedSkinCluster).get_reference_mesh()
                mesh_name_edit.setText(mesh or "")

            def select_mesh(m):
                if m is None:
                    return

                from maya import cmds

                cmds.setToolTo("moveSuperContext")
                cmds.selectMode(component=True)
                cmds.select(m + ".vtx[*]", r=True)
                cmds.hilite(m, replace=True)
                cmds.viewFit()

            @qt.on(select_button.clicked)
            def select_handler():
                select_mesh(Mirror(session.state.selectedSkinCluster).get_reference_mesh())

            @qt.on(create_button.clicked)
            def create():
                if not session.state.layersAvailable:
                    return

                m = Mirror(session.state.selectedSkinCluster)
                mesh = m.get_reference_mesh()
                if mesh is None:
                    mesh = m.build_reference_mesh()

                update_ui()
                select_mesh(mesh)

            @qt.on(set_button.clicked)
            def set():
                set_reference_mesh_from_selection()
                update_ui()

            update_ui()

            return layout

        vertex_mapping_mode = QtWidgets.QComboBox()
        vertex_mapping_mode.addItem(u"��������ĵ�", VertexTransferMode.closestPoint)
        vertex_mapping_mode.addItem(u"UV �ռ�", VertexTransferMode.uvSpace)

        result = QtWidgets.QGroupBox(u"����ӳ��")
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(createTitledRow(u"ӳ��ģʽ:", vertex_mapping_mode))
        layout.addLayout(createTitledRow(u"�Գ�����:", mirror_mesh_group()))
        result.setLayout(layout)

        @qt.on(vertex_mapping_mode.currentIndexChanged)
        def value_changed():
            session.state.mirror().vertex_transfer_mode = vertex_mapping_mode.currentData()

        @signal.on(session.events.targetChanged)
        def target_changed():
            if session.state.layersAvailable:
                qt.select_data(vertex_mapping_mode, session.state.mirror().vertex_transfer_mode)

        return result

    def influence_mapping_group():
        def edit_mapping():
            mapping = QtWidgets.QPushButton(u"Ԥ���ͱ༭ӳ��")

            single_window_policy = qt.SingleWindowPolicy()

            @qt.on(mapping.clicked)
            def edit():
                from ngSkinTools2.ui import influenceMappingUI

                window = influenceMappingUI.open_ui_for_mesh(parent_window, session.state.selectedSkinCluster)
                single_window_policy.setCurrent(window)

            return mapping

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(edit_mapping())

        result = QtWidgets.QGroupBox(u"Ӱ��ؽ�ӳ��")
        result.setLayout(layout)
        return result

    tab = TabSetup()
    tab.innerLayout.addWidget(build_mirroring_options_group())
    tab.innerLayout.addWidget(vertex_mapping_group())
    tab.innerLayout.addWidget(influence_mapping_group())
    tab.innerLayout.addStretch()

    btn_mirror = QtWidgets.QPushButton(u"����")
    tab.lowerButtonsRow.addWidget(btn_mirror)

    @qt.on(btn_mirror.clicked)
    def mirror_clicked():
        if session.state.currentLayer.layer:
            mirror_options = MirrorOptions()
            mirror_options.direction = config.mirror_direction()
            mirror_options.mirrorDq = config.mirror_dq()
            mirror_options.mirrorMask = config.mirror_mask()
            mirror_options.mirrorWeights = config.mirror_weights()

            session.state.mirror().mirror(mirror_options)

    @signal.on(session.events.targetChanged, qtParent=tab.tabContents)
    def update_ui():
        tab.tabContents.setEnabled(session.state.layersAvailable)

    update_ui()

    return tab.tabContents
