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
    obj_lis = mc.ls(sl=1, fl=1)

    if len(obj_lis) == 0:
        loc = mc.spaceLocator()[0]
        log.info('����ԭ�㴴����λ��{}'.format(loc))
    else:
        pos_lis = []
        for obj in obj_lis:
            pos_lis.append(mc.xform(obj, ws=True, q=True, t=True))

        crv = mc.curve(d=1, p=pos_lis)
        clst = mc.cluster()
        loc = mc.spaceLocator()[0]
        mc.matchTransform(loc, clst)
        mc.delete(crv, clst)

        log.info('����ѡ���������Ĵ�����λ��{}'.format(loc))


def create_joint():
    '''
    �����ؽڵ�Ŀ��λ�ò�ƥ����ת
    ���û��ѡ������򴴽���ԭ��
    '''
    sel_lis = mc.ls(sl=True)
    if len(sel_lis) == 1:
        mc.select(cl=True)
        jnt = mc.joint()
        mc.matchTransform(jnt, sel_lis[0], pos=True, rot=True)
        log.info('�Ѵ����ؽ�{}��{}���Ĳ�ƥ����ת��'.format(jnt, sel_lis[0]))
    else:
        log.error('Ӧѡ��1������ʵ��Ϊ{}����'.format(len(sel_lis)))


def get_jnt_core():
    '''
    ��ѡ���������Ĵ����ؽڡ�
    '''
    obj_lis = mc.ls(sl=1, fl=1)
    if len(obj_lis) == 0:
        mc.joint(p=[0, 0, 0])
        log.info('����ԭ�㴴���ؽڡ�')
    else:
        pos_lis = []
        for obj in obj_lis:
            pos_lis.append(mc.xform(obj, ws=True, q=True, t=True))

        crv = mc.curve(d=1, p=pos_lis)
        clst = mc.cluster()
        mc.select(cl=True)
        jnt = mc.joint()
        mc.matchTransform(jnt, clst)
        mc.delete(crv, clst)

        log.info('����ѡ���������Ĵ����ؽ�{}'.format(jnt))


def get_trm_rot():
    '''
    ������λ����ѡ���������Ĳ�ƥ����ת
    '''
    obj = mc.ls(sl=True)
    if obj.__len__() == 1:
        mc.matchTransform(mc.spaceLocator(), obj[0], pos=True, rot=True)
    else:
        log.warning('����{}λ���ϴ�����λ����ƥ��'.format(obj.__len__()))


def match_transform():
    '''
    ��ѡ���б������ж����λ����ת����ƥ�䵽���һ��ѡ�����
    '''
    sel_lis = mc.ls(sl=True)
    if len(sel_lis) < 2:
        log.error('ѡ�����Ӧ������2����ʵ��Ϊ{}����'.format(len(sel_lis)))
        return False
    else:
        obj_target = sel_lis[-1]
        for i in range(0, len(sel_lis) - 1):
            mc.matchTransform(sel_lis[i], obj_target)
            log.info('�ѽ�{}ƥ�䵽{}��'.format(sel_lis[i], obj_target))