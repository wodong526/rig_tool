# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm
import os
import sys
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

if sys.version_info.major == 3:
    #当环境为py3时
    from importlib import reload


class SX_Widget(object):
    '''
    添加图片路径环境
    生成菜单
    生成热盒
    添加meta脚本插件
    '''

    def __init__(self):
        if os.path.exists('Z:/Library/rig_plug_in/maya_plug'):
            #self.create_IconPath()
            self.create_menu()
            #self.create_hotBox()
            self.add_metaToMata_plug()
        else:
            log.error('找不到服务器插件路径，请检查是否已链接到服务器端。')

    def create_IconPath(self):
        os.environ['XBMLANGPATH'] = str(os.environ['XBMLANGPATH']) + ';' + r'Z:\Library\rig_plug_in\maya_plug\data\icon'

    def create_menu(self):
        try:
            from sx_toolBOX.SX_rig.rig_window import menu_ui
            reload(menu_ui)
            menu_ui.SX_Menu()
            log.info('菜单生成成功。')
        except:
            log.error('菜单生成失败。')

    def create_hotBox(self):
        try:
            from sx_toolBOX.SX_rig.rig_window import hotBox_ui
            reload(hotBox_ui)
            hotBox_ui.SX_RotBox()
            log.info('热盒生成成功。')
        except:
            log.error('热盒生成失败。')

    def add_metaToMata_plug(self):
        try:
            if mc.pluginInfo('embeddedRL4', q=1, r=1):
                log.info('bridgeToMaya已经加载。')
            else:
                if 'Z:/Library/rig_plug_in/maya_plug/data/Bridge_To_Maya' in sys.path:
                    pass
                else:
                    sys.path.append('Z:/Library/rig_plug_in/maya_plug/data/Bridge_To_Maya')

                from DHI import DHIPluginLoader
                import LiveLink
                DHIPluginLoader.load()  #添加meta脚本插件
                LiveLink.initLiveLink()  #实时链接
                log.info('已加载bridgeToMaya插件集。')

        except:
            rest = mc.confirmDialog(title='插件加载失败：', message='请注意，你的metaToMaya插件加载可能失败。',
                                    button=['确定', '检查插件管理器'])
            if rest == '检查插件管理器':
                mm.eval('PluginManager;')
            log.error('bridgeToMaya插件集加载失败。')


mc.evalDeferred('SX_Widget()')