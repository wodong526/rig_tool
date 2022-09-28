# -*- coding:GBK -*- 
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mel
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def reload_menu():
    try:
        from sx_toolBOX.SX_rig import menu_ui
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
            master_menu = pm.menu(self.menu_n, to=True, l=u'ɽ��ӳ��', p=mainWindow)

            pm.menuItem(to=True, p=master_menu, l=u'ˢ�²˵�', i='refresh.png',
                        c='from sx_toolBOX.SX_rig import menu_ui;'
                          'reload(menu_ui);'
                          'menu_ui.reload_menu()')
            pm.menuItem(d=1, dl='break', p=master_menu, )
            menu_rig = pm.menuItem(to=True, p=master_menu, l=u'��', i='kinJoint.png', sm=True)
            pm.menuItem(d=1, dl='break', p=master_menu, )
            menu_aim = pm.menuItem(to=True, p=master_menu, l=u'����', i='setKeyframe.png')
            pm.menuItem(d=1, dl='break', p=master_menu, )
            menu_mod = pm.menuItem(to=True, p=master_menu, l=u'��ģ', i='polyCube.png', sm=True)
            pm.menuItem(d=1, dl='break', p=master_menu, )
            menu_clr = pm.menuItem(to=True, p=master_menu, l=u'������', i='error.png', sm=True)
            ##########################################################
            rig_adv = pm.menuItem(to=True, p=menu_rig, l='ADV', sm=True)
            pm.menuItem(to=True, p=rig_adv, i='AS5.png', l='ADV5.690',
                        c="mel.eval('source \"D:/adv/AdvancedSkeleton5.mel\";AdvancedSkeleton5;')")
            pm.menuItem(to=True, p=rig_adv, i='asBiped.png', l='biped',
                        c="mel.eval('source \"D:/adv/AdvancedSkeleton5Files/Selector/biped.mel\";')")
            pm.menuItem(to=True, p=rig_adv, i='asFace.png', l='face',
                        c="mel.eval('source \"D:/adv/AdvancedSkeleton5Files/Selector/face.mel\";')")
            pm.menuItem(to=True, p=rig_adv, i='picker.png', l='picker',
                        c="mel.eval('source \"D:/adv/AdvancedSkeleton5Files/picker/picker.mel\";')")

            pm.menuItem(d=1, dl=u'����', p=menu_rig)
            pm.menuItem(to=True, p=menu_rig, l=u'������������', i='ctl_tool.png',
                        c='from sx_toolBOX.SX_rig import controller_tool;'
                          'reload(controller_tool);')
            pm.menuItem(to=True, p=menu_rig, l=u'���ļ����ݲ���', i='moveShelfDown.png',
                        c='from sx_toolBOX.SX_rig import material_transform;'
                          'reload(material_transform);')
            pm.menuItem(to=True, p=menu_rig, l=u'Meta������', i='meta_trsform_head.png',
                        c='from sx_toolBOX.SX_rig.rig_window import MeTa_Training_win;'
                          'reload(MeTa_Training_win);')
            pm.menuItem(to=True, p=menu_rig, l=u'metaͷ���任', i='meta_trsform_head.png',
                        c='from sx_toolBOX.SX_rig import metaHuman_transformation_head;'
                          'reload(metaHuman_transformation_head);')
            pm.menuItem(to=True, p=menu_rig, l=u'��í��', i='meta_trsform_head.png',
                        c="mel.eval('source \"C:/Users/Administrator/Documents/maya/2018/scripts/sx_toolBOX/SX_rig/check.mel\";')")
            pm.menuItem(to=True, p=menu_rig, l=u'�Ĵ�������', i='meta_trsform_head.png',
                        c='from sx_toolBOX.SX_rig import trackTool;'
                          'reload(trackTool);')

            pm.menuItem(d=1, dl=u'��������', p=menu_rig)
            rig_clear = pm.menuItem(to=True, p=menu_rig, l=u'ģ������', i='polyCleanup.png', sm=True)
            pm.menuItem(to=True, p=rig_clear, l=u'����������', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                                   'reload(rig_clear);'
                                                                   'rig_clear.clear_name()')
            pm.menuItem(to=True, p=rig_clear, l=u'��ѯѡ������ķ��ı���', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                                             'reload(rig_clear);'
                                                                             'rig_clear.clear_face()')
            pm.menuItem(to=True, p=rig_clear, l=u'��ѯѡ�ж���ı߽��', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                                           'reload(rig_clear);'
                                                                           'rig_clear.clear_boundary()')
            pm.menuItem(to=True, p=rig_clear, l=u'��ѯѡ�ж���ķǶ�������',
                        c='from sx_toolBOX.SX_rig import rig_clear;'
                          'reload(rig_clear);'
                          'rig_clear.clear_frozen()')
            pm.menuItem(to=True, p=rig_clear, l=u'��ѯ���������ʷ', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                                       'reload(rig_clear);'
                                                                       'rig_clear.clear_history()')
            pm.menuItem(to=True, p=rig_clear, l=u'��ѯѡ�ж������͵�', c='from sx_toolBOX.SX_rig import rig_clear;'
                                                                           'reload(rig_clear);'
                                                                           'rig_clear.clear_minimum()')

            pm.menuItem(to=True, p=menu_clr, l=u'�Ҳ������̡�look��', c='from sx_toolBOX.SX_tool import clear_errors;'
                                                                      'reload(clear_errors);'
                                                                      'clear_errors.clear_look()')
            pm.menuItem(to=True, p=menu_clr, l=u'�Ҳ������̡�onModelChange��',
                        c='from sx_toolBOX.SX_tool import clear_errors;'
                          'reload(clear_errors);'
                          'clear_errors.clear_onModelChange()')
            ##########################################################
            pm.menuItem(to=True, p=menu_mod, l=u'����������', i='renamePreset.png',
                        c='from sx_toolBOX.SX_mod import rename_tool;'
                          'reload(rename_tool);')