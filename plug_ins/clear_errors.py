# -*- coding:GBK -*-
import os

import maya.cmds as mc

from feedback_tool import Feedback_info as fb_print


def replace_string_in_file(file_path, search_string, replace_strings):
    with open(file_path, 'r') as f:
        file_content = f.read()
    count = 0
    while True:
        index = file_content.find(search_string)
        if index == -1:
            break
        file_content = file_content[:index] + replace_strings[count % len(replace_strings)] + file_content[index + len(
            search_string):]
        count += 1
    with open(file_path, 'w') as f:
        f.write(file_content)


def clear_look():
    import pymel.core as pm
    pm.mel.eval('outlinerEditor -edit -selectCommand "" "outlinerPanel1";')
    fb_print('�������Ҳ�������look����', info=True)


def clear_onModelChange():
    import pymel.core as pm
    for item in pm.lsUI(editors=True):
        if isinstance(item, pm.ui.ModelEditor):
            pm.modelEditor(item, edit=True, editorChanged="")
    fb_print('�������Ҳ�������onModelChange3dc������ر���', info=True)


def clear_shaderBallOrthoCamera1():
    file_path = mc.file(exn=1, q=1)
    if os.path.splitext(file_path)[-1] == '.ma':
        if mc.file(mf=True, q=True):
            rest = mc.confirmDialog(title='���棺', message='�ò����ᱣ�浱ǰ��������ȷ���������Ա�����',
                                    button=['���沢�������', 'ȡ��'])
            if rest == u'�ò����ᱣ�浱ǰ��������ȷ���������Ա�����':
                mc.file(s=True, f=True, op='v=0')
            else:
                fb_print('������ȡ��', info=True)
                return None

        replace_string_in_file(file_path, 'shaderBallOrthoCamera1', ['top', 'side', 'front'])
        mc.file(file_path, f=True, o=True, iv=True, typ='mayaAscii', op='v=0')
        fb_print('shaderBallOrthoCamera1������', info=True)
    else:
        fb_print('ֻ֧������ma�ļ��������±���Ϊma��ʹ�øù���', warning=True)

