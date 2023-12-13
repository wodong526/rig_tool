# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import sys

from feedback_tool import Feedback_info as fb_print

if sys.version_info.major == 3:
    #当环境为py3时
    from importlib import reload


class Rig_HotBox(object):
    """
    绑定用热盒
    """
    def __init__(self):
        self.heatBox_n = 'hot_box_ui'
        self._build()

    def _build(self):
        menu = mc.popupMenu(self.heatBox_n, mm=1, b=3, aob=1, ctl=1, alt=1, sh=0, p='viewPanes', pmo=1,
                            pmc=self._buildMenu)

    def _buildMenu(self, menu, *args):
        mc.popupMenu(self.heatBox_n, e=True, dai=True)
        sundry_menu = mc.menuItem(p=menu, l='杂项', rp='N', sm=1)
        self.menu_sundry(sundry_menu)

        except_menu = mc.menuItem(p=menu, l='导出前', rp='NE', sm=1)
        self.menu_except(except_menu)

        loc_menu = mc.menuItem(p=menu, l='定位器', rp='W', subMenu=1)
        self.menu_loc(loc_menu)

        jnt_menu = mc.menuItem(p=menu, l='关节', rp='E', sm=1)
        self.menu_jnt(jnt_menu)

        get_menu = mc.menuItem(p=menu, l='获取', rp='SW', sm=1)
        self.menu_get(get_menu)

        mc.menuItem(p=menu, l='刷新热盒', c='import reload_tools;'
                                            'reload(reload_tools);'
                                            'reload_tools.reload_hot_ui()')
        mc.menuItem(d=True, p=menu)
        mc.menuItem(p=menu, l='打开上传工具', c='import pushScence_tool;'
                                                'reload(pushScence_tool);'
                                                'pushScence_tool.push_rig();')
        mc.menuItem(d=True, p=menu)
        mc.menuItem(p=menu, l='加载meta脚本', c='import reload_tools;'
                                                'reload(reload_tools);'
                                                'reload_tools.add_metaToMata_plug();')
        mc.menuItem(p=menu, l='加载adPose', c='import reload_tools;'
                                              'reload(reload_tools);'
                                              'reload_tools.add_adPose_ui();')
        mc.menuItem(p=menu, l='打开插件管理器', c="mm.eval('PluginManager;')")
        mc.menuItem(p=menu, l='绑脸工具', c='from ui import faceUi;'
                                            'reload(faceUi);')

    def menu_sundry(self, parent):
        mc.menuItem(p=parent, l='无', rp='N')
        mc.menuItem(p=parent, l='清理选中对象的orig节点', rp='NE', c='from dutils import toolUtils;'
                                                                     'reload(toolUtils);'
                                                                     'toolUtils.clear_orig()')
        mc.menuItem(p=parent, l='冻结选中关节的旋转', rp='W', c='import rig_tool;'
                                                                'reload(rig_tool);'
                                                                'rig_tool.freeze_rotation()')
        mc.menuItem(p=parent, l='打开或关闭对象的轴向', rp='NW', c='mc.ToggleLocalRotationAxes()')
        mc.menuItem(p=parent, l='多匹配一', rp='SE', c='import rig_location;'
                                                       'reload(rig_location);'
                                                       'rig_location.allMatchOne()')
        mc.menuItem(p=parent, l='一匹配多', rp='E', c='import rig_location;'
                                                      'reload(rig_location);'
                                                      'rig_location.oneMatchAll()')

    def menu_except(self, parent):
        mc.menuItem(p=parent, l='导出当前选择为fbx', rp='S', c='import rig_tool;'
                                                               'reload(rig_tool);'
                                                               'rig_tool.exportSelectToFbx();')
        mc.menuItem(p=parent, l='获取场景重名', rp='N', c='from dutils import clearUtils;'
                                                          'reload(clearUtils);'
                                                          'clearUtils.clear_name()')
        mc.menuItem(p=parent, l='清理场景所有空间名', rp='NW', c='from dutils import clearUtils;'
                                                                 'reload(clearUtils);'
                                                                 'clearUtils.clear_nameSpace()')
        mc.menuItem(p=parent, l='清理场景关键帧', rp='NE', c='from dutils import clearUtils;'
                                                             'reload(clearUtils);'
                                                             'clearUtils.clear_key()')
        mc.menuItem(p=parent, l='清理场景动画层', rp='E', c='from dutils import clearUtils;'
                                                            'reload(clearUtils);'
                                                            'clearUtils.clear_animLayer()')
        mc.menuItem(p=parent, l='清理场景HIK', rp='SE', c='from dutils import clearUtils;'
                                                          'reload(clearUtils);'
                                                          'clearUtils.clear_hik()')

    def menu_jnt(self, parent):
        mc.menuItem(p=parent, l='创建关节工具', rp='N', c='mc.JointTool()')
        mc.menuItem(p=parent, l='关节显示大小', rp='S', c=lambda _: mm.eval("jdsWin;"))
        mc.menuItem(p=parent, l='创建关节并匹配旋转', rp='NE', c='import rig_location;'
                                                                 'reload(rig_location);'
                                                                 'rig_location.create_joint()')
        mc.menuItem(p=parent, l='创建关节到选择对象的中心', rp='E', c='import rig_location;'
                                                                      'reload(rig_location);'
                                                                      'rig_location.get_jnt_core()')
        mc.menuItem(p=parent, l='使用brSmooth', rp='SE', c='import rig_tool;'
                                                           'reload(rig_tool);'
                                                           'rig_tool.brSmoothTool()')

    def menu_get(self, parent):
        mc.menuItem(p=parent, l='获取选中对象的蒙皮关节', rp='W', c='import rig_tool;'
                                                                    'reload(rig_tool);'
                                                                    'rig_tool.select_skinJoint()')
        mc.menuItem(p=parent, l='选中个数与对象', rp='NW', c='import rig_tool;'
                                                             'reload(rig_tool);'
                                                             'rig_tool.get_length()')
        mc.menuItem(p=parent, l='选中同名节点', rp='SW', c='import rig_tool;'
                                                           'reload(rig_tool);'
                                                           'rig_tool.selectSameName()')
        mc.menuItem(p=parent, l='回到ADV原始姿势', rp='S', c='from dutils import toolUtils;'
                                                             'reload(toolUtils);'
                                                             'toolUtils.goToADV_pose()')

    def menu_loc(self, parent):
        mc.menuItem(p=parent, l='创建定位器到中心', rp='W', c='import rig_location;'
                                                              'reload(rig_location);'
                                                              'rig_location.get_core()')
        mc.menuItem(p=parent, l='创建定位到目标并匹配旋转', rp='NW', c='import rig_location;'
                                                                       'reload(rig_location);'
                                                                       'rig_location.get_trm_rot()')
