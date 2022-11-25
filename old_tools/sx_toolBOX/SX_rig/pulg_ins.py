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

    DHIPluginLoader.load()#���meta�ű����
    # Installer.createMSshelf()#��shelf����meta��ťˢ��
    # initLiveLink()#�򿪼��ز��ʵĴ���ui
    log.info('�Ѽ���bridgeToMaya�������')

def add_adPose_ui():
    from adPose import ui
    ui.show_in_maya()