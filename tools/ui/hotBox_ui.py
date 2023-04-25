 # -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import sys

from feedback_tool import Feedback_info as fb_print

if sys.version_info.major == 3:
    #������Ϊpy3ʱ
    from importlib import reload

def rebuild_rotBox(*args):
    try:
        from ui import hotBox_ui
        reload(hotBox_ui)
        hotBox_ui.Rig_HotBox()
        fb_print('�Ⱥ�ˢ�³ɹ�', info=True, viewMes=True)
    except:
        fb_print('�Ⱥ�ˢ��ʧ��', error=True, viewMes=True)

class Rig_HotBox(object):
    '''
    �����Ⱥ�
    '''
    def __init__(self):
        self.heatBox_n = 'hot_box'
        self._removeOld()
        self._build()

    def _removeOld(self):
        if mc.popupMenu(self.heatBox_n, ex=1):
            mc.deleteUI(self.heatBox_n)

    def _build(self):
        menu = mc.popupMenu(self.heatBox_n, mm=1, b=3, aob=1, ctl=1, alt=1, sh=0, p='viewPanes', pmo=1,
                            pmc=self._buildMenu)

    def _buildMenu(self, menu, *args):
        mc.popupMenu(self.heatBox_n, e=True, dai=True)
        sundry_menu = mc.menuItem(p=menu, l=u'����', rp='N', sm=1)
        self.menu_sundry(sundry_menu)

        except_menu = mc.menuItem(p=menu, l=u'����ǰ', rp='NE', sm=1)
        self.menu_except(except_menu)

        loc_menu = mc.menuItem(p=menu, l='��λ��', rp='W', subMenu=1)
        self.menu_loc(loc_menu)

        jnt_menu = mc.menuItem(p=menu, l='�ؽ�', rp='E', sm=1)
        self.menu_jnt(jnt_menu)

        get_menu = mc.menuItem(p=menu, l=u'��ȡ', rp='SW', sm=1)
        self.menu_get(get_menu)

        mc.menuItem(p=menu, l='ˢ���Ⱥ�', c=rebuild_rotBox)
        mc.menuItem(d=True, p=menu)
        mc.menuItem(p=menu, l='����meta�ű�', c='import pulg_ins;'
                                               'reload(pulg_ins);'
                                               'pulg_ins.add_metaToMata_plug();')
        mc.menuItem(p=menu, l='����adPose', c='import pulg_ins;'
                                              'reload(pulg_ins);'
                                              'pulg_ins.add_adPose_ui();')

    def menu_sundry(self, parent):
        mc.menuItem(p=parent, l=u'��', rp='N')
        mc.menuItem(p=parent, l=u'����ѡ�ж����orig�ڵ�', rp='NE', c='import rig_tool;'
                                                                   'reload(rig_tool);'
                                                                   'rig_tool.clear_orig()')
        mc.menuItem(p=parent, l=u'����ѡ�йؽڵ���ת', rp='W', c='import rig_tool;'
                                                              'reload(rig_tool);'
                                                              'rig_tool.freeze_rotation()')
        mc.menuItem(p=parent, l=u'�򿪻�رն��������', rp='NW', c='mc.ToggleLocalRotationAxes()')
        mc.menuItem(p=parent, l=u'����ƥ��', rp='SE', c='import rig_location;'
                                                       'reload(rig_location);'
                                                       'rig_location.match_transform()')

    def menu_except(self, parent):
        mc.menuItem(p=parent, l=u'������ǰѡ��Ϊfbx', rp='S', c='import rig_tool;'
                                                              'reload(rig_tool);'
                                                              'rig_tool.exportSelectToFbx();')
        mc.menuItem(p=parent, l=u'��ȡ��������', rp='N', c='import rig_clear;'
                                                         'reload(rig_clear);'
                                                         'rig_clear.clear_name()')
        mc.menuItem(p=parent, l=u'���������пռ���', rp='NW', c='import rig_clear;'
                                                               'reload(rig_clear);'
                                                               'rig_clear.clear_nameSpace()')
        mc.menuItem(p=parent, l=u'�������ؼ�֡', rp='NE', c='import rig_clear;'
                                                           'reload(rig_clear);'
                                                           'rig_clear.clear_key()')
        mc.menuItem(p=parent, l=u'������������', rp='E', c='import rig_clear;'
                                                          'reload(rig_clear);'
                                                          'rig_clear.clear_animLayer()')
        mc.menuItem(p=parent, l=u'������HIK', rp='SE', c='import rig_clear;'
                                                          'reload(rig_clear);'
                                                          'rig_clear.clear_hik()')

    def menu_jnt(self, parent):
        mc.menuItem(p=parent, l='�����ؽڹ���', rp='N', c='mc.JointTool()')
        mc.menuItem(p=parent, l='�ؽ���ʾ��С', rp='S', c=lambda _: mm.eval("jdsWin;"))
        mc.menuItem(p=parent, l='�����ؽڲ�ƥ����ת', rp='NE', c='import rig_location;'
                                                              'reload(rig_location);'
                                                              'rig_location.create_joint()')
        mc.menuItem(p=parent, l='�����ؽڵ�ѡ����������', rp='E', c='import rig_location;'
                                                                  'reload(rig_location);'
                                                                  'rig_location.get_jnt_core()')

    def menu_get(self, parent):
        mc.menuItem(p=parent, l=u'��ȡѡ�ж������Ƥ�ؽ�', rp='W', c='import rig_tool;'
                                                                 'reload(rig_tool);'
                                                                 'rig_tool.select_skinJoint()')
        mc.menuItem(p=parent, l=u'ѡ�и��������', rp='NW', c='import rig_tool;'
                                                            'reload(rig_tool);'
                                                            'rig_tool.get_length()')
        mc.menuItem(p=parent, l=u'ѡ��ͬ���ڵ�', rp='SW', c='import rig_tool;'
                                                          'reload(rig_tool);'
                                                          'rig_tool.showSameNameWindow()')
        mc.menuItem(p=parent, l=u'�ص�ADVԭʼ����', rp='S', c='import utils;'
                                                            'reload(utils);'
                                                            'utils.goToADV_pose();')

    def menu_loc(self, parent):
        mc.menuItem(p=parent, l=u'������λ��������', rp='W', c='import rig_location;'
                                                            'reload(rig_location);'
                                                            'rig_location.get_core()')
        mc.menuItem(p=parent, l=u'������λ��Ŀ�겢ƥ����ת', rp='NW', c='import rig_location;'
                                                                    'reload(rig_location);'
                                                                    'rig_location.get_trm_rot()')