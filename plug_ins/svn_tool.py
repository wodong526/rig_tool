# -*- coding:GBK -*-
import os
import sys
from feedback_tool import Feedback_info as fb_print

tool_nam = __file__.split('\\')[1]
lin = sys._getframe()

def svn_chectOut():
    '''
    ǩ��svn�⵽ָ��λ��
    :return:
    '''
    resout = os.system('svn checkout file:///Z:/Library/rig_plug_in/maya_plug_warehouse/trunk C:/{}'.format(tool_nam))
    if resout == 0:
        fb_print('���߼�ǩ���ɹ���', info=True, viewMes=True, path=__file__, line=lin.f_lineno)
    else:
        fb_print('���߼�ǩ��ʧ�ܡ�', error=True, viewMes=True, path=__file__, line=lin.f_lineno)

def svn_info():
    '''
    ��ӡ��ǰ���ؿ��svn��Ϣ
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
        fb_print('��İ汾��{}����ǰ�汾��{}�����ͬ�����߼ܸ��µ����°汾��'.format(loca_edition, server_edition), warning=True,
                 viewMes=True, path=__file__, line=lin.f_lineno)
    else:
        fb_print('��İ汾��{}����ǰ�汾��{}�����Ѿ������°汾��'.format(loca_edition, server_edition), info=True, viewMes=True,
                 path=__file__, line=lin.f_lineno)

def svn_upData():
    '''
    ���±��ؿ�Ϊ���°汾
    :return:
    '''
    resout = os.system('pushd "C:/{}" && svn update'.format(tool_nam))
    if resout == 0:
        fb_print('���߼�ͬ���ɹ�', info=True, viewMes=True, path=__file__, line=lin.f_lineno)
    else:
        fb_print('���߼�ͬ��ʧ��', error=True, viewMes=True, path=__file__, line=lin.f_lineno)
