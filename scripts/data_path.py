# -*- coding:gbk -*-
from PySide2 import QtGui
import os

from feedback_tool import Feedback_info as fp
#################################工具架文件夹地址#############################################
localPath = ''
if os.path.exists('C:/Rig_Tools/'):
    localPath = 'C:/Rig_Tools/'
else:
    fp('绑定插件文件夹不存在，请检查或重新签出', error=True)
#################################服务器文件url地址############################################
rigToolWarehouseURL = 'file:///Z:/Library/rig_plug_in/tools/Rig_warehouse/trunk'
#################################项目文件夹地址###############################################
#if os.path.exists('Z:/Project/FHZJ/'):
#    projectPath_fhzj = ['Z:/Project/FHZJ/CGT/Asset/', 'proj_fhzj_0']
#else:
#    fp('项目fhzj文件夹不存在，请检查服务器文件夹是否存在', warning=True)

if os.path.exists('X:/Project/XXTT/'):
    projectPath_xxtt = ['X:/Project/XXTT/CGT/Asset/', 'proj_xxtt']
else:
    fp('项目xxtt文件夹不存在，请检查服务器文件夹是否存在', warning=True)


#################################工具架自身配置文件夹地址########################################
iconPath = '{}icons/'.format(localPath)#图片路径
metaPath = '{}scripts/Bridge_To_Maya/'.format(localPath)#meta插件路径
advPath = '{}scripts/ADV/'.format(localPath)#adv插件路径
adPosePath = '{}scripts/adPose/'.format(localPath)#adPose插件路径
studioLibraryPath = '{}scripts/studio_library/'.format(localPath)#studioLibrary插件路径
#################################工具架中各工具文件夹地址#########################################
rigPath = '{}tools/'.format(localPath)#绑定工具路径
controllerFilesDataPath = '{}tools/data/ControllerFiles/'.format(localPath)#控制器资源路径
metaFaceCtrlsPath = '{}tools/data/meta_ctl_dir/'.format(localPath)#metaHuman脸控制器名文件路径
advRepairShapeJointPath = '{}tools/data/'.format(localPath)
rigMetaPath = '{}tools/Meta/'.format(localPath)#meta相关工具路径
rigWindowPath = '{}tools/tool_ui/'.format(localPath)#窗口相关路径
#################################工具架图片文件字典###############################################
icon_dir = {}#给qt的ui用的图片字典，用图片的名字为key，绝对路径为value
for path, _, icons in os.walk(iconPath):
    for icon in icons:
        icon_dir[os.path.splitext(icon)[0]] = QtGui.QIcon(os.path.join(path, icon))
