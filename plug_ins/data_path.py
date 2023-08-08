# -*- coding:gbk -*-
import os

from feedback_tool import Feedback_info as fb_print, LIN as lin

localPath = ''
if os.path.exists('C:/Rig_Tools/'):
    localPath = 'C:/Rig_Tools/'
else:
    fb_print('�󶨲���ļ��в����ڣ����������ǩ��', error=True)

rigToolWarehouseURL = 'file:///Z:/Library/rig_plug_in/tools/Rig_warehouse/trunk'

projectPath_fhzj = ''
projectPath_xxtt = ''
if os.path.exists('Z:/Project/FHZJ/'):
    projectPath_fhzj = 'Z:/Project/FHZJ/CGT/Asset/'
else:
    fb_print('��Ŀfhzj�ļ��в����ڣ�����������ļ����Ƿ����', warning=True)
if os.path.exists('Z:/Project/XXTT/'):
    projectPath_xxtt = 'Z:/Project/XXTT/CGT/Asset/'
else:
    fb_print('��Ŀxxtt�ļ��в����ڣ�����������ļ����Ƿ����', warning=True)

iconPath = '{}icons/'.format(localPath)#ͼƬ·��
metaPath = '{}plug_ins/Bridge_To_Maya/'.format(localPath)#meta���·��
advPath = '{}plug_ins/ADV/'.format(localPath)#adv���·��
adPosePath = '{}plug_ins/adPose/'.format(localPath)#adPose���·��
studioLibraryPath = '{}plug_ins/studio_library/'.format(localPath)#studioLibrary���·��

rigPath = '{}tools/'.format(localPath)#�󶨹���·��
controllerFilesDataPath = '{}tools/data/ControllerFiles/'.format(localPath)#��������Դ·��
metaFaceCtrlsPath = '{}tools/data/meta_ctl_dir/'.format(localPath)#metaHuman�����������ļ�·��
rigMetaPath = '{}tools/Meta/'.format(localPath)#meta��ع���·��
rigWindowPath = '{}tools/ui/'.format(localPath)#�������·��
