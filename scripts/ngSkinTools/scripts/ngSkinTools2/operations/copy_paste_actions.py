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

    operation_name = u"剪切" if cut else u"复制"
    result = actions.define_action(parent, operation_name + u"剪贴板的权重", callback=cut_copy_callback)

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
        PasteOperation.add: u'粘贴权重（添加到现有权重）',
        PasteOperation.subtract: u'粘贴权重（减去现有权重）',
        PasteOperation.replace: u'粘贴权重（替换现有权重）',
    }

    result = actions.define_action(parent, labels[operation], callback=paste_callback)
    result.setToolTip(u"从剪贴板粘贴以前复制的权重")

    @signal.on(session.events.currentLayerChanged)
    def on_selection_changed():
        result.setEnabled(session.state.currentLayer.layer is not None)

    return result
