# -*- coding:GBK -*-
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

import sys
import os

from feedback_tool import Feedback_info as fb_print

if sys.version_info.major == 3:
    #������Ϊpy3ʱ
    from importlib import reload


class Rig_Menu(object):
    def __init__(self):
        self.menu_n = 'menu_ui'
        self.create_menu()

    def create_menu(self):
        mainWindow = pm.language.melGlobals['gMainWindow']
        master_menu = pm.menu(self.menu_n, to=True, l=u'�󶨹��߼�', p=mainWindow)

        pm.menuItem(to=True, p=master_menu, l=u'ˢ�²˵�', i='refresh.png', c='import reload_tools;'
                                                                             'reload(reload_tools);'
                                                                             'reload_tools.reload_menu_ui()')
        pm.menuItem(d=1, dl='ADV����', p=master_menu, )
        rig_adv = pm.menuItem(to=True, p=master_menu, l='ADV', sm=True)
        pm.menuItem(d=1, dl='��������', p=master_menu)
        self.tool_menu(master_menu)
        rig_clear = pm.menuItem(to=True, p=master_menu, l=u'ģ������', i='polyCleanup.png', sm=True)
        pm.menuItem(d=1, dl='��������', p=master_menu)
        menu_import = pm.menuItem(to=True, p=master_menu, l=u'����', i='import.png')
        menu_export = pm.menuItem(to=True, p=master_menu, l=u'����', i='export.png', sm=True)
        pm.menuItem(d=1, dl='�ϴ�����', p=master_menu)
        menu_push = pm.menuItem(to=True, p=master_menu, l=u'�ϴ�', i='pushToServer.png', sm=True)
        pm.menuItem(d=1, dl='��������', p=master_menu)
        menu_clr = pm.menuItem(to=True, p=master_menu, l=u'������', i='error.png', sm=True)
        pm.menuItem(d=1, dl='������', p=master_menu, )
        menu_wps = pm.menuItem(to=True, p=master_menu, l=u'�򿪹�����', i='wps.png', sm=True)
        pm.menuItem(d=1, dl='svn����', p=master_menu, )
        menu_svn = pm.menuItem(to=True, p=master_menu, l=u'svn����', i='svn_logo.png', sm=True)
        ##########################################################
        self.adv_menu(rig_adv)
        self.port(menu_export)
        self.push(menu_push)
        self.mod_clear(rig_clear)
        self.scene_clear(menu_clr)
        self.set_wps(menu_wps)
        self.set_svn(menu_svn)

    def adv_menu(self, p_menu):
        pm.menuItem(to=True, p=p_menu, i='AS5.png', l='ADV5', c="from ui import advTools;"
                                                                "reload(advTools);"
                                                                "advTools.openAdvTool();")
        pm.menuItem(to=True, p=p_menu, i='AS5.png', l='ADV5',
                    c="mm.eval('source \"C:/Rig_Tools/plug_ins/ADV/AdvancedSkeleton5.mel\";AdvancedSkeleton5;')")
        pm.menuItem(to=True, p=p_menu, i='asBiped.png', l='biped',
                    c="mm.eval('source \"C:/Rig_Tools/plug_ins/ADV/AdvancedSkeleton5Files/Selector/biped.mel\";')")
        pm.menuItem(to=True, p=p_menu, i='asFace.png', l='face',
                    c="mm.eval('source \"C:/Rig_Tools/plug_ins/ADV/AdvancedSkeleton5Files/Selector/face.mel\";')")
        pm.menuItem(to=True, p=p_menu, i='picker.png', l='picker',
                    c="mm.eval('source \"C:/Rig_Tools/plug_ins/ADV/AdvancedSkeleton5Files/picker/picker.mel\";')")

    def tool_menu(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'������������', i='ctl_tool.png', c='import controller_tool;'
                                                                              'reload(controller_tool);')
        pm.menuItem(to=True, p=p_menu, l=u'���ļ����ݲ���', i='moveShelfDown.png', c='import transform_matrerl;'
                                                                                     'reload(transform_matrerl);')
        pm.menuItem(to=True, p=p_menu, l=u'Meta������', i='MS_Logo.png', c='from ui import MeTa_Training_win;'
                                                                           'reload(MeTa_Training_win);')
        pm.menuItem(to=True, p=p_menu, l=u'��í��', i='follicle.png', c='import rivet_tool;'
                                                                        'reload(rivet_tool);')
        pm.menuItem(to=True, p=p_menu, l=u'�Ĵ�������', i='tape.png', c='import trackTool;'
                                                                        'reload(trackTool);')
        pm.menuItem(to=True, p=p_menu, l=u'��������', i='link_tool.png', c='import batch_connect_tool;'
                                                                           'reload(batch_connect_tool);'
                                                                           'batch_connect_tool.main()')
        pm.menuItem(to=True, p=p_menu, l=u'����Ȩ��', i='copySkinWeights.png', c='import transformSkinWeight;'
                                                                                 'reload(transformSkinWeight)')
        pm.menuItem(to=True, p=p_menu, i='studio_library.png', l='��studio_library', c='import toos_starter;'
                                                                                         'toos_starter.open_studioLibrary();')

    def port(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'����SM�ļ�', i='export_sm.jpg', c='import port_tool;'
                                                                             'reload(port_tool);'
                                                                             'port_tool.export_SM();')

    def push(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'�ϴ�rig��cgt', i='push_rig.png',
                    ann='cgt���滻���ߣ������ύ�ͼ򵥵��ļ�����',
                    c='import pushScence_tool;reload(pushScence_tool);pushScence_tool.push_rig();')

    def mod_clear(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'����������', c='from dutils import clearUtils;'
                                                          'reload(clearUtils);'
                                                          'clearUtils.clear_name()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯѡ������ķ��ı���', c='import rig_clear;'
                                                                      'reload(rig_clear);'
                                                                      'rig_clear.clear_face()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯѡ�ж���ı߽��', c='import rig_clear;'
                                                                    'reload(rig_clear);'
                                                                    'rig_clear.clear_boundary()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯ����������ģ�͵ķǶ�������', c='import rig_clear;'
                                                                              'reload(rig_clear);'
                                                                              'rig_clear.clear_frozen()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯ���������ʷ', c='import rig_clear;'
                                                                'reload(rig_clear);'
                                                                'rig_clear.clear_history()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯѡ�ж������͵�', c='import rig_clear;'
                                                                    'reload(rig_clear);'
                                                                    'rig_clear.clear_minimum()')

    def aim_menu(self, p_menu):
        pm.menuItem(to=True, p=p_menu, i='studio_library.png', l='��studio_library',
                    c='from sx_toolBOX.SX_aim import run_studio_library;'
                      'reload(run_studio_library)')

    def scene_clear(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'�Ҳ������̡�look��', c='import clear_errors;'
                                                                'reload(clear_errors);'
                                                                'clear_errors.clear_look()')
        pm.menuItem(to=True, p=p_menu, l=u'�Ҳ������̡�onModelChange��', c='import clear_errors;'
                                                                         'reload(clear_errors);'
                                                                         'clear_errors.clear_onModelChange()')
        pm.menuItem(to=True, p=p_menu, l=u'�Ҳ�������shaderBallOrthoCamera1��',
                    c='import clear_errors;'
                      'reload(clear_errors);'
                      'clear_errors.clear_shaderBallOrthoCamera1()')

    def set_wps(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l='�򿪹�����¼��', i='excel.png',
                    c='os.startfile("Z:/ɽ�̶���-����ĵ�/��FHZJ��/�ʲ�-UE��ͨ�Խ�/���鹤����¼.xlsx")')
        pm.menuItem(to=True, p=p_menu, l='��FBX��¼��', i='excel.png',
                    c='os.startfile("Z:/ɽ�̶���-����ĵ�/��XXTT��/�ʲ�-UE��ͨ�Խ�/�ʲ�SVN-FBX��¼��.xlsx")')
        pm.menuItem(to=True, p=p_menu, l='��XXTT�ʲ�������', i='excel.png',
                    c='os.startfile("Z:/ɽ�̶���-����ĵ�/��XXTT��/�ʲ�-UE��ͨ�Խ�/ʱ���ʲ�������.xlsx")')

    def set_svn(self, p_menu):
        def upData_rigMenu(*args):
            import svn_tool
            svn_tool.svn_upData()

        def edition_info(*args):
            import svn_tool
            svn_tool.svn_info()

        def get_logs(*args):
            import svn_tool
            svn_tool.svn_logs()

        pm.menuItem(to=True, p=p_menu, l=u'ͬ�����߼�', i='svn_synchronization.png', c=upData_rigMenu)
        pm.menuItem(to=True, p=p_menu, l=u'��ӡ���ع��߼ܰ汾��Ϣ', i='svn_info.png', c=edition_info)
        pm.menuItem(to=True, p=p_menu, l=u'��ӡ�������ύ��־', i='svn_log.png', c=get_logs)
