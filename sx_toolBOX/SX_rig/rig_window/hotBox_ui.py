# -*- coding:GBK -*- 
import maya.cmds as mc
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def rebuild_rotBox(*args):
    try:
        from sx_toolBOX.SX_rig.rig_window import hotBox_ui
        reload(hotBox_ui)
        hotBox_ui.SX_RotBox()
        log.info(u'热盒刷新成功')
    except:
        log.error(u'热盒刷新失败')



class SX_RotBox(object):
    '''
    绑定用热盒
    '''
    def __init__(self):
        self.heatBox_n = 'sx_rBox'
        self._removeOld()
        self._build()

    
    def _removeOld(self):
        if mc.popupMenu(self.heatBox_n, ex = 1):
            mc.deleteUI(self.heatBox_n)

    
    def _build(self):
        menu = mc.popupMenu(self.heatBox_n, mm = 1, b = 3, aob = 1, ctl = 1, alt = 1, sh = 0, p = 'viewPanes', pmo = 1, pmc = self._buildMenu)

    
    def _buildMenu(self, menu, *args):
        mc.popupMenu(self.heatBox_n, e = True, dai = True)
        sundry_menu = mc.menuItem(p = menu, l = u'杂项', rp = 'N', sm = 1)
        mc.menuItem(p = sundry_menu, l = u'无', rp = 'N')
        mc.menuItem(p = sundry_menu, l = u'清理选中对象的orig节点', rp = 'NE', c = 'from sx_toolBOX.SX_rig import rig_tool;'
                                                                                  'reload(rig_tool);'
                                                                                  'rig_tool.clear_orig()')
        mc.menuItem(p = sundry_menu, l = u'冻结选中对象的旋转', rp = 'W', c = 'from sx_toolBOX.SX_rig import rig_tool;'
                                                                             'reload(rig_tool);'
                                                                             'rig_tool.freeze_rotation()')
        mc.menuItem(p = sundry_menu, l = u'打开或关闭对象的轴向', rp = 'NW', c = 'mc.ToggleLocalRotationAxes()')
        mc.menuItem(p = sundry_menu, l = u'三轴匹配', rp = 'SE', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                     'reload(rig_location);'
                                                                     'rig_location.match_transform()')
        
        except_menu = mc.menuItem(p = menu, l = u'导出前', rp = 'NE', sm = 1)
        mc.menuItem(p = except_menu, l = u'自动', rp = 'S', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                'reload(rig_clear);reload(rig_clear);reload(rig_clear);'
                                                                'rig_clear.clear_uv(1);rig_clear.clear_material();rig_clear.clear_name()')
        mc.menuItem(p = except_menu, l = u'清理场景重名', rp = 'NE', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                        'reload(rig_clear);'
                                                                        'rig_clear.clear_name()')
        mc.menuItem(p = except_menu, l = u'查询可能重复的材质球', rp = 'NW', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                               'reload(rig_clear);'
                                                                               'rig_clear.clear_material()')
        mc.menuItem(p = except_menu, l = u'检查可能的uv位置错误', rp = 'N', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                               'reload(rig_clear);'
                                                                               'rig_clear.clear_uv(0)')
        mc.menuItem(p = except_menu, l = u'清理场景关键帧', rp = 'E', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                         'reload(rig_clear);'
                                                                         'rig_clear.clear_key()')
        
        subMenu = mc.menuItem(p = menu, l = '定位器', rp = 'W', subMenu = 1)
        mc.menuItem(p = subMenu, l = u'创建定位器到中心', rp = 'W', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                       'reload(rig_location);'
                                                                       'rig_location.get_core()')
        mc.menuItem(p = subMenu, l = u'创建定位到目标并匹配旋转', rp = 'NW', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                               'reload(rig_location);'
                                                                               'rig_location.get_trm_rot()')
        
        jnt_menu = mc.menuItem(p = menu, l = '关节', rp = 'E', sm = 1)
        mc.menuItem(p = jnt_menu, l = '创建关节工具', rp = 'N', c = 'mc.JointTool()')
        # mc.menuItem(p = jnt_menu, l = '创建关节到选择位', rp = 'E', c = 'from sx_toolBOX.SX_rig import rig_location;'
        #                                                                'reload(rig_location);'
        #                                                                'rig_location.get_jnt_trs()')
        mc.menuItem(p = jnt_menu, l = '创建关节并匹配旋转', rp = 'NE', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                          'reload(rig_location);'
                                                                          'rig_location.create_joint()')
        mc.menuItem(p = jnt_menu, l = '创建关节到选择对象的中心', rp = 'E', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                                'reload(rig_location);'
                                                                                'rig_location.get_jnt_core()')
        
        get_menu = mc.menuItem(p = menu, l = u'获取', rp = 'SW', sm = 1)
        mc.menuItem(p = get_menu, l = u'获取选中对象的蒙皮关节', rp = 'W', c = 'from sx_toolBOX.SX_rig import rig_tool;'
                                                                              'reload(rig_tool);'
                                                                              'rig_tool.select_skinJoint()')
        mc.menuItem(p = get_menu, l = u'选中个数与对象', rp = 'NW', c = 'from sx_toolBOX.SX_rig import rig_tool;'
                                                                              'reload(rig_tool);'
                                                                              'rig_tool.get_length()')
        
        
        mc.menuItem(p = menu, l = '刷新热盒', c = rebuild_rotBox)