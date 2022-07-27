# -*- coding:GBK -*- 
import maya.cmds as mc
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def get_core():
    '''
    在选择对象的中心创建定位器。
    '''
    obj_lis = mc.ls(sl = 1, fl = 1)
    pos_lis = [0, 0, 0]
    
    if len(obj_lis) == 0:
        loc = mc.spaceLocator()[0]
        mc.xform(loc, ws = 1, t = pos_lis)
        log.info('已在原点创建定位器{}'.format(loc))
    else:
        for obj in obj_lis:
            if mc.nodeType(obj) == 'transform' or mc.nodeType(obj) == 'joint':
                pos = mc.xform(obj, ws = 1, q = 1, t = 1)
            else:
                pos = mc.xform(obj, ws = 1, t = 1, q = 1)
            pos_lis[0] = pos[0] + pos_lis[0]
            pos_lis[1] = pos[1] + pos_lis[1]
            pos_lis[2] = pos[2] + pos_lis[2]
        
        obj_pos = [pos_lis[0] / len(obj_lis),
                   pos_lis[1] / len(obj_lis),
                   pos_lis[2] / len(obj_lis)]
        loc = mc.spaceLocator()[0]
        mc.xform(loc, ws = 1, t = obj_pos)

        log.info('已在选择对象的中心创建定位器{}'.format(loc))

def create_joint():
    '''
    创建关节到目标位置并匹配旋转
    如果没有选择对象，则创建在原点
    '''
    sel_lis = mc.ls(sl = True)
    if len(sel_lis) == 1:
        mc.parent(mc.joint(), w = True)
        log.info('已创建关节到{}中心并匹配旋转。'.format(sel_lis[0]))
    elif len(sel_lis) == 0:
        mc.joint(p = [0, 0, 0])
        log.info('已在原点创建关节。')
    else:
        log.error('应选择1个对象，实际为{}个。'.format(len(sel_lis)))

def get_jnt_trs():
    '''
    在选择对象上创建关节
    '''
    obj = mc.ls(sl = True)
    mc.select(cl = True)
    if len(obj) != 1:
        log.error('应选择1个对象，实际为{}个。'.format(len(obj)))
    else:
        pos = mc.xform(obj[0], ws = True, q = True, t = True)
        jnt = mc.joint()
        mc.xform(jnt, t = pos, ws = True)
        log.info('已创建{}到{}中心。'.format(jnt, obj[0]))

def get_jnt_core():
    '''
    在选择对象的中心创建关节。
    '''
    obj_lis = mc.ls(sl = 1, fl = 1)
    pos_lis = [0, 0, 0]
    
    if len(obj_lis) == 0:
        log.error('没有选择对象。')
    else:
        for obj in obj_lis:
            pos = mc.xform(obj, ws = 1, t = 1, q = 1)
            pos_lis[0] = pos[0] + pos_lis[0]
            pos_lis[1] = pos[1] + pos_lis[1]
            pos_lis[2] = pos[2] + pos_lis[2]
        
        obj_pos = [pos_lis[0] / len(obj_lis),
                   pos_lis[1] / len(obj_lis),
                   pos_lis[2] / len(obj_lis)]
        loc = mc.joint()
        mc.xform(loc, ws = 1, t = obj_pos)

        log.info('已在选择对象的中心创建关节{}'.format(loc))


def get_trm_rot():
    '''
    创建定位器到选择对象的中心并匹配旋转
    '''
    obj = mc.ls(sl = 1)
    if obj.__len__() == 1:
        pos = mc.xform(obj[0], q = True, ws = True, t = True)
        rot = mc.xform(obj[0], q = True, ws = True, ro = True)
        mc.xform(mc.spaceLocator(), ws = True, t = pos, ro = rot)
    else:
        log.warning('已在{}位置上创建定位器并匹配'.format(obj.__len__()))