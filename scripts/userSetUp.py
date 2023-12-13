# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import os
import sys
from ctypes import *

from feedback_tool import Feedback_info as fp


class ClearOutputWindow:
    def __init__(self):
        self.user32 = windll.user32
        self.EnumWindowsProc = WINFUNCTYPE(c_int, c_int, c_int)
        self.clear()

    def get_handle(self, title, parent=None):
        """
        将句柄返回到具有匹配标题的窗口
        :param title:
        :param parent:
        :return:
        """
        rHwnd = []
        def EnumCB(hwnd, lparam, match=title.lower(), rHwnd=rHwnd):
            if lparam == 1:
                rHwnd.append(hwnd)
                return False
            title = c_buffer(' ' * 256)
            self.user32.GetWindowTextA(hwnd, title, 255)
            if title.value.lower() == match:
                rHwnd.append(hwnd)
                return False
            return True
        if parent is not None:
            self.user32.EnumChildWindows(parent, self.EnumWindowsProc(EnumCB), 1)
        else:
            self.user32.EnumWindows(self.EnumWindowsProc(EnumCB), 0)
        return rHwnd

    def clear(self):
        """
        清除 Maya output窗口
        """
        out = self.get_handle("Output Window")
        if not out:
            fp("找不到输出窗口", warning=True, viewMes=True)
        else:
            ch = self.get_handle("", out[0])
            if ch[0]:
                self.user32.SendMessageA(ch[0], 0x00B1, 0, -1)
                self.user32.SendMessageA(ch[0], 0x00C2, 1, "")
                sys.__stdout__.write('''\n                   . .\n                 '.-:-.`\n                 '  :  `
              .-----:\n            .'       `.\n      ,    /       (o) \\  愉快的Maya时光开始咯~~
      \\`._/          ,__)\n  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~''')
            else:
                fp("找不到子窗口", warning=True, viewMes=True)


class RIG_setUp(object):
    """
    添加图片路径环境
    生成菜单
    生成热盒
    添加meta脚本插件
    设置默认路径为工作区
    """

    def __init__(self):
        if os.path.exists('C:/Rig_Tools'):
            #self.renew_svn()
            self.clear_maya_output()
            self.add_toolScript_path()
            self.create_menu()
            self.create_hotBox()
            self.add_metaToMaya_plug()
            self.set_defaultWorlkSpace()
        else:
            fp('找不到插件路径，请到服务器安装工具架。', error=True)

    @staticmethod
    def clear_maya_output():
        ClearOutputWindow()

    @staticmethod
    def renew_svn():
        import svn_tool
        svn_tool.svn_upData()
        fp('工具架同步成功', info=True, viewMes=True)

    @staticmethod
    def add_toolScript_path():
        sys_path = ['C:/Rig_Tools/tools', 'C:/cgteamwork/bin/base']
        for path in sys_path:
            if path not in sys.path:
                sys.path.append(path) if os.path.exists(path) else fp('路径{}不存在'.format(path), warning=True)

    @staticmethod
    def create_menu():
        import reload_tools
        reload(reload_tools)
        reload_tools.reload_menu_ui()

    @staticmethod
    def create_hotBox():
        import reload_tools
        reload(reload_tools)
        reload_tools.reload_hot_ui()

    @staticmethod
    def add_metaToMaya_plug():
        try:
            if mc.pluginInfo('embeddedRL4', q=True, r=True):
                fp('bridgeToMaya已经加载。', info=True)
            else:
                if 'C:/Rig_Tools/scripts/Bridge_To_Maya' not in sys.path:
                    sys.path.append('C:/Rig_Tools/scripts/Bridge_To_Maya')

                from DHI import DHIPluginLoader
                import LiveLink
                DHIPluginLoader.load()  #添加meta脚本插件
                if not mc.about(b=True):#在批处理模式下监听器会导致出现QWidget: Cannot create a QWidget without QApplication
                    LiveLink.initLiveLink()  #实时链接
                fp('已加载bridgeToMaya {}插件集。'.format(LiveLink.MAYA_PLUGIN_VERSION), info=True)

        except Exception as e:
            rest = mc.confirmDialog(title='插件加载失败：', message='请注意，你的metaToMaya插件加载可能失败。\n{}'.format(e),
                                    button=['确定', '检查插件管理器'])
            if rest == u'检查插件管理器':
                mm.eval('PluginManager;')
            fp('bridgeToMaya插件集加载失败。', error=True)

    @staticmethod
    def set_defaultWorlkSpace():
        """
        将工作区设置为默认路径，而非meta的路径
        :return:
        """
        document_path = mc.internalVar(uad=True)
        mc.workspace('{}projects/default'.format(document_path), o=True)



mc.evalDeferred('RIG_setUp()')
