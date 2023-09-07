# coding=gbk
import maya.cmds as mc

import os
import shutil
import sys

from feedback_tool import Feedback_info as fp


def reload_hot_ui():
    """
    ˢ���Ⱥ�
    :return:
    """
    if mc.menu('hot_box_ui', ex=True):
        mc.deleteUI('hot_box_ui')

    from ui import hotBox_ui
    reload(hotBox_ui)
    hotBox_ui.Rig_HotBox()
    fp('�Ⱥ�ˢ�³ɹ�', info=True, viewMes=True)


def reload_menu_ui():
    """
    ˢ�²˵�
    :return:
    """
    if mc.menu('menu_ui', ex=True):
        mc.deleteUI('menu_ui')

    from ui import menu_ui
    reload(menu_ui)
    menu_ui.Rig_Menu()
    fp('�˵�ˢ�³ɹ�', info=True, viewMes=True)


def reload_mod():
    """
    ��mod�ļ�Ҳ����һ��
    :return:
    """
    maya_mod_path = mc.internalVar(uad=True) + "modules/Rig_Tools.mod"
    if os.path.exists(mc.internalVar(uad=True) + 'modules'):
        if os.path.exists(maya_mod_path):
            os.remove(maya_mod_path)
    else:
        os.mkdir(mc.internalVar(uad=True) + 'modules')
    shutil.copy('Z:/Library/rig_plug_in/Maya_openTools/Rig_Tools.mod', mc.internalVar(uad=True) + 'modules')

def open_studioLibrary():
    '''
    ��studioLibrary����
    :return:
    '''
    if not os.path.exists('C:/Rig_Tools/scripts/studio_library'):
        fp('C:/Rig_Tools/scripts/studio_library"·��������', error=True, path=__file__, line=lin.f_lineno,
                 viewMes=True)

    if 'C:/Rig_Tools/scripts/studio_library' not in sys.path:
        sys.path.insert(0, 'C:/Rig_Tools/plug_ins/studio_library')

    import studiolibrary
    studiolibrary.main()
