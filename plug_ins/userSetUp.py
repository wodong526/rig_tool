# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import os
import sys

from feedback_tool import Feedback_info as fb_print, LIN as lin


class RIG_setUp(object):
    """
    ���ͼƬ·������
    ���ɲ˵�
    �����Ⱥ�
    ���meta�ű����
    ����Ĭ��·��Ϊ������
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
            fb_print('�Ҳ������·�����뵽��������װ���߼ܡ�', error=True)

    def renew_svn(self):
        import svn_tool
        svn_tool.svn_upData()
        fb_print('���߼�ͬ���ɹ�', info=True, viewMes=True)

    def add_toolScript_path(self):
        sys.path.append('C:/Rig_Tools/tools')

    def create_IconPath(self):
        if 'C:\Rig_Tools\icons' not in os.environ['XBMLANGPATH']:
            os.environ['XBMLANGPATH'] = str(os.environ['XBMLANGPATH']) + ';' + r'C:\Rig_Tools\icons'

    def create_menu(self):
        try:
            from ui.menu_ui import Rig_Menu
            Rig_Menu()
            fb_print('�˵����ɳɹ�', info=True)
        except:
            fb_print('�˵�����ʧ��', line=lin(), error=True)

    def create_hotBox(self):
        try:
            from ui.hotBox_ui import Rig_HotBox
            Rig_HotBox()
            fb_print('�Ⱥ����ɳɹ���', info=True)
        except:
            fb_print('�Ⱥ�����ʧ�ܡ�', line=lin(), error=True)

    def add_metaToMata_plug(self):
        try:
            if mc.pluginInfo('embeddedRL4', q=1, r=1):
                fb_print('bridgeToMaya�Ѿ����ء�', info=True)
            else:
                if 'C:/Rig_Tools/plug_ins/Bridge_To_Maya' in sys.path:
                    pass
                else:
                    sys.path.append('C:/Rig_Tools/plug_ins/Bridge_To_Maya')

                from DHI import DHIPluginLoader
                import LiveLink
                DHIPluginLoader.load()  #���meta�ű����
                LiveLink.initLiveLink()  #ʵʱ����
                fb_print('�Ѽ���bridgeToMaya {}�������'.format(LiveLink.MAYA_PLUGIN_VERSION), info=True)

        except:
            rest = mc.confirmDialog(title='�������ʧ�ܣ�', message='��ע�⣬���metaToMaya������ؿ���ʧ�ܡ�',
                                    button=['ȷ��', '�����������'])
            if rest == u'�����������':
                mm.eval('PluginManager;')
            fb_print('bridgeToMaya���������ʧ�ܡ�', error=True)

    def set_defaultWorlkSpace(self):
        """
        ������������ΪĬ��·��������meta��·��
        :return:
        """
        document_path = mc.internalVar(uad=True)
        mc.workspace('{}projects/default'.format(document_path), o=True)


mc.evalDeferred('RIG_setUp()')
