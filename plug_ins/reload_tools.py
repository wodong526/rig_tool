# coding=gbk
import maya.cmds as mc

import os
import shutil

from feedback_tool import Feedback_info as fp


def reload_hot_ui():
    """
    刷新热盒
    :return:
    """
    if mc.menu('hot_box_ui', ex=True):
        mc.deleteUI('hot_box_ui')

    from ui import hotBox_ui
    reload(hotBox_ui)
    hotBox_ui.Rig_HotBox()
    fp('热盒刷新成功', info=True, viewMes=True)


def reload_menu_ui():
    """
    刷新菜单
    :return:
    """
    if mc.menu('menu_ui', ex=True):
        mc.deleteUI('menu_ui')

    from ui import menu_ui
    reload(menu_ui)
    menu_ui.Rig_Menu()
    fp('菜单刷新成功', info=True, viewMes=True)


def reload_mod():
    """
    将mod文件也更新一遍
    :return:
    """
    maya_mod_path = mc.internalVar(uad=True) + "modules/Rig_Tools.mod"
    if os.path.exists(mc.internalVar(uad=True) + 'modules'):
        if os.path.exists(maya_mod_path):
            os.remove(maya_mod_path)
    else:
        os.mkdir(mc.internalVar(uad=True) + 'modules')
    shutil.copy('Z:/Library/rig_plug_in/Maya_openTools/Rig_Tools.mod', mc.internalVar(uad=True) + 'modules')
