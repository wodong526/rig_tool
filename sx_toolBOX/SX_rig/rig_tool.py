# -*- coding:GBK -*- 
import maya.cmds as mc
import pymel.core as pm
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def clear_orig():
    sel_lis = mc.ls(sl = 1)
    for obj in sel_lis:
        for sub_node in mc.listRelatives(obj, ad = True):
            if 'Orig' in sub_node:
                mc.delete(sub_node)
                log.info('模型{}的orig节点{}已删除。'.format(obj, sub_node))
                continue
    


def freeze_rotation():
    objs = pm.selected()
    for obj in objs:
        if isinstance(obj, pm.nt.Joint):
            rot = obj.rotate.get()
            ra = obj.rotateAxis.get()
            jo = obj.jointOrient.get()
            rotMatrix = pm.dt.EulerRotation(rot, unit = 'degrees').asMatrix()
            raMatrix = pm.dt.EulerRotation(ra, unit = 'degrees').asMatrix()
            joMatrix = pm.dt.EulerRotation(jo, unit = 'degrees').asMatrix()
            rotationMatrix = rotMatrix * raMatrix * joMatrix
            tmat = pm.dt.TransformationMatrix(rotationMatrix)
            newRotation = tmat.eulerRotation()
            newRotation = [ pm.dt.degrees(x) for x in newRotation.asVector() ]
            obj.rotate.set(0, 0, 0)
            obj.rotateAxis.set(0, 0, 0)
            obj.jointOrient.set(newRotation)
            log.info('{}的旋转已冻结。'.format(obj))
            continue

def select_skinJoint():
    sel_lis = mc.ls(sl = 1)
    jnt_lis = []
    for mod in sel_lis:
        for obj in mc.listHistory(mod, af=True):
            if mc.nodeType(obj) == 'skinCluster':
                for jnt in mc.skinCluster(obj, inf=1, q=1):
                    if jnt not in jnt_lis:
                        jnt_lis.append(jnt)
    if jnt_lis:
        mc.select(jnt_lis)
        log.info('已选中蒙皮关节。')
    else:
        log.error('选中对象没有蒙皮关节。')
        
def get_length():
    obj = mc.ls(sl=True, fl=True)
    n = len(obj)
    log.info('选中对象共有：{}个。对象为：{}。'.format(n, obj))
        
        