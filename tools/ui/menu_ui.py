# -*- coding:GBK -*-
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

import sys
import os

from feedback_tool import Feedback_info as fb_print

if sys.version_info.major == 3:
    #当环境为py3时
    from importlib import reload


def reload_menu():
    try:
        from ui import menu_ui
        menu_ui.Rig_Menu()
        fb_print('菜单刷新成功', info=True, viewMes=True)
    except:
        fb_print('菜单刷新失败', error=True, viewMes=True)

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
            master_menu = pm.menu(self.menu_n, to=True, l=u'绑定工具架', p=mainWindow)

            pm.menuItem(to=True, p=master_menu, l=u'刷新菜单', i='refresh.png',
                        c='from ui import menu_ui;'
                          'reload(menu_ui);'
                          'menu_ui.reload_menu()')
            pm.menuItem(d=1, dl='ADV工具', p=master_menu, )
            rig_adv = pm.menuItem(to=True, p=master_menu, l='ADV', sm=True)
            pm.menuItem(d=1, dl='辅助工具', p=master_menu)
            self.tool_menu(master_menu)
            rig_clear = pm.menuItem(to=True, p=master_menu, l=u'模型清理', i='polyCleanup.png', sm=True)
            pm.menuItem(d=1, dl='导出导入', p=master_menu, i='port.jpg')
            menu_import = pm.menuItem(to=True, p=master_menu, l=u'导入', i='import.png')
            menu_export = pm.menuItem(to=True, p=master_menu, l=u'导出', i='export.png', sm=True)
            pm.menuItem(d=1, dl='场景清理', p=master_menu)
            menu_clr = pm.menuItem(to=True, p=master_menu, l=u'清理报错', i='error.png', sm=True)
            pm.menuItem(d=1, dl='工作表', p=master_menu, )
            menu_wps = pm.menuItem(to=True, p=master_menu, l=u'打开工作表', i='wps.png', sm=True)
            pm.menuItem(d=1, dl='svn管理', p=master_menu, )
            menu_svn = pm.menuItem(to=True, p=master_menu, l=u'svn设置', i='svn_logo.png', sm=True)
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
        pm.menuItem(to=True, p=p_menu, l=u'控制器生成器', i='ctl_tool.png', c='import controller_tool;'
                                                                            'reload(controller_tool);')
        pm.menuItem(to=True, p=p_menu, l=u'跨文件传递材质', i='moveShelfDown.png', c='import transform_matrerl;'
                                                                                   'reload(transform_matrerl);')
        pm.menuItem(to=True, p=p_menu, l=u'Meta调教器', i='MS_Logo.png', c='from ui import MeTa_Training_win;'
                                                                          'reload(MeTa_Training_win);')
        pm.menuItem(to=True, p=p_menu, l=u'打铆钉', i='follicle.png', c='import rivet_tool;'
                                                                       'reload(rivet_tool);')
        pm.menuItem(to=True, p=p_menu, l=u'履带生成器', i='tape.png', c='import trackTool;'
                                                                                   'reload(trackTool);')
        pm.menuItem(to=True, p=p_menu, l=u'批量链接', i='link_tool.png', c='import batch_connect_tool;'
                                                                          'reload(batch_connect_tool);'
                                                                          'batch_connect_tool.main()')
        pm.menuItem(to=True, p=p_menu, i='studio_library.png', l='打开studio_library', c='import toos_starter;'
                                                                                         'toos_starter.open_studioLibrary();')

    def port(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'导出SM文件', i='export_sm.jpg', c='import port_tool;'
                                                                            'reload(port_tool);'
                                                                            'port_tool.export_SM();')

    def mod_clear(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'清理场景重名', c='import rig_clear;'
                                                          'reload(rig_clear);'
                                                          'rig_clear.clear_name()')
        pm.menuItem(to=True, p=p_menu, l=u'查询选中物体的非四边面', c='import rig_clear;'
                                                                  'reload(rig_clear);'
                                                                  'rig_clear.clear_face()')
        pm.menuItem(to=True, p=p_menu, l=u'查询选中对象的边界边', c='import rig_clear;'
                                                                 'reload(rig_clear);'
                                                                 'rig_clear.clear_boundary()')
        pm.menuItem(to=True, p=p_menu, l=u'查询场景中所有模型的非冻结属性', c='import rig_clear;'
                                                                        'reload(rig_clear);'
                                                                        'rig_clear.clear_frozen()')
        pm.menuItem(to=True, p=p_menu, l=u'查询对象残留历史', c='import rig_clear;'
                                                             'reload(rig_clear);'
                                                             'rig_clear.clear_history()')
        pm.menuItem(to=True, p=p_menu, l=u'查询选中对象的最低点', c='import rig_clear;'
                                                                'reload(rig_clear);'
                                                                'rig_clear.clear_minimum()')

    def aim_menu(self, p_menu):
        pm.menuItem(to=True, p=p_menu, i='studio_library.png', l='打开studio_library',
                    c='from sx_toolBOX.SX_aim import run_studio_library;'
                      'reload(run_studio_library)')

    def scene_clear(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l=u'找不到过程“look”', c='import clear_errors;'
                                                              'reload(clear_errors);'
                                                              'clear_errors.clear_look()')
        pm.menuItem(to=True, p=p_menu, l=u'找不到过程“onModelChange”', c='import clear_errors;'
                                                                        'reload(clear_errors);'
                                                                        'clear_errors.clear_onModelChange()')

    def set_wps(self, p_menu):
        pm.menuItem(to=True, p=p_menu, l='打开工作记录表', i='excel.png',
                    c='os.startfile("Z:/山魈动画-表格文档/《FHZJ》/资产-UE沟通对接/绑定组工作记录.xlsx")')
        pm.menuItem(to=True, p=p_menu, l='打开FBX记录表', i='excel.png',
                    c='os.startfile("Z:/山魈动画-表格文档/《FHZJ》/资产-UE沟通对接/资产SVN-FBX记录表.xlsx")')
        pm.menuItem(to=True, p=p_menu, l='打开7—16集资产制作表', i='excel.png',
                    c='os.startfile("Z:/山魈动画-表格文档/《FHZJ》/资产-UE沟通对接/资产统筹制作表EP07~EP16.xlsx")')

    def set_svn(self, p_menu):
        import svn_tool
        def upData_rigMenu(*args):
            svn_tool.svn_upData()
        def edition_info(*args):
            svn_tool.svn_info()

        pm.menuItem(to=True, p=p_menu, l=u'同步工具架', i='svn_synchronization.png', c=upData_rigMenu)
        pm.menuItem(to=True, p=p_menu, l=u'打印本地工具架版本信息', i='svn_info.png', c=edition_info)

