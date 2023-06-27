# coding=gbk
import maya.cmds as mc
import maya.api.OpenMaya as oma

from feedback_tool import Feedback_info as fb_print, LIN as lin


def getDagPath(obj):
    """
    获取对象的MDagPath
    :param obj:(str) 要获取的对象
    :return:
    """
    sel = oma.MSelectionList()
    sel.add(obj)
    m_dag = sel.getDagPath(0)

    return m_dag


def getMPoint(obj):
    """
    获取给定对象的世界xyz坐标
    :param obj: 要获取坐标的对象
    :return: MPoint类型
    """
    pos = mc.xform(obj, q=True, t=True, ws=True)

    return oma.MPoint(pos[0], pos[1], pos[2], 1.0)


