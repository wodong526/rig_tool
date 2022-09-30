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
        log.info(u'�Ⱥ�ˢ�³ɹ�')
    except:
        log.error(u'�Ⱥ�ˢ��ʧ��')



class SX_RotBox(object):
    '''
    �����Ⱥ�
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
        sundry_menu = mc.menuItem(p = menu, l = u'����', rp = 'N', sm = 1)
        mc.menuItem(p = sundry_menu, l = u'��', rp = 'N')
        mc.menuItem(p = sundry_menu, l = u'����ѡ�ж����orig�ڵ�', rp = 'NE', c = 'from sx_toolBOX.SX_rig import rig_tool;'
                                                                                  'reload(rig_tool);'
                                                                                  'rig_tool.clear_orig()')
        mc.menuItem(p = sundry_menu, l = u'����ѡ�ж������ת', rp = 'W', c = 'from sx_toolBOX.SX_rig import rig_tool;'
                                                                             'reload(rig_tool);'
                                                                             'rig_tool.freeze_rotation()')
        mc.menuItem(p = sundry_menu, l = u'�򿪻�رն��������', rp = 'NW', c = 'mc.ToggleLocalRotationAxes()')
        mc.menuItem(p = sundry_menu, l = u'����ƥ��', rp = 'SE', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                     'reload(rig_location);'
                                                                     'rig_location.match_transform()')
        
        except_menu = mc.menuItem(p = menu, l = u'����ǰ', rp = 'NE', sm = 1)
        mc.menuItem(p = except_menu, l = u'�Զ�', rp = 'S', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                'reload(rig_clear);reload(rig_clear);reload(rig_clear);'
                                                                'rig_clear.clear_uv(1);rig_clear.clear_material();rig_clear.clear_name()')
        mc.menuItem(p = except_menu, l = u'����������', rp = 'NE', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                        'reload(rig_clear);'
                                                                        'rig_clear.clear_name()')
        mc.menuItem(p = except_menu, l = u'��ѯ�����ظ��Ĳ�����', rp = 'NW', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                               'reload(rig_clear);'
                                                                               'rig_clear.clear_material()')
        mc.menuItem(p = except_menu, l = u'�����ܵ�uvλ�ô���', rp = 'N', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                               'reload(rig_clear);'
                                                                               'rig_clear.clear_uv(0)')
        mc.menuItem(p = except_menu, l = u'�������ؼ�֡', rp = 'E', c = 'from sx_toolBOX.SX_rig import rig_clear;'
                                                                         'reload(rig_clear);'
                                                                         'rig_clear.clear_key()')
        
        subMenu = mc.menuItem(p = menu, l = '��λ��', rp = 'W', subMenu = 1)
        mc.menuItem(p = subMenu, l = u'������λ��������', rp = 'W', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                       'reload(rig_location);'
                                                                       'rig_location.get_core()')
        mc.menuItem(p = subMenu, l = u'������λ��Ŀ�겢ƥ����ת', rp = 'NW', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                               'reload(rig_location);'
                                                                               'rig_location.get_trm_rot()')
        
        jnt_menu = mc.menuItem(p = menu, l = '�ؽ�', rp = 'E', sm = 1)
        mc.menuItem(p = jnt_menu, l = '�����ؽڹ���', rp = 'N', c = 'mc.JointTool()')
        # mc.menuItem(p = jnt_menu, l = '�����ؽڵ�ѡ��λ', rp = 'E', c = 'from sx_toolBOX.SX_rig import rig_location;'
        #                                                                'reload(rig_location);'
        #                                                                'rig_location.get_jnt_trs()')
        mc.menuItem(p = jnt_menu, l = '�����ؽڲ�ƥ����ת', rp = 'NE', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                          'reload(rig_location);'
                                                                          'rig_location.create_joint()')
        mc.menuItem(p = jnt_menu, l = '�����ؽڵ�ѡ����������', rp = 'E', c = 'from sx_toolBOX.SX_rig import rig_location;'
                                                                                'reload(rig_location);'
                                                                                'rig_location.get_jnt_core()')
        
        get_menu = mc.menuItem(p = menu, l = u'��ȡ', rp = 'SW', sm = 1)
        mc.menuItem(p = get_menu, l = u'��ȡѡ�ж������Ƥ�ؽ�', rp = 'W', c = 'from sx_toolBOX.SX_rig import rig_tool;'
                                                                              'reload(rig_tool);'
                                                                              'rig_tool.select_skinJoint()')
        mc.menuItem(p = get_menu, l = u'ѡ�и��������', rp = 'NW', c = 'from sx_toolBOX.SX_rig import rig_tool;'
                                                                              'reload(rig_tool);'
                                                                              'rig_tool.get_length()')
        
        
        mc.menuItem(p = menu, l = 'ˢ���Ⱥ�', c = rebuild_rotBox)