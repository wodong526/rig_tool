# -*- coding:GBK -*-
import maya.cmds as mc

import os
import sys

from feedback_tool import Feedback_info as fb_print
lin = sys._getframe()

def open_studioLibrary():
    '''
    打开studioLibrary窗口
    :return:
    '''
    if not os.path.exists(r'C:\Rig_Tools\plug_ins\studio_library'):
        fb_print('C:\Rig_Tools\plug_ins\studio_library"路径不存在', error=True, path=__file__, line=lin.f_lineno, viewMes=True)

    if r'C:\Rig_Tools\plug_ins\studio_library' not in sys.path:
        sys.path.insert(0, r'C:\Rig_Tools\plug_ins\studio_library')

    import studiolibrary
    studiolibrary.main()