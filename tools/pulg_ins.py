# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import sys

from feedback_tool import Feedback_info as fb_print
lin = sys._getframe()

def add_metaToMata_plug():
    try:
        if mc.pluginInfo('embeddedRL4', q=1, r=1):
            fb_print('bridgeToMaya�Ѿ�����', info=True, path=__file__, line=lin.f_lineno, viewMes=True)
        else:
            if 'C:/Rig_Tools/plug_ins/Bridge_To_Maya' in sys.path:
                pass
            else:
                sys.path.append('C:/Rig_Tools/plug_ins/Bridge_To_Maya')

            from DHI import DHIPluginLoader

            DHIPluginLoader.load()#���meta�ű����
            # Installer.createMSshelf()#��shelf����meta��ťˢ��
            initLiveLink()#��ʵʱ��������ز��ʵĴ���ui���ѹرռ��ظ������ڴ��룩
            fb_print('�Ѽ���bridgeToMaya�����', info=True, path=__file__, line=lin.f_lineno, viewMes=True)
    except:
        rest = mc.confirmDialog(title='�������ʧ�ܣ�', message='��ע�⣬���metaToMaya������ؿ���ʧ�ܡ�',
                                button=['ȷ��', '�����������'])
        if rest == u'�����������':
            mm.eval('PluginManager;')

def add_adPose_ui():
    from adPose import ui
    ui.show_in_maya()
    fb_print('�Ѽ���adPose����', info=True, path=__file__, line=lin.f_lineno)