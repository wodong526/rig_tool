# coding=gbk
import maya.cmds as mc

from ast import literal_eval

from feedback_tool import Feedback_info as fb_print

FINE_PATH = __file__


def add_string_info(information, obj, attr=''):
    """
    给指定节点的指定属性添加字符串内容
    :param information: 要填入的字符串内容
    :param obj: 要填入字符串的节点
    :param attr: 节点的属性名
    :return:
    """
    if not mc.objExists('{}.{}'.format(obj, attr)):
        mc.addAttr(obj, ln=attr, dt='string')
    if not information:
        information = ''

    mc.setAttr('{}.{}'.format(obj, attr), l=False)
    mc.setAttr('{}.{}'.format(obj, attr), e=True, k=True)
    mc.setAttr('{}.{}'.format(obj, attr), information, type='string')
    mc.setAttr('{}.{}'.format(obj, attr), l=True)

def add_string_attr(information, obj, attr='', keyble=True, lock=False):
    """
    对某节点添加字符串类型的属性
    :param lock:是否锁定属性
    :param keyble:是否让属性能被k帧（不能被k帧会在通道盒中隐藏
    :param information:被填入字符串属性的值
    :param obj:生成该属性的节点名
    :param attr:生成的属性名
    :return:
    """
    if not mc.objExists('{}.{}'.format(obj, attr)):
        mc.addAttr(obj, ln=attr, dt='string', k=keyble)
    else:
        fb_print('属性{}.{}已经存在'.format(obj, attr), error=True)

    mc.setAttr('{}.{}'.format(obj, attr), information, typ='string')
    mc.setAttr('{}.{}'.format(obj, attr), l=lock)


def lock_and_hide_attrs(objs, attrs=[], lock=False, hide=False):
    """
    锁定并隐藏指定属性
    :param objs: 要被操作的对象或对象列表
    :param attrs: 要被操作的属性
    :param lock: 使对象是否被锁定
    :param hide: 使对象是否被隐藏
    :return:
    """
    if type(objs) not in list():
        objs = [objs]

    for obj in objs:
        for attr in attrs:
            mc.setAttr('{}.{}'.format(obj, attr), l=lock, k=not hide)


def get_string_info(obj, attr=''):
    """
    将节点的字符串属性以字符串内容的真实类型返回
    :param obj:要查询的节点
    :param attr:要查询的节点属性名
    :return:
    """
    if mc.objExists('{}.{}'.format(obj, attr)):
        string_info_message = mc.getAttr('{}.{}'.format(obj, attr))
        if string_info_message:
            info = literal_eval(string_info_message)#将字符串转换为字符串内容的真实类型
            return info
        else:
            return False
    else:
        return None
