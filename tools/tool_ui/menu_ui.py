# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mm

import sys
import os

from feedback_tool import Feedback_info as fb_print
from dutils import toolUtils

if sys.version_info.major == 3:
    from importlib import reload


class Rig_Menu(object):
    def __init__(self):
        self.menu_n = 'menu_ui'
        self.create_menu()

    def create_menu(self):
        mainWindow = 'MayaWindow'
        master_menu = mc.menu(self.menu_n, to=True, l=u'绑定工具架', p=mainWindow)

        mc.menuItem(to=True, p=master_menu, l=u'刷新菜单', i='refresh.png', c='import reload_tools;'
                                                                             'reload(reload_tools);'
                                                                             'reload_tools.reload_menu_ui()')
        mc.menuItem(d=1, dl='ADV工具', p=master_menu, )
        rig_adv = mc.menuItem(to=True, p=master_menu, l='ADV', sm=True)
        mc.menuItem(d=1, dl='辅助工具', p=master_menu)
        self.tool_menu(master_menu)
        rig_clear = mc.menuItem(to=True, p=master_menu, l=u'模型清理', i='polyCleanup.png', sm=True)
        mc.menuItem(d=1, dl='导出导入', p=master_menu)
        menu_import = mc.menuItem(to=True, p=master_menu, l=u'导入', i='import.png')
        menu_export = mc.menuItem(to=True, p=master_menu, l=u'导出', i='export.png', sm=True)
        mc.menuItem(d=1, dl='上传下载', p=master_menu)
        menu_push = mc.menuItem(to=True, p=master_menu, l=u'上传', i='pushToServer.png', sm=True)
        mc.menuItem(d=1, dl='场景清理', p=master_menu)
        menu_clr = mc.menuItem(to=True, p=master_menu, l=u'清理报错', i='error.png', sm=True)
        mc.menuItem(d=1, dl='工作表', p=master_menu, )
        menu_wps = mc.menuItem(to=True, p=master_menu, l=u'打开工作表', i='wps.png', sm=True)
        mc.menuItem(d=1, dl='svn管理', p=master_menu, )
        menu_svn = mc.menuItem(to=True, p=master_menu, l=u'svn设置', i='svn_logo.png', sm=True)
        ##########################################################
        self.adv_menu(rig_adv)
        self.port(menu_export)
        self.push(menu_push)
        self.mod_clear(rig_clear)
        self.scene_clear(menu_clr)
        self.set_wps(menu_wps)
        self.set_svn(menu_svn)

    def adv_menu(self, p_menu):
        mc.menuItem(to=True, p=p_menu, i='AS5_tool.png', l='ADV辅助工具', c="from tool_ui import advTools;"
                                                                           "reload(advTools);"
                                                                           "advTools.openAdvTool();")
        mc.menuItem(to=True, p=p_menu, i='AS5.png', l='ADV',
                    c="mm.eval('source \"C:/Rig_Tools/scripts/ADV/AdvancedSkeleton.mel\";AdvancedSkeleton;')")
        mc.menuItem(to=True, p=p_menu, i='asBiped.png', l='biped',
                    c="mm.eval('source \"C:/Rig_Tools/scripts/ADV/AdvancedSkeletonFiles/Selector/biped.mel\";')")
        mc.menuItem(to=True, p=p_menu, i='asFace.png', l='face',
                    c="mm.eval('source \"C:/Rig_Tools/scripts/ADV/AdvancedSkeletonFiles/Selector/face.mel\";')")
        mc.menuItem(to=True, p=p_menu, i='picker.png', l='picker',
                    c="mm.eval('source \"C:/Rig_Tools/scripts/ADV/AdvancedSkeletonFiles/picker/picker.mel\";')")

    def tool_menu(self, p_menu):
        mc.menuItem(to=True, p=p_menu, l=u'控制器生成器', i='ctl_tool.png', c='import controller_tool;'
                                                                              'reload(controller_tool);')
        mc.menuItem(to=True, p=p_menu, l=u'跨文件传递材质', i='moveShelfDown.png', c='import transfer_material;'
                                                                                     'reload(transfer_material);')
        mc.menuItem(to=True, p=p_menu, l=u'Meta调教器', i='MS_Logo.png', c='from tool_ui import MeTa_Training_win;'
                                                                           'reload(MeTa_Training_win);')
        mc.menuItem(to=True, p=p_menu, l=u'打铆钉', i='follicle.png', c='import rivet_tool;'
                                                                        'reload(rivet_tool);')
        mc.menuItem(to=True, p=p_menu, l=u'履带生成器', i='tape.png', c='import trackTool;'
                                                                        'reload(trackTool);')
        mc.menuItem(to=True, p=p_menu, l=u'批量链接', i='link_tool.png', c='import batch_connect_tool;'
                                                                           'reload(batch_connect_tool);'
                                                                           'batch_connect_tool.main()')
        mc.menuItem(to=True, p=p_menu, l=u'传递权重', i='copySkinWeights.png', c='import transformSkinWeight;'
                                                                                 'reload(transformSkinWeight)')
        mc.menuItem(to=True, p=p_menu, i='studio_library.png', l='打开studio_library', c='import reload_tools;'
                                                                                         'reload_tools.open_studioLibrary()')

    def port(self, p_menu):
        mc.menuItem(to=True, p=p_menu, l=u'导出SM文件', i='export_sm.jpg', c='import port_tool;'
                                                                             'reload(port_tool);'
                                                                             'port_tool.export_SM();')

    def push(self, p_menu):
        mc.menuItem(to=True, p=p_menu, l=u'上传rig到cgt', i='push_rig.png',
                    ann='cgt的替换工具，进行提交和简单的文件操作',
                    c='import pushScence_tool;reload(pushScence_tool);pushScence_tool.push_rig();')

    def mod_clear(self, p_menu):
        mc.menuItem(to=True, p=p_menu, l=u'清理场景重名', c='from dutils import clearUtils;'
                                                          'reload(clearUtils);'
                                                          'clearUtils.clear_name()')
        mc.menuItem(to=True, p=p_menu, l=u'查询选中物体的非四边面', c='import rig_clear;'
                                                                      'reload(rig_clear);'
                                                                      'rig_clear.clear_face()')
        mc.menuItem(to=True, p=p_menu, l=u'查询选中对象的边界边', c='import rig_clear;'
                                                                    'reload(rig_clear);'
                                                                    'rig_clear.clear_boundary()')
        mc.menuItem(to=True, p=p_menu, l=u'查询场景中所有模型的非冻结属性', c='import rig_clear;'
                                                                          'reload(rig_clear);'
                                                                          'rig_clear.clear_frozen()')
        mc.menuItem(to=True, p=p_menu, l=u'查询对象残留历史', c='import rig_clear;'
                                                                'reload(rig_clear);'
                                                                'rig_clear.clear_history()')
        mc.menuItem(to=True, p=p_menu, l=u'查询选中对象的最低点', c='import rig_clear;'
                                                                    'reload(rig_clear);'
                                                                    'rig_clear.clear_minimum()')

    def aim_menu(self, p_menu):
        mc.menuItem(to=True, p=p_menu, i='studio_library.png', l='打开studio_library',
                    c='from sx_toolBOX.SX_aim import run_studio_library;'
                      'reload(run_studio_library)')

    def scene_clear(self, p_menu):
        mc.menuItem(to=True, p=p_menu, l=u'找不到过程“look”', c='import clear_errors;'
                                                                'reload(clear_errors);'
                                                                'clear_errors.clear_look()')
        mc.menuItem(to=True, p=p_menu, l=u'找不到过程“onModelChange”', c='import clear_errors;'
                                                                         'reload(clear_errors);'
                                                                         'clear_errors.clear_onModelChange()')
        mc.menuItem(to=True, p=p_menu, l=u'找不到对象“shaderBallOrthoCamera1”',
                    c='import clear_errors;'
                      'reload(clear_errors);'
                      'clear_errors.clear_shaderBallOrthoCamera1()')

    def set_wps(self, p_menu):
        pass

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

        if toolUtils.get_native_iP() == '192.168.0.59':
            mc.menuItem(to=True, p=p_menu, l=u'同步工具架', i='svn_synchronization.png', c=upData_rigMenu)
        mc.menuItem(to=True, p=p_menu, l=u'打印本地工具架版本信息', i='svn_info.png', c=edition_info)
        mc.menuItem(to=True, p=p_menu, l=u'打印服务器提交日志', i='svn_log.png', c=get_logs)
