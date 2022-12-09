# -*- coding:GBK -*-
import maya.cmds as mc
from sys import path
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

    
if 'Z:/Library/rig_plug_in/maya_plug/data' in path:
    pass
else:
    path.append('Z:/Library/rig_plug_in/maya_plug/data')

def add_metaToMata_plug():
    if 'Z:/Library/rig_plug_in/maya_plug/data/Bridge_To_Maya' in path:
        pass
    else:
        path.append('Z:/Library/rig_plug_in/maya_plug/data/Bridge_To_Maya')
        
    #from Bridge_To_Maya.LiveLink import initLiveLink
    #from Bridge_To_Maya.Megascans import Installer
    from DHI import DHIPluginLoader

    DHIPluginLoader.load()#添加meta脚本插件
    # Installer.createMSshelf()#将shelf栏的meta按钮刷新
    initLiveLink()#打开实时链接与加载材质的窗口ui（已关闭加载浮动窗口代码）
    log.info('已加载bridgeToMaya插件集。')

def add_adPose_ui():
    from adPose import ui
    ui.show_in_maya()
    log.info('已加载adPose窗口。')