# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import maya.api.OpenMaya as oma
import maya.api.OpenMayaAnim as omaa

from feedback_tool import Feedback_info as fb_print, LIN as lin
from dutils import attrUtils, toolUtils, fileUtils

reload(attrUtils)

FILE_PATH = __file__


def mirrorBS(bs, src, dst, side='X'):
    """
    ��ָ���±�bs������һ���±��Ŀ������
    :param bs: Ҫ�����bs�ڵ�
    :param src:Ҫ�����bsĿ�����±�
    :param dst:Ҫ���񵽵�bsĿ�����±�
    :param side:Ҫ�������
    :return:none
    """
    mc.blendShape(bs, e=1, rtd=[0, dst])
    mc.blendShape(bs, e=1, cd=[0, src, dst])
    mc.blendShape(bs, e=1, ft=[0, dst], sa=side, ss=1)

    mc.symmetricModelling(s=0, e=1)  #�رջ��ڶ�����
    bsNam_lis = mc.listAttr(bs + ".w", k=True, m=True)
    fb_print('�ѽ�{}��{}Ŀ���徵��{}Ŀ����'.format(bs, bsNam_lis[src], bsNam_lis[dst]), info=True)


def create_blendshape(base_geo, name=None, origin='local', deform_order=None):
    """
    Ϊָ�����󴴽�bs
    :param base_geo:
    :param name:
    :param origin:
    :param deform_order:
    :return:
    """
    if not name:
        name = 'BS_{}'.format(base_geo)

    if mc.objExists(name):
        fb_print('�ڵ���{}�Ѿ����ڣ�������ָ��BS�ڵ�����'.format(name), error=True, viewMes=True)

    if deform_order == 'after':
        blendshape = mc.blendShape(base_geo, name=name, origin=origin, after=True)[0]
    elif deform_order == 'before':
        blendshape = mc.blendShape(base_geo, name=name, origin=origin, before=True)[0]
    elif deform_order == 'parallel':
        blendshape = mc.blendShape(base_geo, name=name, origin=origin, parallel=True)[0]
    elif deform_order == 'split':
        blendshape = mc.blendShape(base_geo, name=name, origin=origin, split=True)[0]
    elif deform_order == 'foc':
        blendshape = mc.blendShape(base_geo, name=name, origin=origin, foc=True)[0]
    else:
        blendshape = mc.blendShape(base_geo, name=name, origin=origin)[0]

    return blendshape


