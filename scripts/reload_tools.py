# coding=gbk
import maya.cmds as mc
import maya.mel as mm

import os
import shutil
import sys

from feedback_tool import Feedback_info as fp


def reload_hot_ui():
    """
    刷新热盒
    :return:
    """
    if mc.menu('hot_box_ui', ex=True):
        mc.deleteUI('hot_box_ui')

    from tool_ui import hotBox_ui
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

    from tool_ui import menu_ui
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

def open_studioLibrary():
    """
    打开studioLibrary窗口
    :return:
    """
    if not os.path.exists('C:/Rig_Tools/scripts/studio_library'):
        fp('C:/Rig_Tools/scripts/studio_library"路径不存在', error=True, path=True, viewMes=True)

    if 'C:/Rig_Tools/scripts/studio_library' not in sys.path:
        sys.path.insert(0, 'C:/Rig_Tools/plug_ins/studio_library')

    import studiolibrary
    studiolibrary.main()

def add_metaToMaya_plug():
    """
    加载metaToMaya插件
    :return:
    """
    try:
        if mc.pluginInfo('embeddedRL4', q=True, r=True):
            fp('bridgeToMaya已经加载', info=True, path=True, viewMes=True)
        else:
            if 'C:/Rig_Tools/scripts/Bridge_To_Maya' in sys.path:
                pass
            else:
                sys.path.append('//Bridge_To_Maya')

            from DHI import DHIPluginLoader

            DHIPluginLoader.load()#添加meta脚本插件
            # Installer.createMSshelf()#将shelf栏的meta按钮刷新
            initLiveLink()#打开实时链接与加载材质的窗口ui（已关闭加载浮动窗口代码）
            fp('已加载bridgeToMaya插件集', info=True, path=True, viewMes=True)
    except:
        rest = mc.confirmDialog(title='插件加载失败：', message='请注意，你的metaToMaya插件加载可能失败。',
                                button=['确定', '检查插件管理器'])
        if rest == u'检查插件管理器':
            mm.eval('PluginManager;')

def add_adPose_ui():
    from adPose import ui
    ui.show_in_maya()
    fp('已加载adPose窗口', info=True, path=True)