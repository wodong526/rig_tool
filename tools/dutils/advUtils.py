# coding=gbk
import maya.cmds as mc

from feedback_tool import Feedback_info as fp


def obj_to_set(*objs):
    """
    将传入对象按对象类型放进adv的set集中
    :param objs: 要被放入set集的对象
    :return:
    """
    for qukSet in ['Sets', 'AllSet', 'ControlSet', 'DeformSet']:
        if not mc.objExists(qukSet):
            fp('set集{}不存在'.format(qukSet), error=True)

    for obj in objs:
        if mc.objectType(obj) == 'joint':
            mc.sets(obj, e=1, forceElement='DeformSet')
        elif mc.objectType(obj) == 'transform' and mc.objectType(mc.listRelatives(obj, s=True)[0]) == 'nurbsCurve':
            mc.sets(obj, e=1, forceElement='ControlSet')

        mc.sets(obj, e=1, forceElement='AllSet')


def createUiaxialDrive(drv_joint, aix='ry', point='double', val=6, angle=90):
    """
    对指定关节和轴向增加被驱动关节
    :param val: 驱动值的最大值
    :param point: 向哪个方向驱动
    :param drv_joint: 驱动关节
    :param aix: 驱动属性
    :param angle: 驱动值
    :return:有驱动效果的关节名
    """

    def set_joint(jnt, side, aixs, data_val, max_val, ang):
        mc.setAttr('{}.side'.format(skin_jnt), side)
        if 'ry' in aixs:
            aixs = 'ry'
            moveAix = 'tz'
        elif 'rx' in aixs:
            aixs = 'rx'
            moveAix = 'ty'
        elif 'rz' in aixs:
            aixs = 'rz'
            moveAix = 'tx'
        mc.setDrivenKeyframe('{}.{}'.format(skin_jnt, moveAix), itt='linear', ott='linear', cd='{}.{}'.format(jnt, aixs),
                             driverValue=0, value=data_val)
        mc.setDrivenKeyframe('{}.{}'.format(skin_jnt, moveAix), itt='linear', ott='linear', cd='{}.{}'.format(jnt, aixs),
                             driverValue=angle, value=max_val)
        if point == 'double':
            mc.setDrivenKeyframe('{}.{}'.format(skin_jnt, moveAix), itt='linear', ott='linear', cd='{}.{}'.format(jnt, aixs),
                                 driverValue=-1 * ang, value=max_val)

    rot_jnt = 'jnt_{}_{}_base_001'.format(drv_joint, aix)
    if mc.objExists(rot_jnt):
        mc.delete(rot_jnt)
    mult = mc.createNode('multDoubleLinear', n='mult_{}'.format(drv_joint))
    mc.createNode('joint', n=rot_jnt)
    skin_jnt = mc.createNode('joint', n='jnt_{}_{}_skin_001'.format(drv_joint, aix))

    mc.matchTransform(rot_jnt, drv_joint, rot=True, pos=True)
    mc.matchTransform(skin_jnt, drv_joint, rot=True, pos=True)
    mc.parent(rot_jnt, drv_joint)
    mc.parent(skin_jnt, rot_jnt)
    mc.makeIdentity(rot_jnt, a=True, r=True, n=False, pn=True)
    mc.makeIdentity(skin_jnt, a=True, r=True, n=False, pn=True)

    if not mc.attributeQuery("drv_{}".format(aix), n=drv_joint, ex=True):
        mc.addAttr(drv_joint, ln="drv_{}".format(aix), at="double", dv=-0.5, keyable=True)
    mc.connectAttr('{}.{}'.format(drv_joint, aix.split('_')[0]), '{}.input1'.format(mult))
    mc.connectAttr('{}.drv_{}'.format(drv_joint, aix), '{}.input2'.format(mult))
    mc.connectAttr('{}.output'.format(mult), '{}.{}'.format(rot_jnt, aix.split('_')[0]))

    if '_L' in drv_joint:
        set_joint(drv_joint, 1, aix, -1, -1 * val, angle)
        if 'all' in aix:
            skin_jnt = mc.duplicate(skin_jnt, n=skin_jnt.replace('skin_', 'skin_rvs_'), rr=True)[0]
            set_joint(drv_joint, 1, aix, 1, val, angle)

    elif '_R' in drv_joint:
        set_joint(drv_joint, 2, aix, 1, val, angle)
        if 'all' in aix:
            skin_jnt = mc.duplicate(skin_jnt, n=skin_jnt.replace('skin_', 'skin_rvs_'), rr=True)[0]
            set_joint(drv_joint, 2, aix, -1, -1 * val, angle)
    else:
        fp('对象{}不在检测范围内'.format(drv_joint), warning=True)
    mc.setAttr('{}.type'.format(skin_jnt), 18)
    mc.setAttr('{}.otherType'.format(skin_jnt), skin_jnt.split('_')[1], typ='string')

    return rot_jnt
