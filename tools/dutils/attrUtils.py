# coding=gbk
import maya.cmds as mc

from ast import literal_eval

from feedback_tool import Feedback_info as fb_print

FINE_PATH = __file__


def add_string_info(information, obj, attr=''):
    """
    ��ָ���ڵ��ָ����������ַ�������
    :param information: Ҫ������ַ�������
    :param obj: Ҫ�����ַ����Ľڵ�
    :param attr: �ڵ��������
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
    ��ĳ�ڵ�����ַ������͵�����
    :param lock:�Ƿ���������
    :param keyble:�Ƿ��������ܱ�k֡�����ܱ�k֡����ͨ����������
    :param information:�������ַ������Ե�ֵ
    :param obj:���ɸ����ԵĽڵ���
    :param attr:���ɵ�������
    :return:
    """
    if not mc.objExists('{}.{}'.format(obj, attr)):
        mc.addAttr(obj, ln=attr, dt='string', k=keyble)
    else:
        fb_print('����{}.{}�Ѿ�����'.format(obj, attr), error=True)

    mc.setAttr('{}.{}'.format(obj, attr), information, typ='string')
    mc.setAttr('{}.{}'.format(obj, attr), l=lock)


def lock_and_hide_attrs(objs, attrs=[], lock=False, hide=False):
    """
    ����������ָ������
    :param objs: Ҫ�������Ķ��������б�
    :param attrs: Ҫ������������
    :param lock: ʹ�����Ƿ�����
    :param hide: ʹ�����Ƿ�����
    :return:
    """
    if type(objs) not in list():
        objs = [objs]

    for obj in objs:
        for attr in attrs:
            mc.setAttr('{}.{}'.format(obj, attr), l=lock, k=not hide)


def get_string_info(obj, attr=''):
    """
    ���ڵ���ַ����������ַ������ݵ���ʵ���ͷ���
    :param obj:Ҫ��ѯ�Ľڵ�
    :param attr:Ҫ��ѯ�Ľڵ�������
    :return:
    """
    if mc.objExists('{}.{}'.format(obj, attr)):
        string_info_message = mc.getAttr('{}.{}'.format(obj, attr))
        if string_info_message:
            info = literal_eval(string_info_message)#���ַ���ת��Ϊ�ַ������ݵ���ʵ����
            return info
        else:
            return False
    else:
        return None
