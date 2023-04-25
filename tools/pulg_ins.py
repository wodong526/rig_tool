# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import sys

from feedback_tool import Feedback_info as fb_print
lin = sys._getframe()

def add_metaToMata_plug():
    try:
        if mc.pluginInfo('embeddedRL4', q=1, r=1):
            fb_print('bridgeToMaya已经加载', info=True, path=__file__, line=lin.f_lineno, viewMes=True)
        else:
            if 'C:/Rig_Tools/plug_ins/Bridge_To_Maya' in sys.path:
                pass
            else:
                sys.path.append('C:/Rig_Tools/plug_ins/Bridge_To_Maya')

            from DHI import DHIPluginLoader

            DHIPluginLoader.load()#添加meta脚本插件
            # Installer.createMSshelf()#将shelf栏的meta按钮刷新
            initLiveLink()#打开实时链接与加载材质的窗口ui（已关闭加载浮动窗口代码）
            fb_print('已加载bridgeToMaya插件集', info=True, path=__file__, line=lin.f_lineno, viewMes=True)
    except:
        rest = mc.confirmDialog(title='插件加载失败：', message='请注意，你的metaToMaya插件加载可能失败。',
                                button=['确定', '检查插件管理器'])
        if rest == u'检查插件管理器':
            mm.eval('PluginManager;')

def add_adPose_ui():
    from adPose import ui
    ui.show_in_maya()
    fb_print('已加载adPose窗口', info=True, path=__file__, line=lin.f_lineno)