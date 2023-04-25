# -*- coding:GBK -*- 
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def clear_look():
    import pymel.core as pm
    pm.mel.eval('outlinerEditor -edit -selectCommand "" "outlinerPanel1";')
    log.info('�������Ҳ�������look����')

def clear_onModelChange():
    import pymel.core as pm
    for item in pm.lsUI(editors=True):
       if isinstance(item, pm.ui.ModelEditor):
           pm.modelEditor(item, edit=True, editorChanged="")
    log.info('�������Ҳ�������onModelChange3dc������ر���')