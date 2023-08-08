# -*- coding:gbk -*-
import os

from feedback_tool import Feedback_info as fb_print, LIN as lin

localPath = ''
if os.path.exists('C:/Rig_Tools/'):
    localPath = 'C:/Rig_Tools/'
else:
    fb_print('绑定插件文件夹不存在，请检查或重新签出', error=True)

rigToolWarehouseURL = 'file:///Z:/Library/rig_plug_in/tools/Rig_warehouse/trunk'

projectPath_fhzj = ''
projectPath_xxtt = ''
if os.path.exists('Z:/Project/FHZJ/'):
    projectPath_fhzj = 'Z:/Project/FHZJ/CGT/Asset/'
else:
    fb_print('项目fhzj文件夹不存在，请检查服务器文件夹是否存在', warning=True)
if os.path.exists('Z:/Project/XXTT/'):
    projectPath_xxtt = 'Z:/Project/XXTT/CGT/Asset/'
else:
    fb_print('项目xxtt文件夹不存在，请检查服务器文件夹是否存在', warning=True)

iconPath = '{}icons/'.format(localPath)#图片路径
metaPath = '{}plug_ins/Bridge_To_Maya/'.format(localPath)#meta插件路径
advPath = '{}plug_ins/ADV/'.format(localPath)#adv插件路径
adPosePath = '{}plug_ins/adPose/'.format(localPath)#adPose插件路径
studioLibraryPath = '{}plug_ins/studio_library/'.format(localPath)#studioLibrary插件路径

rigPath = '{}tools/'.format(localPath)#绑定工具路径
controllerFilesDataPath = '{}tools/data/ControllerFiles/'.format(localPath)#控制器资源路径
metaFaceCtrlsPath = '{}tools/data/meta_ctl_dir/'.format(localPath)#metaHuman脸控制器名文件路径
rigMetaPath = '{}tools/Meta/'.format(localPath)#meta相关工具路径
rigWindowPath = '{}tools/ui/'.format(localPath)#窗口相关路径
