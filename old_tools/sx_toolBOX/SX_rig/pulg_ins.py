# -*- coding:GBK -*-
import maya.cmds as mc

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def add_metaToMata_plug():
    import sys
    sys.path.append('F:\\bridge_library\\support\\plugins\\maya\\6.9\\MSLiveLink')
    #from LiveLink import initLiveLink
    #from Megascans import Installer
    from DHI import DHIPluginLoader

    DHIPluginLoader.load()#添加meta脚本插件
    # Installer.createMSshelf()#将shelf栏的meta按钮刷新
    # initLiveLink()#打开加载材质的窗口ui
    log.info('已加载bridgeToMaya插件集。')

def add_adPose_ui():
    from adPose import ui
    ui.show_in_maya()