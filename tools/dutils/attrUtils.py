# coding=gbk
import maya.cmds as mc

from feedback_tool import Feedback_info as fb_print, LIN as lin

FINE_PATH = __file__

def add_string_info(information, obj, attr='', keyble=True, lock=False):
    """
    对某节点添加字符串类型的属性
    :param lock:
    :param keyble:
    :param information:
    :param obj:
    :param attr:
    :return:
    """
    if not mc.objExists('{}.{}'.format(obj, attr)):
        mc.addAttr(obj, ln=attr, dt='string', k=keyble)
    else:
        fb_print('属性{}.{}已经存在'.format(obj, attr), error=True)

    mc.setAttr('{}.{}'.format(obj, attr), information, typ='string')
    mc.setAttr('{}.{}'.format(obj, attr), l=lock)



