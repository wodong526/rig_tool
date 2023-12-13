# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import sys

from feedback_tool import Feedback_info as fb_print

if sys.version_info.major == 3:
    #������Ϊpy3ʱ
    from importlib import reload


class Rig_HotBox(object):
    """
    �����Ⱥ�
    """
    def __init__(self):
        self.heatBox_n = 'hot_box_ui'
        self._build()

    def _build(self):
        menu = mc.popupMenu(self.heatBox_n, mm=1, b=3, aob=1, ctl=1, alt=1, sh=0, p='viewPanes', pmo=1,
                            pmc=self._buildMenu)

    def _buildMenu(self, menu, *args):
        mc.popupMenu(self.heatBox_n, e=True, dai=True)
        sundry_menu = mc.menuItem(p=menu, l='����', rp='N', sm=1)
        self.menu_sundry(sundry_menu)

        except_menu = mc.menuItem(p=menu, l='����ǰ', rp='NE', sm=1)
        self.menu_except(except_menu)

        loc_menu = mc.menuItem(p=menu, l='��λ��', rp='W', subMenu=1)
        self.menu_loc(loc_menu)

        jnt_menu = mc.menuItem(p=menu, l='�ؽ�', rp='E', sm=1)
        self.menu_jnt(jnt_menu)

        get_menu = mc.menuItem(p=menu, l='��ȡ', rp='SW', sm=1)
        self.menu_get(get_menu)

        mc.menuItem(p=menu, l='ˢ���Ⱥ�', c='import reload_tools;'
                                            'reload(reload_tools);'
                                            'reload_tools.reload_hot_ui()')
        mc.menuItem(d=True, p=menu)
        mc.menuItem(p=menu, l='���ϴ�����', c='import pushScence_tool;'
                                                'reload(pushScence_tool);'
                                                'pushScence_tool.push_rig();')
        mc.menuItem(d=True, p=menu)
        mc.menuItem(p=menu, l='����meta�ű�', c='import reload_tools;'
                                                'reload(reload_tools);'
                                                'reload_tools.add_metaToMata_plug();')
        mc.menuItem(p=menu, l='����adPose', c='import reload_tools;'
                                              'reload(reload_tools);'
                                              'reload_tools.add_adPose_ui();')
        mc.menuItem(p=menu, l='�򿪲��������', c="mm.eval('PluginManager;')")
        mc.menuItem(p=menu, l='��������', c='from ui import faceUi;'
                                            'reload(faceUi);')

    def menu_sundry(self, parent):
        mc.menuItem(p=parent, l='��', rp='N')
        mc.menuItem(p=parent, l='����ѡ�ж����orig�ڵ�', rp='NE', c='from dutils import toolUtils;'
                                                                     'reload(toolUtils);'
                                                                     'toolUtils.clear_orig()')
        mc.menuItem(p=parent, l='����ѡ�йؽڵ���ת', rp='W', c='import rig_tool;'
                                                                'reload(rig_tool);'
                                                                'rig_tool.freeze_rotation()')
        mc.menuItem(p=parent, l='�򿪻�رն��������', rp='NW', c='mc.ToggleLocalRotationAxes()')
        mc.menuItem(p=parent, l='��ƥ��һ', rp='SE', c='import rig_location;'
                                                       'reload(rig_location);'
                                                       'rig_location.allMatchOne()')
        mc.menuItem(p=parent, l='һƥ���', rp='E', c='import rig_location;'
                                                      'reload(rig_location);'
                                                      'rig_location.oneMatchAll()')

    def menu_except(self, parent):
        mc.menuItem(p=parent, l='������ǰѡ��Ϊfbx', rp='S', c='import rig_tool;'
                                                               'reload(rig_tool);'
                                                               'rig_tool.exportSelectToFbx();')
        mc.menuItem(p=parent, l='��ȡ��������', rp='N', c='from dutils import clearUtils;'
                                                          'reload(clearUtils);'
                                                          'clearUtils.clear_name()')
        mc.menuItem(p=parent, l='���������пռ���', rp='NW', c='from dutils import clearUtils;'
                                                                 'reload(clearUtils);'
                                                                 'clearUtils.clear_nameSpace()')
        mc.menuItem(p=parent, l='�������ؼ�֡', rp='NE', c='from dutils import clearUtils;'
                                                             'reload(clearUtils);'
                                                             'clearUtils.clear_key()')
        mc.menuItem(p=parent, l='������������', rp='E', c='from dutils import clearUtils;'
                                                            'reload(clearUtils);'
                                                            'clearUtils.clear_animLayer()')
        mc.menuItem(p=parent, l='������HIK', rp='SE', c='from dutils import clearUtils;'
                                                          'reload(clearUtils);'
                                                          'clearUtils.clear_hik()')

    def menu_jnt(self, parent):
        mc.menuItem(p=parent, l='�����ؽڹ���', rp='N', c='mc.JointTool()')
        mc.menuItem(p=parent, l='�ؽ���ʾ��С', rp='S', c=lambda _: mm.eval("jdsWin;"))
        mc.menuItem(p=parent, l='�����ؽڲ�ƥ����ת', rp='NE', c='import rig_location;'
                                                                 'reload(rig_location);'
                                                                 'rig_location.create_joint()')
        mc.menuItem(p=parent, l='�����ؽڵ�ѡ����������', rp='E', c='import rig_location;'
                                                                      'reload(rig_location);'
                                                                      'rig_location.get_jnt_core()')
        mc.menuItem(p=parent, l='ʹ��brSmooth', rp='SE', c='import rig_tool;'
                                                           'reload(rig_tool);'
                                                           'rig_tool.brSmoothTool()')

    def menu_get(self, parent):
        mc.menuItem(p=parent, l='��ȡѡ�ж������Ƥ�ؽ�', rp='W', c='import rig_tool;'
                                                                    'reload(rig_tool);'
                                                                    'rig_tool.select_skinJoint()')
        mc.menuItem(p=parent, l='ѡ�и��������', rp='NW', c='import rig_tool;'
                                                             'reload(rig_tool);'
                                                             'rig_tool.get_length()')
        mc.menuItem(p=parent, l='ѡ��ͬ���ڵ�', rp='SW', c='import rig_tool;'
                                                           'reload(rig_tool);'
                                                           'rig_tool.selectSameName()')
        mc.menuItem(p=parent, l='�ص�ADVԭʼ����', rp='S', c='from dutils import toolUtils;'
                                                             'reload(toolUtils);'
                                                             'toolUtils.goToADV_pose()')

    def menu_loc(self, parent):
        mc.menuItem(p=parent, l='������λ��������', rp='W', c='import rig_location;'
                                                              'reload(rig_location);'
                                                              'rig_location.get_core()')
        mc.menuItem(p=parent, l='������λ��Ŀ�겢ƥ����ת', rp='NW', c='import rig_location;'
                                                                       'reload(rig_location);'
                                                                       'rig_location.get_trm_rot()')
