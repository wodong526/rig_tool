# -*- coding:GBK -*-
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mel
import sys
import os
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

if sys.version_info.major == 3:
    #������Ϊpy3ʱ
    from importlib import reload

def reload_menu():
    try:
        from sx_toolBOX.SX_rig.rig_window import menu_ui
        reload(menu_ui)
        menu_ui.SX_Menu()
        log.info(u'�˵�ˢ�³ɹ�')
    except:
        log.error(u'�˵�ˢ��ʧ��')


class SX_Menu(object):
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
            master_menu = pm.menu(self.menu_n, to=True, l=u'ɽ�̶���', p=mainWindow, c=last_fu)

            # pm.menuItem(to=True, p=master_menu, l=u'ˢ�²˵�', i='refresh.png',
            #             c='from sx_toolBOX.SX_rig.rig_window import menu_ui;'
            #               'reload(menu_ui);'
            #               'menu_ui.reload_menu()')
            # pm.menuItem(d=1, dl='break', p=master_menu, )
            # menu_rig = pm.menuItem(to=True, p=master_menu, l=u'��', i='kinJoint.png', sm=True)
            # menu_aim = pm.menuItem(to=True, p=master_menu, l=u'����', i='setKeyframe.png', sm=True)
            # menu_mod = pm.menuItem(to=True, p=master_menu, l=u'��ģ', i='polyCube.png')
            # pm.menuItem(d=1, dl='break', p=master_menu, )
            # menu_clr = pm.menuItem(to=True, p=master_menu, l=u'������', i='error.png', sm=True)
            # ##########################################################
            # self.rig_menu(menu_rig)
            # self.aim_menu(menu_aim)
            # self.scene_clear(menu_clr)

    def rig_menu(self, p_menu):
        rig_adv = pm.menuItem(to=True, p=p_menu, l='ADV', sm=True)
        pm.menuItem(d=1, dl=u'����', p=p_menu)
        pm.menuItem(to=True, p=p_menu, l=u'������������', i='ctl_tool.png',
                    c='from sx_toolBOX.SX_rig import controller_tool;'
                      'reload(controller_tool);')
        pm.menuItem(to=True, p=p_menu, l=u'���ļ����ݲ���', i='moveShelfDown.png',
                    c='from sx_toolBOX.SX_rig import transform_matrerl;'
                      'reload(transform_matrerl);')
        pm.menuItem(to=True, p=p_menu, l=u'Meta������', i='meta_trsform_head.png',
                    c='from sx_toolBOX.SX_rig.rig_window import MeTa_Training_win;'
                      'reload(MeTa_Training_win);')
        pm.menuItem(to=True, p=p_menu, l=u'��í��', i='meta_trsform_head.png',
                    c='from sx_toolBOX.SX_rig import rivet_tool; reload(rivet_tool);')
        pm.menuItem(to=True, p=p_menu, l=u'�Ĵ�������', i='meta_trsform_head.png',
                    c='from sx_toolBOX.SX_rig import trackTool;'
                      'reload(trackTool);')
        pm.menuItem(to=True, p=p_menu, l=u'��������', i='link_tool.png',
                    c='from sx_toolBOX.SX_rig import batch_connect_tool;'
                      'reload(batch_connect_tool);'
                      'batch_connect_tool.main()')
        pm.menuItem(d=1, dl=u'��������', p=p_menu)
        rig_clear = pm.menuItem(to=True, p=p_menu, l=u'ģ������', i='polyCleanup.png', sm=True)
        self.adv_menu(rig_adv)
        self.mod_clear(rig_clear)

    def adv_menu(self, p_menu):
        pm.menuItem(to=True, p=p_menu, i='AS5.png', l='ADV5',
                    c="mel.eval('source \"Z:/Library/rig_plug_in/maya_plug/data/ADV/AdvancedSkeleton5.mel\";AdvancedSkeleton5;')")
        pm.menuItem(to=True, p=p_menu, i='asBiped.png', l='biped',
                    c="mel.eval('source \"Z:/Library/rig_plug_in/maya_plug/data/ADV/AdvancedSkeleton5Files/Selector/biped.mel\";')")
        pm.menuItem(to=True, p=p_menu, i='asFace.png', l='face',
                    c="mel.eval('source \"Z:/Library/rig_plug_in/maya_plug/data/ADV/AdvancedSkeleton5Files/Selector/face.mel\";')")
        pm.menuItem(to=True, p=p_menu, i='picker.png', l='picker',
                    c="mel.eval('source \"Z:/Library/rig_plug_in/maya_plug/data/ADV/AdvancedSkeleton5Files/picker/picker.mel\";')")

    def mod_clear(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'����������', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                               'reload(rig_clear);'
                                                               'rig_clear.clear_name()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯѡ������ķ��ı���', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                                         'reload(rig_clear);'
                                                                         'rig_clear.clear_face()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯѡ�ж���ı߽��', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                                       'reload(rig_clear);'
                                                                       'rig_clear.clear_boundary()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯ����������ģ�͵ķǶ�������',
                    c='from sx_toolBOX.SX_rig import rig_clear;'
                      'reload(rig_clear);'
                      'rig_clear.clear_frozen()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯ���������ʷ', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                                   'reload(rig_clear);'
                                                                   'rig_clear.clear_history()')
        pm.menuItem(to=True, p=p_menu, l=u'��ѯѡ�ж������͵�', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                                       'reload(rig_clear);'
                                                                       'rig_clear.clear_minimum()')

    def aim_menu(self, p_menu):
        pm.menuItem(to=True, p=p_menu, i='studio_library.png', l='��studio_library', 
                    c='from sx_toolBOX.SX_aim import run_studio_library;'
                      'reload(run_studio_library)')

    def scene_clear(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'�Ҳ������̡�look��', c='from sx_toolBOX.SX_tool import clear_errors;'
                                                                  'reload(clear_errors);'
                                                                  'clear_errors.clear_look()')
        pm.menuItem(to=True, p=p_menu, l=u'�Ҳ������̡�onModelChange��',
                    c='from sx_toolBOX.SX_tool import clear_errors;'
                      'reload(clear_errors);'
                      'clear_errors.clear_onModelChange()')

    def last_fu(self):
        rest = mc.confirmDialog(title='�޷��򿪴���',
                                message='�����߼��Ѿ�����\nʹ���µĹ��߼��������򿪹��߼ܰ�װ��·�����󣬽��Լ���λ��Ӧ�İ�װ���ļ��Ϸŵ�Maya��3d�Ӵ��ڡ�',
                                button=['֪����', '�򿪹��߼ܰ�װ��·��'], defaultButton='Yes', cancelButton='No',
                                dismissString='No')
        if rest == u'�򿪹��߼ܰ�װ��·��':
            os.system('explorer /select, Z:\Library\\rig_plug_in\Maya_openTools\Rig_install.py')