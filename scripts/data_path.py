# -*- coding:gbk -*-
try:
    from PySide2 import QtGui
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtGui
    from PySide6 import QtCore
import os

from feedback_tool import Feedback_info as fp
#################################���߼��ļ��е�ַ#############################################
localPath = ''
if os.path.exists('C:/Rig_Tools/'):
    localPath = 'C:/Rig_Tools/'
else:
    fp('�󶨲���ļ��в����ڣ����������ǩ��', error=True)
#################################�������ļ�url��ַ############################################
rigToolWarehouseURL = 'file:///Z:/Library/rig_plug_in/tools/Rig_warehouse/trunk'
#################################��Ŀ�ļ��е�ַ###############################################
database_dir = {'proj_fhzj_0': 'Z:/Project/FHZJ/', 'proj_xxtt': 'Z:/Project/XXTT/', 'proj_spkt': 'X:/Project/SPKT'}

if os.path.exists('Z:/Project/FHZJ/'):
   projectPath_fhzj = ['Z:/Project/FHZJ/CGT/Asset/', 'proj_fhzj_0']
else:
   fp('��Ŀfhzj�ļ��в����ڣ�����������ļ����Ƿ����', error=True, block=False)

if os.path.exists('X:/Project/XXTT/'):
    projectPath_xxtt = ['X:/Project/XXTT/CGT/Asset/', 'proj_xxtt']
else:
    fp('��Ŀxxtt�ļ��в����ڣ�����������ļ����Ƿ����', error=True, block=False)


#################################���߼����������ļ��е�ַ########################################
iconPath = '{}icons/'.format(localPath)#ͼƬ·��
metaPath = '{}scripts/Bridge_To_Maya/'.format(localPath)#meta���·��
advPath = '{}scripts/ADV/'.format(localPath)#adv���·��
adPosePath = '{}scripts/adPose/'.format(localPath)#adPose���·��
studioLibraryPath = '{}scripts/studio_library/'.format(localPath)#studioLibrary���·��
#################################���߼��и������ļ��е�ַ#########################################
rigPath = '{}tools/'.format(localPath)#�󶨹���·��
dataPath = '{}tools/data/'.format(localPath)#�����ļ�·��
controllerFilesDataPath = '{}/ControllerFiles/'.format(dataPath)#��������Դ·��
metaFaceCtrlsPath = '{}/meta_ctl_dir/'.format(dataPath)#metaHuman�����������ļ�·��

rigMetaPath = '{}tools/Meta/'.format(localPath)#meta��ع���·��
rigWindowPath = '{}tools/tool_ui/'.format(localPath)#�������·��
#################################���߼�ͼƬ�ļ��ֵ�###############################################
icon_dir = {}#��qt��ui�õ�ͼƬ�ֵ䣬��ͼƬ������Ϊkey������·��Ϊvalue
for path, _, icons in os.walk(iconPath):
    for icon in icons:
        icon_dir[os.path.splitext(icon)[0]] = QtGui.QIcon(os.path.join(path, icon))
