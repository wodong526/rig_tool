# -*- coding:GBK -*-
import os
import sys
from feedback_tool import Feedback_info as fb_print

tool_nam = __file__.split('\\')[1]
lin = sys._getframe()

def svn_chectOut():
    '''
    签出svn库到指定位置
    :return:
    '''
    resout = os.system('svn checkout file:///Z:/Library/rig_plug_in/maya_plug_warehouse/trunk C:/{}'.format(tool_nam))
    if resout == 0:
        fb_print('工具架签出成功。', info=True, viewMes=True, path=__file__, line=lin.f_lineno)
    else:
        fb_print('工具架签出失败。', error=True, viewMes=True, path=__file__, line=lin.f_lineno)

def svn_info():
    '''
    打印当前本地库的svn信息
    :return:
    '''
    def output_info(info):
        revisionNum = re.search("Revision:\s\d+", info)
        return revisionNum.group().split(":")[1]

    import re, subprocess
    server_info = subprocess.check_output("svn info file:///Z:/Library/rig_plug_in/tools/Rig_warehouse/trunk")
    loca_info = subprocess.check_output("svn info C:/Rig_Tools")
    server_edition = output_info(server_info)
    loca_edition = output_info(loca_info)
    if server_edition != loca_edition:
        fb_print('你的版本是{}，当前版本是{}。点击同步工具架更新到最新版本。'.format(loca_edition, server_edition), warning=True,
                 viewMes=True, path=__file__, line=lin.f_lineno)
    else:
        fb_print('你的版本是{}，当前版本是{}。你已经是最新版本。'.format(loca_edition, server_edition), info=True, viewMes=True,
                 path=__file__, line=lin.f_lineno)

def svn_upData():
    '''
    更新本地库为最新版本
    :return:
    '''
    resout = os.system('pushd "C:/{}" && svn update'.format(tool_nam))
    if resout == 0:
        fb_print('工具架同步成功', info=True, viewMes=True, path=__file__, line=lin.f_lineno)
    else:
        fb_print('工具架同步失败', error=True, viewMes=True, path=__file__, line=lin.f_lineno)
