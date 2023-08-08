# coding=gbk
import maya.cmds as mc

from feedback_tool import Feedback_info as fp


def obj_to_set(*objs):
    """
    ��������󰴶������ͷŽ�adv��set����
    :param objs: Ҫ������set���Ķ���
    :return:
    """
    for qukSet in ['Sets', 'AllSet', 'ControlSet', 'DeformSet']:
        if not mc.objExists(qukSet):
            fp('set��{}������'.format(qukSet), error=True)

    for obj in objs:
        if mc.objectType(obj) == 'joint':
            mc.sets(obj, e=1, forceElement='DeformSet')
        elif mc.objectType(obj) == 'transform' and mc.objectType(mc.listRelatives(obj, s=True)[0]) == 'nurbsCurve':
            mc.sets(obj, e=1, forceElement='ControlSet')

        mc.sets(obj, e=1, forceElement='AllSet')


def createUiaxialDrive(drv_joint, aix='ry', angle=90):
    """
    ��ָ���ؽں��������ӱ������ؽ�
    :param drv_joint: �����ؽ�
    :param aix: ��������
    :param angle: ����ֵ
    :return:������Ч���Ĺؽ���
    """
    mult = mc.createNode('multDoubleLinear', n='mult_{}'.format(drv_joint))
    rot_jnt = mc.createNode('joint', n='jnt_{}_{}_base_001'.format(drv_joint, aix))
    skin_jnt = mc.createNode('joint', n='jnt_{}_{}_skin_001'.format(drv_joint, aix))

    mc.matchTransform(rot_jnt, drv_joint, rot=True, pos=True)
    mc.matchTransform(skin_jnt, drv_joint, rot=True, pos=True)
    mc.parent(rot_jnt, drv_joint)
    mc.parent(skin_jnt, rot_jnt)
    mc.makeIdentity(rot_jnt, a=True, r=True, n=False, pn=True)
    mc.makeIdentity(skin_jnt, a=True, r=True, n=False, pn=True)

    if not mc.attributeQuery("drv_{}".format(aix), n=drv_joint, ex=True):
        mc.addAttr(drv_joint, ln="drv_{}".format(aix), at="double", dv=-0.5, keyable=True)
    mc.connectAttr('{}.{}'.format(drv_joint, aix), '{}.input1'.format(mult))
    mc.connectAttr('{}.drv_{}'.format(drv_joint, aix), '{}.input2'.format(mult))
    mc.connectAttr('{}.output'.format(mult), '{}.{}'.format(rot_jnt, aix))

    if '_L' in drv_joint:
        mc.setDrivenKeyframe('{}.tz'.format(skin_jnt), itt='linear', ott='linear', cd='{}.{}'.format(drv_joint, aix),
                             driverValue=0, value=-1)
        mc.setAttr('{}.side'.format(skin_jnt), 1)
        mc.setDrivenKeyframe('{}.tz'.format(skin_jnt), itt='linear', ott='linear', cd='{}.{}'.format(drv_joint, aix),
                             driverValue=angle, value=-6)
    elif '_R' in drv_joint:
        mc.setDrivenKeyframe('{}.tz'.format(skin_jnt), itt='linear', ott='linear', cd='{}.{}'.format(drv_joint, aix),
                             driverValue=0, value=1)
        mc.setAttr('{}.side'.format(skin_jnt), 2)
        mc.setDrivenKeyframe('{}.tz'.format(skin_jnt), itt='linear', ott='linear', cd='{}.{}'.format(drv_joint, aix),
                             driverValue=angle, value=6)
    else:
        fp('����{}���ڼ�ⷶΧ��'.format(drv_joint), warning=True)
    mc.setAttr('{}.type'.format(skin_jnt), 18)
    mc.setAttr('{}.otherType'.format(skin_jnt), skin_jnt.split('_')[1], typ='string')

    return rot_jnt
