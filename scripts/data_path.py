# -*- coding:gbk -*-
import os

from feedback_tool import Feedback_info as fp

localPath = ''
if os.path.exists('C:/Rig_Tools/'):
    localPath = 'C:/Rig_Tools/'
else:
    fp('�󶨲���ļ��в����ڣ����������ǩ��', error=True)

rigToolWarehouseURL = 'file:///Z:/Library/rig_plug_in/tools/Rig_warehouse/trunk'

projectPath_fhzj = ''
projectPath_xxtt = ''
if os.path.exists('Z:/Project/FHZJ/'):
    projectPath_fhzj = 'Z:/Project/FHZJ/CGT/Asset/'
else:
    fp('��Ŀfhzj�ļ��в����ڣ�����������ļ����Ƿ����', warning=True)
if os.path.exists('Z:/Project/XXTT/'):
    projectPath_xxtt = 'Z:/Project/XXTT/CGT/Asset/'
else:
    fp('��Ŀxxtt�ļ��в����ڣ�����������ļ����Ƿ����', warning=True)

iconPath = '{}icons/'.format(localPath)#ͼƬ·��
metaPath = '{}scripts/Bridge_To_Maya/'.format(localPath)#meta���·��
advPath = '{}scripts/ADV/'.format(localPath)#adv���·��
adPosePath = '{}scripts/adPose/'.format(localPath)#adPose���·��
studioLibraryPath = '{}scripts/studio_library/'.format(localPath)#studioLibrary���·��

rigPath = '{}tools/'.format(localPath)#�󶨹���·��
controllerFilesDataPath = '{}tools/data/ControllerFiles/'.format(localPath)#��������Դ·��
metaFaceCtrlsPath = '{}tools/data/meta_ctl_dir/'.format(localPath)#metaHuman�����������ļ�·��
advRepairShapeJointPath = '{}tools/data/'.format(localPath)
rigMetaPath = '{}tools/Meta/'.format(localPath)#meta��ع���·��
rigWindowPath = '{}tools/ui/'.format(localPath)#�������·��

icon_dic = {}#��qt��ui�õ�ͼƬ�ֵ䣬��ͼƬ������Ϊkey������·��Ϊvalue
for path, _, icons in os.walk(iconPath):
    for icon in icons:
        icon_dic[os.path.splitext(icon)[0]] = os.path.join(path, icon)
