# -*- coding:GBK -*- 
import maya.cmds as mc
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def get_core():
    '''
    ��ѡ���������Ĵ�����λ����
    '''
    obj_lis = mc.ls(sl = 1, fl = 1)
    pos_lis = [0, 0, 0]
    
    if len(obj_lis) == 0:
        loc = mc.spaceLocator()[0]
        mc.xform(loc, ws = 1, t = pos_lis)
        log.info('����ԭ�㴴����λ��{}'.format(loc))
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

        log.info('����ѡ���������Ĵ�����λ��{}'.format(loc))

def create_joint():
    '''
    �����ؽڵ�Ŀ��λ�ò�ƥ����ת
    ���û��ѡ������򴴽���ԭ��
    '''
    sel_lis = mc.ls(sl = True)
    if len(sel_lis) == 1:
        mc.parent(mc.joint(), w = True)
        log.info('�Ѵ����ؽڵ�{}���Ĳ�ƥ����ת��'.format(sel_lis[0]))
    elif len(sel_lis) == 0:
        mc.joint(p = [0, 0, 0])
        log.info('����ԭ�㴴���ؽڡ�')
    else:
        log.error('Ӧѡ��1������ʵ��Ϊ{}����'.format(len(sel_lis)))

def get_jnt_trs():
    '''
    ��ѡ������ϴ����ؽ�
    '''
    obj = mc.ls(sl = True)
    mc.select(cl = True)
    if len(obj) != 1:
        log.error('Ӧѡ��1������ʵ��Ϊ{}����'.format(len(obj)))
    else:
        pos = mc.xform(obj[0], ws = True, q = True, t = True)
        jnt = mc.joint()
        mc.xform(jnt, t = pos, ws = True)
        log.info('�Ѵ���{}��{}���ġ�'.format(jnt, obj[0]))

def get_jnt_core():
    '''
    ��ѡ���������Ĵ����ؽڡ�
    '''
    obj_lis = mc.ls(sl = 1, fl = 1)
    pos_lis = [0, 0, 0]
    
    if len(obj_lis) == 0:
        log.error('û��ѡ�����')
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

        log.info('����ѡ���������Ĵ����ؽ�{}'.format(loc))


def get_trm_rot():
    '''
    ������λ����ѡ���������Ĳ�ƥ����ת
    '''
    obj = mc.ls(sl = 1)
    if obj.__len__() == 1:
        pos = mc.xform(obj[0], q = True, ws = True, t = True)
        rot = mc.xform(obj[0], q = True, ws = True, ro = True)
        mc.xform(mc.spaceLocator(), ws = True, t = pos, ro = rot)
    else:
        log.warning('����{}λ���ϴ�����λ����ƥ��'.format(obj.__len__()))