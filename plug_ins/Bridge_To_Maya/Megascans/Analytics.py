import sys, json

sys.path.append("..") # Adds higher directory to python modules path.
import socket
import maya.cmds as cmds
import maya.mel as melc

# For Importing Requests package 
import os
parent_dir = os.path.abspath(os.path.dirname(__file__))
package = os.path.join(parent_dir, 'RequestLibrary')
sys.path.append(package)

# For Handling all kinds of Logging
class Analytics:
    def __init__(self,id, guid, export_type):
        self.id = id
        self.guid = guid
        self.export_type = export_type
        self.sendBridgeLog()
        self.sendMetabase()
        
    # Open Local Connection to get Port from Bridge
    def GetActivePort(self):
        HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        PORT = 28852        # Port to listen on (non-privileged ports are > 1023)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        activeport = sock.recv(32)
        sock.close()
        
        return activeport.decode("utf-8") 

    # Set the data which will be sent to metabase
    def GetData(self):
        # from Megascans.ImporterSetup import importerSetup
        # instance = importerSetup.getInstance()
        from LiveLink import MAYA_PLUGIN_VERSION
        self.maya_version = cmds.about(version=True)
        self.renderer = melc.eval("getAttr defaultRenderGlobals.currentRenderer;")
        self.render_version = self.rendererVersion()
        data = {
            'event': "MAYA_ASSET_IMPORT",
            'data':{
                'guid': self.guid,
                'plugin_version':MAYA_PLUGIN_VERSION,
                'app_version': self.maya_version,
                'renderer': self.renderer,
                'renderer_version': self.render_version,
                'asset_ID': self.id,
                'export_type': self.export_type 
            }
        }
        return json.dumps(data)
    
    # Gets the current active render engine and its version
    def rendererVersion(self):
        if(self.renderer == 'arnold'):
            return cmds.pluginInfo('mtoa', query=True, version=True)
        elif(self.renderer == 'redshift'):
            return cmds.pluginInfo('redshift4maya', query=True, version=True)
        elif(self.renderer == 'vray'):
           return  cmds.pluginInfo('vrayformaya', query=True, version=True)
        elif(self.renderer == 'mayaSoftware'):
            return '1.0'
        elif(self.renderer == 'mayaHardware2'):
            return '2.0'
        elif(self.renderer == 'mayaVector'):
            return '1.0'
        else:
            return "-"
        
        
    # For Sending the data to Bridge Log File
    def sendBridgeLog(self):        
        try:
            from Megascans.RequestLibrary import requests
            port = self.GetActivePort()
            url = "http://localhost:" + port + "/log/"
            response =  requests.post(url, json=self.GetData())
            #print("Logging Response : ", response)
        except Exception as e:
            print("Bridge Logging Exception", e)
            
    # # For Sending the data to Metabase
    def sendMetabase(self):
        try:
            from Megascans.RequestLibrary import requests
            port = self.GetActivePort()
            url = "http://localhost:" + port + "/analytics/"
            response = requests.post(url, data=self.GetData())
            #print("Metabase finished: ", response)
        except Exception as e:
            print("Metabase Exception : ", e)
