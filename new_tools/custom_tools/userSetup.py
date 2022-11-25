# -*- coding:GBK -*-
import maya.cmds as mc
import os
import sys
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

if sys.version_info.major == 3:
    #������Ϊpy3ʱ
    from importlib import reload

class SX_Widget(object):
    '''
    ���ͼƬ·������
    ���ɲ˵�
    �����Ⱥ�
    '''

    def __init__(self):
        if os.path.exists('Z:/Library/rig_plug_in/maya_plug/custom_tools'):
            self.create_IconPath()
            self.create_menu()
            self.create_hotBox()
        else:
            log.error('�Ҳ������������·�����������������Ƿ������ӵ��������ˡ�')

    def create_IconPath(self):
        os.environ['XBMLANGPATH'] = str(os.environ['XBMLANGPATH']) + ';' + r'Z:\Library\rig_plug_in\maya_plug\data\icon'

    def create_menu(self):
        try:
            from sx_toolBOX.SX_rig.rig_window import menu_ui
            reload(menu_ui)
            menu_ui.SX_Menu()
            log.info('�˵����ɳɹ���')
        except:
            log.error('�˵�����ʧ�ܡ�')

    def create_hotBox(self):
        try:
            from sx_toolBOX.SX_rig.rig_window import hotBox_ui
            reload(hotBox_ui)
            hotBox_ui.SX_RotBox()
            log.info('�Ⱥ����ɳɹ���')
        except:
            log.error('�Ⱥ�����ʧ�ܡ�')


mc.evalDeferred('SX_Widget()')