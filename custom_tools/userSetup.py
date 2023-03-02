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
    #������Ϊpy3ʱ
    from importlib import reload


class SX_Widget(object):
    '''
    ���ͼƬ·������
    ���ɲ˵�
    �����Ⱥ�
    ���meta�ű����
    '''

    def __init__(self):
        if os.path.exists('Z:/Library/rig_plug_in/maya_plug'):
            #self.create_IconPath()
            self.create_menu()
            #self.create_hotBox()
            self.add_metaToMata_plug()
        else:
            log.error('�Ҳ������������·���������Ƿ������ӵ��������ˡ�')

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

    def add_metaToMata_plug(self):
        try:
            if mc.pluginInfo('embeddedRL4', q=1, r=1):
                log.info('bridgeToMaya�Ѿ����ء�')
            else:
                if 'Z:/Library/rig_plug_in/maya_plug/data/Bridge_To_Maya' in sys.path:
                    pass
                else:
                    sys.path.append('Z:/Library/rig_plug_in/maya_plug/data/Bridge_To_Maya')

                from DHI import DHIPluginLoader
                import LiveLink
                DHIPluginLoader.load()  #���meta�ű����
                LiveLink.initLiveLink()  #ʵʱ����
                log.info('�Ѽ���bridgeToMaya�������')

        except:
            rest = mc.confirmDialog(title='�������ʧ�ܣ�', message='��ע�⣬���metaToMaya������ؿ���ʧ�ܡ�',
                                    button=['ȷ��', '�����������'])
            if rest == '�����������':
                mm.eval('PluginManager;')
            log.error('bridgeToMaya���������ʧ�ܡ�')


mc.evalDeferred('SX_Widget()')