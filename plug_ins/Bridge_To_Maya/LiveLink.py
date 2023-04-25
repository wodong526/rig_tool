#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MegascansLiveLinkAPI is the core component of the Megascans Plugin plugins.
This API relies on a QThread to monitor any incoming data from Bridge by communicating
via a socket port.

This is the main class for setting up the communication between the software and Quixel Bridge
This Module:
- Communicates with bridge
- Listens for import using socket
"""


import os, json, sys, socket, time, re
try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtCore import QThread
except:
    try:
        from PySide.QtGui import *
        from PySide.QtCore import *
    except:
        try:
            from PyQt5.QtGui import *
            from PyQ5.QtCore import *
            from PyQ5.QtWidgets import *
        except:
            try:
                from PyQt4.QtGui import *
                from PyQ4.QtCore import *
            except:
                pass

from Megascans.ImporterSetup import importerSetup
from Megascans.Analytics import Analytics

MAYA_PLUGIN_VERSION = "6.9"

""" QLiveLinkMonitor is a QThread-based thread that monitors a specific port for import.
Simply put, this class is responsible for communication between your software and Bridge."""
# Using threads listen at the socket port
class QLiveLinkMonitor(QThread):

    Bridge_Call = Signal()
    Instance = []

    def __init__(self):
        QThread.__init__(self)
        self.TotalData = b""
        QLiveLinkMonitor.Instance.append(self)

    def __del__(self):
        self.quit()
        self.wait()

    def stop(self):
        self.terminate()

    def run(self):

        time.sleep(0.025)

        try:
            host, port = 'localhost', 13291

            socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_.bind((host, port))

            while True:
                socket_.listen(5)
                client, address = socket_.accept()
                data = ""
                data = client.recv(4096*2)

                if data != "":

                    self.TotalData = b""
                    self.TotalData += data
                    while True:
                        data = client.recv(4096*2)
                        if data : self.TotalData += data
                        else : break

                    time.sleep(0.05)
                    self.Bridge_Call.emit()
                    time.sleep(0.05)
                    # break
        except:
            pass

# Load the json array and pass the importersetup to this class for asset data config
    def InitializeImporter(self):
        print("Found import data, importing...")
        json_array = json.loads(self.TotalData)

        for asset_ in json_array:
            #print(asset_)

            try:
                export_type = "SINGLE_ASSET_EXPORT"
                try:
                    id = asset_['id']
                except:
                    id = "-"

                try:
                    guid = asset_['guid']
                except:
                    guid = "-"

                if len(json_array) > 1:
                    export_type = "BULK_ASSET_EXPORT"
                AnalyticsObj = Analytics(id, guid, export_type)
                print("Analytics Sent")
            except:
                print("Analytics Exception")

            if "isDHIAsset" in asset_.keys():
                print("Received data with DH Character descriptor. Initializing import!")
                from DHI.DHIImporterSetup import DHIImporterSetup
                DHIobj = DHIImporterSetup()
                DHIobj.set_Asset_Data(asset_)
            else:
                self = importerSetup.Instance
                self.set_Asset_Data(asset_)



# Setup the plugin UI and start the socket server of LiveLink
def initLiveLink():
    #from Megascans import UI
    #UI.initUI(MAYA_PLUGIN_VERSION)#加载浮动窗口
    StartSocketServer()
    #return UI.LiveLinkUI.Instance
    
# Setup Bridge Socket Server and start listening on socket
def StartSocketServer():
    try:
        if len(QLiveLinkMonitor.Instance) == 0:
            bridge_monitor = QLiveLinkMonitor()
            bridge_monitor.Bridge_Call.connect(bridge_monitor.InitializeImporter)
            bridge_monitor.start()
        #print("Quixel Bridge Plugin started successfully.")
    except:
        print("Quixel Bridge Plugin failed to start.")
