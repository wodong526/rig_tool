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


def reload_menu():
    try:
        from ui import menu_ui
        menu_ui.Rig_Menu()
        fb_print('�˵�ˢ�³ɹ�', info=True, viewMes=True)
    except:
        fb_print('�˵�ˢ��ʧ��', error=True, viewMes=True)

class Rig_Menu(object):
    def __init__(self):
        self.menu_n = 'sanXiaoYingHua'
        self.create_menu()

    def create_menu(self):
        mainWindow = pm.language.melGlobals['gMainWindow']
        try:
            if mc.menu(self.menu_n, ex=True):
                mc.deleteUI(self.menu_n)
        except:
            pass
        else:
            pass
        finally:
            mainWindow = pm.language.melGlobals['gMainWindow']
            master_menu = pm.menu(self.menu_n, to=True, l=u'�󶨹��߼�', p=mainWindow)

            pm.menuItem(to=True, p=master_menu, l=u'ˢ�²˵�', i='refresh.png',
                        c='from ui import menu_ui;'
                          'reload(menu_ui);'
                          'menu_ui.reload_menu()')
            pm.menuItem(d=1, dl='ADV����', p=master_menu, )
            rig_adv = pm.menuItem(to=True, p=master_menu, l='ADV', sm=True)
            pm.menuItem(d=1, dl='��������', p=master_menu)
            self.tool_menu(master_menu)
            rig_clear = pm.menuItem(to=True, p=master_menu, l=u'ģ������', i='polyCleanup.png', sm=True)
            pm.menuItem(d=1, dl='��������', p=master_menu, i='port.jpg')
            menu_import = pm.menuItem(to=True, p=master_menu, l=u'����', i='import.png')
            menu_export = pm.menuItem(to=True, p=master_menu, l=u'����', i='export.png', sm=True)
            pm.menuItem(d=1, dl='��������', p=master_menu)
            menu_clr = pm.menuItem(to=True, p=master_menu, l=u'������', i='error.png', sm=True)
            pm.menuItem(d=1, dl='������', p=master_menu, )
            menu_wps = pm.menuItem(to=True, p=master_menu, l=u'�򿪹�����', i='wps.png', sm=True)
            pm.menuItem(d=1, dl='svn����', p=master_menu, )
            menu_svn = pm.menuItem(to=True, p=master_menu, l=u'svn����', i='svn_logo.png', sm=True)
            ##########################################################
            self.adv_menu(rig_adv)
            self.port(menu_export)
            self.mod_clear(rig_clear)
            self.scene_clear(menu_clr)
            self.set_wps(menu_wps)
            self.set_svn(menu_svn)

    def adv_menu(self, p_menu):
        pm.menuItem(to=True, p=p_menu, i='AS5.png', l='ADV5',
                    c="mel.eval('source \"C:/Rig_Tools\/plug_ins/ADV/AdvancedSkeleton5.mel\";AdvancedSkeleton5;')")
        pm.menuItem(to=True, p=p_menu, i='asBiped.png', l='biped',
                    c="mel.eval('source \"C:/Rig_Tools\/plug_ins/ADV/AdvancedSkeleton5Files/Selector/biped.mel\";')")
        pm.menuItem(to=True, p=p_menu, i='asFace.png', l='face',
                    c="mel.eval('source \"C:/Rig_Tools\/plug_ins/ADV/AdvancedSkeleton5Files/Selector/face.mel\";')")
        pm.menuItem(to=True, p=p_menu, i='picker.png', l='picker',
                    c="mel.eval('source \"C:/Rig_Tools\/plug_ins/ADV/AdvancedSkeleton5Files/picker/picker.mel\";')")

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
        pm.menuItem(to=True, p=p_menu, i='studio_library.png', l='��studio_library', c='import toos_starter;'
                                                                                         'toos_starter.open_studioLibrary();')

    def port(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'����SM�ļ�', i='export_sm.jpg', c='import port_tool;'
                                                                            'reload(port_tool);'
                                                                            'port_tool.export_SM();')

    def mod_clear(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'����������', c='import rig_clear;'
                                                          'reload(rig_clear);'
                                                          'rig_clear.clear_name()')
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

    def set_wps(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l='�򿪹�����¼��', i='excel.png',
                    c='os.startfile("Z:/ɽ�̶���-����ĵ�/��FHZJ��/�ʲ�-UE��ͨ�Խ�/���鹤����¼.xlsx")')
        pm.menuItem(to=True, p=p_menu, l='��FBX��¼��', i='excel.png',
                    c='os.startfile("Z:/ɽ�̶���-����ĵ�/��FHZJ��/�ʲ�-UE��ͨ�Խ�/�ʲ�SVN-FBX��¼��.xlsx")')
        pm.menuItem(to=True, p=p_menu, l='��7��16���ʲ�������', i='excel.png',
                    c='os.startfile("Z:/ɽ�̶���-����ĵ�/��FHZJ��/�ʲ�-UE��ͨ�Խ�/�ʲ�ͳ��������EP07~EP16.xlsx")')

    def set_svn(self, p_menu):
        import svn_tool
        def upData_rigMenu(*args):
            svn_tool.svn_upData()
        def edition_info(*args):
            svn_tool.svn_info()

        pm.menuItem(to=True, p=p_menu, l=u'ͬ�����߼�', i='svn_synchronization.png', c=upData_rigMenu)
        pm.menuItem(to=True, p=p_menu, l=u'��ӡ���ع��߼ܰ汾��Ϣ', i='svn_info.png', c=edition_info)

