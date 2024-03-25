# coding=gbk
from PySide2 import QtWidgets

from ngSkinTools2 import signal
from ngSkinTools2.api.session import Session
from ngSkinTools2.ui import model_binds, qt, widgets
from ngSkinTools2.ui.actions import Actions
from ngSkinTools2.ui.layout import TabSetup, createTitledRow


def build_ui(actions, session):
    """

    :type actions: Actions
    :type session: Session
    """

    def assign_weights_from_closest_joint_group():
        options = actions.toolsAssignFromClosestJointOptions

        # noinspection PyShadowingNames
        def influences_options():
            result = QtWidgets.QVBoxLayout()
            button_group = QtWidgets.QButtonGroup()
            for index, i in enumerate([u"ʹ�����п��õ�Ӱ��ؽ�", u"ʹ��ѡ����Ӱ��ؽ�"]):
                radio = QtWidgets.QRadioButton(i)
                button_group.addButton(radio, index)
                result.addWidget(radio)

                @qt.on(radio.toggled)
                def update_value():
                    options.all_influences.set(button_group.buttons()[0].isChecked())

            # noinspection PyShadowingNames
            @signal.on(options.all_influences.changed, qtParent=result)
            def update_ui():
                button_group.buttons()[0 if options.all_influences() else 1].setChecked(True)

            update_ui()

            return result

        new_layer = QtWidgets.QCheckBox(u"������ͼ��")

        @qt.on(new_layer.toggled)
        def update_new_layer():
            options.create_new_layer.set(new_layer.isChecked())

        @signal.on(options.create_new_layer.changed)
        def update_ui():
            new_layer.setChecked(options.create_new_layer())

        btn = QtWidgets.QPushButton()
        qt.bind_action_to_button(actions.toolsAssignFromClosestJoint, btn)

        update_ui()

        result = QtWidgets.QGroupBox(u"������Ĺؽ�ָ��Ȩ��")
        layout = QtWidgets.QVBoxLayout()
        result.setLayout(layout)
        layout.addLayout(createTitledRow(u"Ŀ���", new_layer))
        layout.addLayout(createTitledRow(u"Ӱ��ؽ�", influences_options()))
        layout.addWidget(btn)

        return result

    def unify_weights_group():
        options = actions.toolsUnifyWeightsOptions

        intensity = widgets.NumberSliderGroup()
        model_binds.bind(intensity, options.overall_effect)

        single_cluster_mode = QtWidgets.QCheckBox(u"����ģʽ",)
        single_cluster_mode.setToolTip(u"����ѡ����ƽ��Ȩ�أ����Ե�������ǻ�ѡ����϶")
        model_binds.bind(single_cluster_mode, options.single_cluster_mode)

        btn = QtWidgets.QPushButton()
        qt.bind_action_to_button(actions.toolsUnifyWeights, btn)

        result = QtWidgets.QGroupBox(u"ͳһȨ��")
        layout = QtWidgets.QVBoxLayout()
        result.setLayout(layout)
        layout.addLayout(createTitledRow(u"ǿ��:", intensity.layout()))
        layout.addLayout(createTitledRow(u"��Ⱥ:", single_cluster_mode))
        layout.addWidget(btn)

        return result

    def other_tools_group():
        result = QtWidgets.QGroupBox(u"����")
        layout = QtWidgets.QVBoxLayout()
        result.setLayout(layout)
        layout.addWidget(to_button(actions.fill_layer_transparency))
        layout.addWidget(to_button(actions.copy_components))
        layout.addWidget(to_button(actions.paste_component_average))

        return result

    tab = TabSetup()
    tab.innerLayout.addWidget(assign_weights_from_closest_joint_group())
    tab.innerLayout.addWidget(unify_weights_group())
    tab.innerLayout.addWidget(other_tools_group())
    tab.innerLayout.addStretch()

    @signal.on(session.events.targetChanged, qtParent=tab.tabContents)
    def update_tab_enabled():
        tab.tabContents.setEnabled(session.state.layersAvailable)

    update_tab_enabled()

    return tab.tabContents


def to_button(action):
    btn = QtWidgets.QPushButton()
    qt.bind_action_to_button(action, btn)
    return btn
