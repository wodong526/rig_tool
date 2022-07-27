# -*- coding:GBK -*- 
import maya.cmds as mc
import os
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class SX_Widget(object):
    '''
    添加图片路径环境
    生成菜单
    生成热盒
    '''
    def __init__(self):
        self.create_IconPath()
        self.create_menu()
        self.create_hotBox()        

    def create_IconPath(self):
        os.environ['XBMLANGPATH'] = str(os.environ['XBMLANGPATH']) + ';' + r'C:\Users\Administrator\Documents\maya\scripts\icon'
    
    def create_menu(self):
        try:
            from sx_toolBOX.SX_rig import menu_ui
            reload(menu_ui)
            menu_ui.SX_Menu()
            log.info('菜单生成成功。')
        except:
            log.error('菜单生成失败。')
    
    def create_hotBox(self):
        try:
            from sx_toolBOX.SX_rig import hotBox_ui
            reload(hotBox_ui)
            hotBox_ui.SX_RotBox()
            log.info('热盒生成成功。')
        except:
            log.error('热盒生成失败。')

    
mc.evalDeferred('SX_Widget()')