class BSWeights:
    def __init__(self, blendshape, weights_handle=None):
        self.scence_path = (mc.file(q=True, location=True)).rpartition("/")[0]

        if not weights_handle:  # ��ȡȨ�ؿ��Ʊ���λ��
            weights_handle = 'trs_{}_whMaster'.format(blendshape)
        if not mc.objExists(blendshape):  # ������Ƿ��ǻ����״�ڵ�
            fb_print('BS�ڵ�{}�����ڣ�������ָ��BS�ڵ�'.format(blendshape), error=True, viewMes=True)

        self.weights_handle = self.create_weights_trs(blendshape, weights_handle)  # �������ӵ������״��Ȩ����
        self.weights_file = '{}.json'.format(self.weights_handle)  # ����bsȨ����Ϣ��json�ļ���

        # ��ȡȨ��������Ϣ�ֵ�
        self.bs_weights_dict = attrUtils.get_string_info(self.weights_handle, 'BS_Weights_Dict')
        if not self.bs_weights_dict:  #û�оͶ���Ϊ���ֵ�
            self.bs_weights_dict = {}

        # ��ȡȨ������Ϣ�б���νṹ�ʵ��б�
        # ������������������ֵ���������������Ӽ�����ֵ��Ȩ���������ƣ�
        self.bs_weights_groups_list = attrUtils.get_string_info(self.weights_handle, 'BS_Weights_Groups_List')
        if not self.bs_weights_groups_list:
            self.bs_weights_groups_list = [{'parent': '', 'children': []}]  #���������Ӽ���

        self.data = {'bs_weights_dict': self.bs_weights_dict,
                     'bs_weights_groups_list': self.bs_weights_groups_list}

    def create_weights_trs(self, blendshape, weights_handle):
        """
        ����Ƿ��г���bs���飬û�оʹ���
        ��������blendShapeNode���Ը�bs�ڵ��weightsHandleû������ʱɾ����blendShapeNode����������Բ���������������
        :param blendshape: ��ȡbsȨ�ص�bs�ڵ�
        :param weights_handle: ����bsȨ����Ϣ���������
        :return:����bsȨ����Ϣ������
        """
        if not mc.objExists(weights_handle) or mc.nodeType(weights_handle) != 'transform':
            weights_handle = mc.group(name=weights_handle, em=True, w=True)
            attrUtils.lock_and_hide_attrs(weights_handle, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
                                          lock=True, hide=True)

        # ������Ƿ���л����״�ڵ����Ϣ�������ԣ����û�д���һ����
        if not mc.objExists('{}.weightsHandle'.format(blendshape)):
            mc.addAttr(blendshape, ln='weightsHandle', at='message')
        if not mc.objExists('{}.blendShapeNode'.format(weights_handle)):
            mc.addAttr(weights_handle, ln='blendShapeNode', at='message')

        if [weights_handle] != mc.listConnections('{}.weightsHandle'.format(blendshape)):
            weights_attributes = mc.listAttr(weights_handle, k=True, ud=True)
            if weights_attributes:
                for w_attr in weights_attributes:
                    if w_attr == 'blendShapeNode':
                        continue
                    else:
                        mc.deleteAttr('{}.{}'.format(weights_handle, w_attr))
            mc.connectAttr('{}.weightsHandle'.format(blendshape), '{}.blendShapeNode'.format(weights_handle), f=True)

        return weights_handle

    def set_bs_weight_attr(self, bs_weight_name, ctrl_attr, value):
        """
        ��bsHandl�ϵ�BS_Weights_Dict���Լ�¼������bs�����֡������������ԡ����Ե�����ֵ
        :param bs_weight_name: bs��
        :param ctrl_attr: ��������������
        :param value: ���Ե�����ֵ
        :return:
        """
        if mc.objExists(ctrl_attr):
            #��� bs Ȩ���������������������Ƴ�ͻ��
            for i in range(len(self.bs_weights_groups_list)):
                if bs_weight_name == self.bs_weights_groups_list[i]['parent']:
                    fb_print('{} ��������Ϊ�����ƴ����ڴ�Ȩ�ؾ����,��ѡһ����'.format(bs_weight_name), error=True)

            # ���bs_weight_name������û���������룬������Ȩ����������
            if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):

                connections = mc.listConnections('{}.{}'.format(self.weights_handle, bs_weight_name), p=True, d=False)
                if connections:
                    fb_print('BSȨ������{}�Ѵ��ڲ��������ӣ�ѡ����һ��BSȨ���������ƣ�'.format(bs_weight_name),
                             error=True)
                else:
                    return_attr = [None, bs_weight_name]

            else:  # ���bs_weight_name�����ڣ��봴��һ����Ȩ��ֵΪ 0 �� 1��
                mc.addAttr(self.weights_handle, ln=bs_weight_name, nn=bs_weight_name, at='double', min=0, max=1,
                           dv=0, keyable=True)
                # ���֮ǰδ��ӣ��뽫bs_weight_name��ӵ�������
                self.bs_weights_groups_list[0]['children'].append(bs_weight_name)
                return_attr = [bs_weight_name, None]

            # ���������� Ctrl ����Ϊ BS Ȩ������
            mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear', ott='linear',
                                 currentDriver=ctrl_attr, driverValue=value[0], value=0)
            mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear', ott='linear',
                                 currentDriver=ctrl_attr, driverValue=value[1], value=1)

            self.bs_weights_dict[bs_weight_name] = (ctrl_attr, value)
            attrUtils.add_string_info(self.bs_weights_dict, self.weights_handle, 'BS_Weights_Dict')
            attrUtils.add_string_info(self.bs_weights_groups_list, self.weights_handle, 'BS_Weights_Groups_List')
            return return_attr
        else:
            fb_print('����������{}������'.format(ctrl_attr), error=True)

    def set_bs_weights_attrs(self, input_data):
        """
        ˢ������ָ����bs�������������
        :param input_data: ������Ϣ�ֵ�
        :return:
        """
        for bs_weight_name, inputs in input_data.items():
            if mc.objExists(inputs[0]):  #�������������Ƿ����
                if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):  #��bsHandl��bs��Ϣ���ڣ���Ͽ��������
                    connections = mc.listConnections('{}.{}'.format(self.weights_handle, bs_weight_name), p=True,
                                                     d=False)
                    if connections:
                        mc.disconnectAttr(connections[0], '{}.{}'.format(self.weights_handle, bs_weight_name))
                else:
                    mc.addAttr(self.weights_handle, ln=bs_weight_name, nn=bs_weight_name, at='double', min=0, max=1,
                               dv=0, keyable=True)
                    self.bs_weights_groups_list[0]['children'].append(bs_weight_name)

                mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear', ott='linear',
                                     currentDriver=inputs[0], driverValue=inputs[1][0], value=0)
                mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear', ott='linear',
                                     currentDriver=inputs[0], driverValue=inputs[1][1], value=1)

                self.bs_weights_dict[bs_weight_name] = inputs  #ˢ�����bs����Ϣ
            else:
                mc.warning("������������{}������".format(inputs[0]))

        attrUtils.add_string_info(self.bs_weights_dict, self.weights_handle, 'BS_Weights_Dict')
        attrUtils.add_string_info(self.bs_weights_groups_list, self.weights_handle, 'BS_Weights_Groups_List')

    def disconnect_ctrls_to_bsHandl(self, bs_weights=None):
        """
        �Ͽ�ָ������
        :param bs_weights:Ҫ�Ͽ���bs�б�ΪNoneʱ�Ͽ�ȫ��
        :return:
        """
        bs_weights_names = self.bs_weights_dict.keys()

        if bs_weights:  #ȡָ��bs������bs�������ϵĽ�������
            bs_weights_names = toolUtils.list_operation(list_a=bs_weights, list_b=bs_weights_names, operation='&')

        for bs_weight_name in bs_weights_names:
            if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):  #���bs�������Դ���ʱ
                connections = mc.listConnections('{}.{}'.format(self.weights_handle, bs_weight_name), p=True, d=False)
                if connections:
                    mc.disconnectAttr(connections[0], '{}.{}'.format(self.weights_handle, bs_weight_name))
                    fb_print('�ѶϿ�{}������'.format(bs_weight_name), info=True)
                    mc.delete(connections[0].split('.')[0])
                else:
                    fb_print('{}û����������'.format(bs_weight_name), warning=True)

    def reconnect_ctrls_to_bsHandl(self, bs_weights=None):
        """
        ˢ��bs������bsHandl�ϼ�¼��bs������Ϣ
        :param bs_weights: ָ����Ҫ������bs�б�ΪNoneʱȫ������
        :return:
        """
        bs_weights_names = self.bs_weights_dict.keys()  #bsHandl�ϵ�bs�����б�

        if bs_weights:
            bs_weights_names = toolUtils.list_operation(bs_weights, bs_weights_names, '&')  #ָ���������еĵĽ���Ԫ��

        for bs_weight_name in bs_weights_names:
            ctrl_attr, value = self.bs_weights_dict[bs_weight_name]  #�������Ӹ�bs�ģ����������ԣ�ֵ��

            if mc.objExists(ctrl_attr):  #��������������Ƿ����
                if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):  #bsHandl�Ƿ������bs����
                    connections = mc.listConnections('{}.{}'.format(self.weights_handle, bs_weight_name), p=True,
                                                     d=False)  #����
                    if connections:  #�Ͽ�����
                        mc.disconnectAttr(connections[0], '{}.{}'.format(self.weights_handle, bs_weight_name))

                    # ���������� Ctrl ����Ϊ BS Ȩ�����ԡ�
                    mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear',
                                         ott='linear', currentDriver=ctrl_attr, driverValue=value[0], value=0)

                    mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear',
                                         ott='linear', currentDriver=ctrl_attr, driverValue=value[1], value=1)
                else:  #���bsHandlû��������ԣ����ڼ�¼�б���ɾ�����bs��
                    del self.bs_weights_dict[bs_weight_name]
            else:
                if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):
                    mc.deleteAttr('{}.{}'.format(self.weights_handle, bs_weight_name))
                del self.bs_weights_dict[bs_weight_name]
                fb_print('���ӵ�{0}�ϵ�{1}�Ŀ���������{2}������, bsHandl���������¼��bs��Ϣ����ɾ��bs:{1}'.format(
                    self.weights_handle, bs_weight_name, ctrl_attr), warning=True)

        attrUtils.add_string_info(self.bs_weights_dict, self.weights_handle, 'BS_Weights_Dict')  #��bsHandl������д�����µ�bs��Ϣ
        fb_print('bsHandl������������ˢ��', info=True)

    def export_connections(self, bs_weights=None):
        """
        ��ָ����bsHandl�ϵ�bs��Ϣд�뵽json��
        :param bs_weights: ����ָ��bs��ʱֻ����д����Щbs����Ϣ��û��ʱд������
        :return:
        """
        fileUtils.version_up(self.scence_path, self.weights_file)  #��������һ��
        exist_data = self.import_data()  #��ȡ�ѱ����bsȨ����Ϣjson�ļ�����
        if not exist_data or 'bs_weights_dict' not in exist_data:
            exist_data['bs_weights_dict'] = {}

        if bs_weights:  #��ѡ����ĳЩbs
            for bs_weight in bs_weights:  #���ϰ��¼��Ȩ����Ϣ����ָ����bs��Ϣ
                exist_data['bs_weights_dict'][bs_weight] = self.bs_weights_dict[bs_weight]
        else:  #δָ������bsʱ������ǰbsȫ���滻ΪҪд�����Ϣ
            exist_data['bs_weights_dict'] = self.bs_weights_dict

        fileUtils.writeInfoAsFile(self.scence_path, self.weights_file, exist_data)
        fb_print("�ѽ�{}��ָ����bsȨ����Ϣд�뵽{}.json��".format(self.weights_handle, self.scence_path), info=True)

    def import_connections(self, bs_weights=None):
        """
        ��json�ļ��ж�ȡbsHandl��������Ϣ��������Щ����
        :param bs_weights: ָ��ֻ������Щbs��ΪNoneʱȫ���滻
        :return:
        """
        input_data = self.import_data()  #��ȡ���е�json�ļ���Ϣ

        if input_data and 'bs_weights_dict' in input_data:
            if input_data['bs_weights_dict']:  #�����key����ʱ
                if bs_weights:  #ָ����ֻ��ĳЩbs����ʱ
                    for bs_weight in bs_weights:
                        if bs_weight in input_data['bs_weights_dict']:  #�����bs���������json�ļ���ʱ
                            inputs = input_data['bs_weights_dict'][bs_weight]
                            if mc.objExists(inputs[0]):  #�����������Դ���ʱ
                                self.disconnect_ctrls_to_bsHandl([bs_weight])  #�Ͽ������������ؼ�֡��bsHandl������
                                self.set_bs_weight_attr(bs_weight, inputs[0], inputs[1])  #�����µ�����
                            else:
                                fb_print("������������{}������".format(inputs[0]), warning=True)
                else:
                    self.set_bs_weights_attrs(input_data=input_data['bs_weights_dict'])

                print("����{}����{}��bsHandl��Ϣ".format(self.weights_handle, self.scence_path))

            else:
                fb_print("�ļ�{}�����ڻ�����Ϊ��".format(self.weights_handle), error=True)

    def import_data(self):
        """
        ��ȡ���е�json�ļ�����
        :return:
        """
        input_data = fileUtils.fromFileReadInfo(self.scence_path, self.weights_file)
        if input_data:
            return input_data

        else:
            fb_print('��¼bsȨ����Ϣ��json�ļ������ڻ�Ϊ�գ��ѷ��ؿ��ֵ�', warning=True)
            return {}
