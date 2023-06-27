# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import os
import sys

from feedback_tool import Feedback_info as fb_print, LIN as lin


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
            self.add_toolScript_path()
            self.create_IconPath()
            self.create_menu()
            self.create_hotBox()
            self.add_metaToMata_plug()
            self.set_defaultWorlkSpace()
        else:
            fb_print('找不到插件路径，请到服务器安装工具架。', error=True)

    def renew_svn(self):
        import svn_tool
        svn_tool.svn_upData()
        fb_print('工具架同步成功', info=True, viewMes=True)

    def add_toolScript_path(self):
        sys.path.append('C:/Rig_Tools/tools')

    def create_IconPath(self):
        if 'C:\Rig_Tools\icons' not in os.environ['XBMLANGPATH']:
            os.environ['XBMLANGPATH'] = str(os.environ['XBMLANGPATH']) + ';' + r'C:\Rig_Tools\icons'

    def create_menu(self):
        try:
            from ui.menu_ui import Rig_Menu
            Rig_Menu()
            fb_print('菜单生成成功', info=True)
        except:
            fb_print('菜单生成失败', line=lin(), error=True)

    def create_hotBox(self):
        try:
            from ui.hotBox_ui import Rig_HotBox
            Rig_HotBox()
            fb_print('热盒生成成功。', info=True)
        except:
            fb_print('热盒生成失败。', line=lin(), error=True)

    def add_metaToMata_plug(self):
        try:
            if mc.pluginInfo('embeddedRL4', q=1, r=1):
                fb_print('bridgeToMaya已经加载。', info=True)
            else:
                if 'C:/Rig_Tools/plug_ins/Bridge_To_Maya' in sys.path:
                    pass
                else:
                    sys.path.append('C:/Rig_Tools/plug_ins/Bridge_To_Maya')

                from DHI import DHIPluginLoader
                import LiveLink
                DHIPluginLoader.load()  #添加meta脚本插件
                LiveLink.initLiveLink()  #实时链接
                fb_print('已加载bridgeToMaya {}插件集。'.format(LiveLink.MAYA_PLUGIN_VERSION), info=True)

        except:
            rest = mc.confirmDialog(title='插件加载失败：', message='请注意，你的metaToMaya插件加载可能失败。',
                                    button=['确定', '检查插件管理器'])
            if rest == u'检查插件管理器':
                mm.eval('PluginManager;')
            fb_print('bridgeToMaya插件集加载失败。', error=True)

    def set_defaultWorlkSpace(self):
        """
        将工作区设置为默认路径，而非meta的路径
        :return:
        """
        document_path = mc.internalVar(uad=True)
        mc.workspace('{}projects/default'.format(document_path), o=True)


mc.evalDeferred('RIG_setUp()')
