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
        sys.path.append('C:/Rig_Tools/scripts/plug_ins')

    def create_IconPath(self):
        if 'C:\Rig_Tools\icons' not in os.environ['XBMLANGPATH']:
            os.environ['XBMLANGPATH'] = str(os.environ['XBMLANGPATH']) + ';' + r'C:\Rig_Tools\icons'

    def create_menu(self):
        import reload_tools
        reload(reload_tools)
        reload_tools.reload_menu_ui()

    def create_hotBox(self):
        import reload_tools
        reload(reload_tools)
        reload_tools.reload_hot_ui()

    def add_metaToMata_plug(self):
        try:
            if mc.pluginInfo('embeddedRL4', q=True, r=True):
                fb_print('bridgeToMaya�Ѿ����ء�', info=True)
            else:
                if 'C:/Rig_Tools/scripts/Bridge_To_Maya' not in sys.path:
                    sys.path.append('C:/Rig_Tools/scripts/Bridge_To_Maya')

                from DHI import DHIPluginLoader
                import LiveLink
                DHIPluginLoader.load()  #���meta�ű����
                if not mc.about(b=True):#��������ģʽ�¼������ᵼ�³���QWidget: Cannot create a QWidget without QApplication
                    LiveLink.initLiveLink()  #ʵʱ����
                fb_print('�Ѽ���bridgeToMaya {}�������'.format(LiveLink.MAYA_PLUGIN_VERSION), info=True)

        except Exception as e:
            rest = mc.confirmDialog(title='�������ʧ�ܣ�', message='��ע�⣬���metaToMaya������ؿ���ʧ�ܡ�\n{}'.format(e),
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


#if not mc.about(batch=True):
mc.evalDeferred('RIG_setUp()')
