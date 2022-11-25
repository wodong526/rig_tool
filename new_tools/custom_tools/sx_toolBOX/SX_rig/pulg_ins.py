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
    from Bridge_To_Maya.DHI import DHIPluginLoader

    DHIPluginLoader.load()#���meta�ű����
    # Installer.createMSshelf()#��shelf����meta��ťˢ��
    # initLiveLink()#�򿪼��ز��ʵĴ���ui
    log.info('�Ѽ���bridgeToMaya�������')

def add_adPose_ui():
    from adPose import ui
    ui.show_in_maya()
    log.info('�Ѽ���adPose���ڡ�')