# coding=gbk
from ngSkinTools2 import api, signal
from ngSkinTools2.api import Layer, PasteOperation
from ngSkinTools2.api.session import Session


def action_copy_cut(session, parent, cut):
    """
    :type session: Session
    :type parent: PySide2.QtWidgets.QWidget
    :type cut: bool
    """
    from ngSkinTools2.ui import actions

    def cut_copy_callback():
        if session.state.selectedSkinCluster is None:
            return
        if session.state.currentLayer.layer is None:
            return
        influences = session.state.currentLayer.layer.paint_targets
        operation = api.copy_weights  # type: Callable[[Layer, list], None]
        if cut:
            operation = api.cut_weights

        operation(session.state.currentLayer.layer, influences)

    operation_name = u"����" if cut else u"����"
    result = actions.define_action(parent, operation_name + u"�������Ȩ��", callback=cut_copy_callback)

    @signal.on(session.events.currentLayerChanged, session.events.currentInfluenceChanged, qtParent=parent)
    def on_selection_changed():
        layer = session.state.currentLayer.layer
        result.setEnabled(layer is not None and len(layer.paint_targets) > 0)

    return result


def action_paste(session, parent, operation):
    """
    :type session: Session
    :type parent: PySide2.QtWidgets.QWidget
    :type cut: bool
    """
    from ngSkinTools2.ui import actions

    def paste_callback():
        if session.state.currentLayer.layer is None:
            return
        influences = session.state.currentLayer.layer.paint_targets
        api.paste_weights(session.state.currentLayer.layer, operation, influences=influences)

    labels = {
        PasteOperation.add: u'ճ��Ȩ�أ���ӵ�����Ȩ�أ�',
        PasteOperation.subtract: u'ճ��Ȩ�أ���ȥ����Ȩ�أ�',
        PasteOperation.replace: u'ճ��Ȩ�أ��滻����Ȩ�أ�',
    }

    result = actions.define_action(parent, labels[operation], callback=paste_callback)
    result.setToolTip(u"�Ӽ�����ճ����ǰ���Ƶ�Ȩ��")

    @signal.on(session.events.currentLayerChanged)
    def on_selection_changed():
        result.setEnabled(session.state.currentLayer.layer is not None)

    return result
