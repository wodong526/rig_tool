# -*- coding:gbk -*-
import os

from feedback_tool import Feedback_info as fb_print, LIN as lin

localPath = ''
if os.path.exists('C:/Rig_Tools/'):
    localPath = 'C:/Rig_Tools/'
else:
    fb_print('�󶨲���ļ��в����ڣ������', error=True)

serverSubmitsTheLogs = 'file:///Z:/Library/rig_plug_in/tools/Rig_warehouse/trunk'


projectPath = 'Z:/Project/FHZJ/CGT/Asset/'

iconPath = '{}icons/'.format(localPath)#ͼƬ·��
metaPath = '{}plug_ins/Bridge_To_Maya/'.format(localPath)#meta���·��
advPath = '{}plug_ins/ADV/'.format(localPath)#adv���·��
adPosePath = '{}plug_ins/adPose/'.format(localPath)#adPose���·��
studioLibraryPath = '{}plug_ins/studio_library/'.format(localPath)#studioLibrary���·��

rigPath = '{}tools/'.format(localPath)#�󶨹���·��
controllerFilesDataPath = '{}tools/data/ControllerFiles/'.format(localPath)#��������Դ·��
rigMetaPath = '{}tools/Meta/'.format(localPath)#meta��ع���·��
rigWindowPath = '{}tools/ui/'.format(localPath)#�������·��
