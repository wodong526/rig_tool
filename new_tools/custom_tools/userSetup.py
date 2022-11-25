# -*- coding:GBK -*-
import maya.cmds as mc
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
    '''

    def __init__(self):
        if os.path.exists('Z:/Library/rig_plug_in/maya_plug/custom_tools'):
            self.create_IconPath()
            self.create_menu()
            self.create_hotBox()
        else:
            log.error('找不到服务器插件路径，请检查您的网络是否已链接到服务器端。')

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


mc.evalDeferred('SX_Widget()')