# -*- coding:GBK -*- 
import maya.cmds as mc
import os
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class SX_Widget(object):
    '''
    ���ͼƬ·������
    ���ɲ˵�
    �����Ⱥ�
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
            log.info('�˵����ɳɹ���')
        except:
            log.error('�˵�����ʧ�ܡ�')
    
    def create_hotBox(self):
        try:
            from sx_toolBOX.SX_rig import hotBox_ui
            reload(hotBox_ui)
            hotBox_ui.SX_RotBox()
            log.info('�Ⱥ����ɳɹ���')
        except:
            log.error('�Ⱥ�����ʧ�ܡ�')

    
mc.evalDeferred('SX_Widget()')