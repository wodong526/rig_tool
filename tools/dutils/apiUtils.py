# coding=gbk
import maya.cmds as mc
import maya.api.OpenMaya as oma

from feedback_tool import Feedback_info as fb_print, LIN as lin


def getDagPath(obj):
    """
    ��ȡ�����MDagPath
    :param obj:(str) Ҫ��ȡ�Ķ���
    :return:
    """
    sel = oma.MSelectionList()
    sel.add(obj)
    m_dag = sel.getDagPath(0)

    return m_dag


def getMPoint(obj):
    """
    ��ȡ�������������xyz����
    :param obj: Ҫ��ȡ����Ķ���
    :return: MPoint����
    """
    pos = mc.xform(obj, q=True, t=True, ws=True)

    return oma.MPoint(pos[0], pos[1], pos[2], 1.0)


