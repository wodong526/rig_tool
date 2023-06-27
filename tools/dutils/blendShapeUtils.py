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
    将指定下标bs镜像到另一个下标的目标体上
    :param bs: 要镜像的bs节点
    :param src:要镜像的bs目标体下标
    :param dst:要镜像到的bs目标体下标
    :param side:要镜像的轴
    :return:none
    """
    mc.blendShape(bs, e=1, rtd=[0, dst])
    mc.blendShape(bs, e=1, cd=[0, src, dst])
    mc.blendShape(bs, e=1, ft=[0, dst], sa=side, ss=1)

    mc.symmetricModelling(s=0, e=1)  #关闭基于对象镜像
    bsNam_lis = mc.listAttr(bs + ".w", k=True, m=True)
    fb_print('已将{}的{}目标体镜像到{}目标体'.format(bs, bsNam_lis[src], bsNam_lis[dst]), info=True)


def create_blendshape(base_geo, name=None, origin='local', deform_order=None):
    """
    为指定对象创建bs
    :param base_geo:
    :param name:
    :param origin:
    :param deform_order:
    :return:
    """
    if not name:
        name = 'BS_{}'.format(base_geo)

    if mc.objExists(name):
        fb_print('节点名{}已经存在，请重新指定BS节点名称'.format(name), error=True, viewMes=True)

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

        if not weights_handle:  # 获取权重控制柄定位器
            weights_handle = 'trs_{}_whMaster'.format(blendshape)
        if not mc.objExists(blendshape):  # 检查它是否是混合形状节点
            fb_print('BS节点{}不存在，请重新指定BS节点'.format(blendshape), error=True, viewMes=True)

        self.weights_handle = self.create_weights_trs(blendshape, weights_handle)  # 创建连接到混合形状的权重组
        self.weights_file = '{}.json'.format(self.weights_handle)  # 储存bs权重信息的json文件名

        # 获取权重输入信息字典
        self.bs_weights_dict = attrUtils.get_string_info(self.weights_handle, 'BS_Weights_Dict')
        if not self.bs_weights_dict:  #没有就定义为空字典
            self.bs_weights_dict = {}

        # 获取权重组信息列表。层次结构词典列表
        # 带键（“父级”）、值（组名）、键（子级）、值（权重属性名称）
        self.bs_weights_groups_list = attrUtils.get_string_info(self.weights_handle, 'BS_Weights_Groups_List')
        if not self.bs_weights_groups_list:
            self.bs_weights_groups_list = [{'parent': '', 'children': []}]  #父级：、子级：

        self.data = {'bs_weights_dict': self.bs_weights_dict,
                     'bs_weights_groups_list': self.bs_weights_groups_list}

    def create_weights_trs(self, blendshape, weights_handle):
        """
        检查是否有承载bs的组，没有就创建
        当这个组的blendShapeNode属性跟bs节点的weightsHandle没有链接时删除除blendShapeNode外的所有属性并连接这两个属性
        :param blendshape: 获取bs权重的bs节点
        :param weights_handle: 承载bs权重信息的组的名字
        :return:承载bs权重信息的组名
        """
        if not mc.objExists(weights_handle) or mc.nodeType(weights_handle) != 'transform':
            weights_handle = mc.group(name=weights_handle, em=True, w=True)
            attrUtils.lock_and_hide_attrs(weights_handle, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
                                          lock=True, hide=True)

        # 检查它是否具有混合形状节点的消息连接属性，如果没有创建一个。
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
        在bsHandl上的BS_Weights_Dict属性记录下所有bs的名字、控制器及属性、属性的驱动值
        :param bs_weight_name: bs名
        :param ctrl_attr: 控制器及属性名
        :param value: 属性的驱动值
        :return:
        """
        if mc.objExists(ctrl_attr):
            #如果 bs 权重属性名称与现有组名称冲突。
            for i in range(len(self.bs_weights_groups_list)):
                if bs_weight_name == self.bs_weights_groups_list[i]['parent']:
                    fb_print('{} 名称已作为组名称存在于此权重句柄上,再选一个！'.format(bs_weight_name), error=True)

            # 如果bs_weight_name存在且没有连接输入，请设置权重驱动程序
            if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):

                connections = mc.listConnections('{}.{}'.format(self.weights_handle, bs_weight_name), p=True, d=False)
                if connections:
                    fb_print('BS权重属性{}已存在并具有连接，选择另一个BS权重属性名称！'.format(bs_weight_name),
                             error=True)
                else:
                    return_attr = [None, bs_weight_name]

            else:  # 如果bs_weight_name不存在，请创建一个，权重值为 0 到 1。
                mc.addAttr(self.weights_handle, ln=bs_weight_name, nn=bs_weight_name, at='double', min=0, max=1,
                           dv=0, keyable=True)
                # 如果之前未添加，请将bs_weight_name添加到顶部组
                self.bs_weights_groups_list[0]['children'].append(bs_weight_name)
                return_attr = [bs_weight_name, None]

            # 将驱动键从 Ctrl 设置为 BS 权重属性
            mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear', ott='linear',
                                 currentDriver=ctrl_attr, driverValue=value[0], value=0)
            mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear', ott='linear',
                                 currentDriver=ctrl_attr, driverValue=value[1], value=1)

            self.bs_weights_dict[bs_weight_name] = (ctrl_attr, value)
            attrUtils.add_string_info(self.bs_weights_dict, self.weights_handle, 'BS_Weights_Dict')
            attrUtils.add_string_info(self.bs_weights_groups_list, self.weights_handle, 'BS_Weights_Groups_List')
            return return_attr
        else:
            fb_print('控制器属性{}不存在'.format(ctrl_attr), error=True)

    def set_bs_weights_attrs(self, input_data):
        """
        刷新链接指定的bs与控制器的链接
        :param input_data: 链接信息字典
        :return:
        """
        for bs_weight_name, inputs in input_data.items():
            if mc.objExists(inputs[0]):  #控制器及属性是否存在
                if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):  #当bsHandl的bs信息存在，则断开这个链接
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

                self.bs_weights_dict[bs_weight_name] = inputs  #刷新这个bs的信息
            else:
                mc.warning("控制器及属性{}不存在".format(inputs[0]))

        attrUtils.add_string_info(self.bs_weights_dict, self.weights_handle, 'BS_Weights_Dict')
        attrUtils.add_string_info(self.bs_weights_groups_list, self.weights_handle, 'BS_Weights_Groups_List')

    def disconnect_ctrls_to_bsHandl(self, bs_weights=None):
        """
        断开指定链接
        :param bs_weights:要断开的bs列表，为None时断开全部
        :return:
        """
        bs_weights_names = self.bs_weights_dict.keys()

        if bs_weights:  #取指定bs与已有bs两个集合的交集对象
            bs_weights_names = toolUtils.list_operation(list_a=bs_weights, list_b=bs_weights_names, operation='&')

        for bs_weight_name in bs_weights_names:
            if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):  #这个bs名的属性存在时
                connections = mc.listConnections('{}.{}'.format(self.weights_handle, bs_weight_name), p=True, d=False)
                if connections:
                    mc.disconnectAttr(connections[0], '{}.{}'.format(self.weights_handle, bs_weight_name))
                    fb_print('已断开{}的链接'.format(bs_weight_name), info=True)
                    mc.delete(connections[0].split('.')[0])
                else:
                    fb_print('{}没有上游链接'.format(bs_weight_name), warning=True)

    def reconnect_ctrls_to_bsHandl(self, bs_weights=None):
        """
        刷新bs链接与bsHandl上记录的bs驱动信息
        :param bs_weights: 指定的要重连的bs列表，为None时全部冲脸
        :return:
        """
        bs_weights_names = self.bs_weights_dict.keys()  #bsHandl上的bs名称列表

        if bs_weights:
            bs_weights_names = toolUtils.list_operation(bs_weights, bs_weights_names, '&')  #指定的与已有的的交集元素

        for bs_weight_name in bs_weights_names:
            ctrl_attr, value = self.bs_weights_dict[bs_weight_name]  #返回链接该bs的（控制器属性，值）

            if mc.objExists(ctrl_attr):  #这个控制器属性是否存在
                if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):  #bsHandl是否有这个bs属性
                    connections = mc.listConnections('{}.{}'.format(self.weights_handle, bs_weight_name), p=True,
                                                     d=False)  #上游
                    if connections:  #断开链接
                        mc.disconnectAttr(connections[0], '{}.{}'.format(self.weights_handle, bs_weight_name))

                    # 将驱动键从 Ctrl 设置为 BS 权重属性。
                    mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear',
                                         ott='linear', currentDriver=ctrl_attr, driverValue=value[0], value=0)

                    mc.setDrivenKeyframe('{}.{}'.format(self.weights_handle, bs_weight_name), itt='linear',
                                         ott='linear', currentDriver=ctrl_attr, driverValue=value[1], value=1)
                else:  #如果bsHandl没有这个属性，就在记录列表里删除这个bs项
                    del self.bs_weights_dict[bs_weight_name]
            else:
                if mc.objExists('{}.{}'.format(self.weights_handle, bs_weight_name)):
                    mc.deleteAttr('{}.{}'.format(self.weights_handle, bs_weight_name))
                del self.bs_weights_dict[bs_weight_name]
                fb_print('连接到{0}上的{1}的控制器属性{2}不存在, bsHandl的属性与记录的bs信息中已删除bs:{1}'.format(
                    self.weights_handle, bs_weight_name, ctrl_attr), warning=True)

        attrUtils.add_string_info(self.bs_weights_dict, self.weights_handle, 'BS_Weights_Dict')  #在bsHandl上重新写入最新的bs信息
        fb_print('bsHandl的属性链接已刷新', info=True)

    def export_connections(self, bs_weights=None):
        """
        将指定的bsHandl上的bs信息写入到json中
        :param bs_weights: 当有指定bs名时只增加写入这些bs的信息，没有时写入所有
        :return:
        """
        fileUtils.version_up(self.scence_path, self.weights_file)  #迭代保存一次
        exist_data = self.import_data()  #读取已保存的bs权重信息json文件内容
        if not exist_data or 'bs_weights_dict' not in exist_data:
            exist_data['bs_weights_dict'] = {}

        if bs_weights:  #当选定了某些bs
            for bs_weight in bs_weights:  #在老版记录的权重信息更新指定的bs信息
                exist_data['bs_weights_dict'][bs_weight] = self.bs_weights_dict[bs_weight]
        else:  #未指定具体bs时，将当前bs全部替换为要写入的信息
            exist_data['bs_weights_dict'] = self.bs_weights_dict

        fileUtils.writeInfoAsFile(self.scence_path, self.weights_file, exist_data)
        fb_print("已将{}上指定的bs权重信息写入到{}.json中".format(self.weights_handle, self.scence_path), info=True)

    def import_connections(self, bs_weights=None):
        """
        从json文件中读取bsHandl的链接信息并重连这些链接
        :param bs_weights: 指定只重连这些bs，为None时全部替换
        :return:
        """
        input_data = self.import_data()  #获取已有的json文件信息

        if input_data and 'bs_weights_dict' in input_data:
            if input_data['bs_weights_dict']:  #当这个key存在时
                if bs_weights:  #指定了只读某些bs对象时
                    for bs_weight in bs_weights:
                        if bs_weight in input_data['bs_weights_dict']:  #当这个bs存在于这个json文件内时
                            inputs = input_data['bs_weights_dict'][bs_weight]
                            if mc.objExists(inputs[0]):  #控制器及属性存在时
                                self.disconnect_ctrls_to_bsHandl([bs_weight])  #断开控制器驱动关键帧与bsHandl的链接
                                self.set_bs_weight_attr(bs_weight, inputs[0], inputs[1])  #建立新的连接
                            else:
                                fb_print("控制器及属性{}不存在".format(inputs[0]), warning=True)
                else:
                    self.set_bs_weights_attrs(input_data=input_data['bs_weights_dict'])

                print("已在{}重连{}的bsHandl信息".format(self.weights_handle, self.scence_path))

            else:
                fb_print("文件{}不存在或内容为空".format(self.weights_handle), error=True)

    def import_data(self):
        """
        读取已有的json文件内容
        :return:
        """
        input_data = fileUtils.fromFileReadInfo(self.scence_path, self.weights_file)
        if input_data:
            return input_data

        else:
            fb_print('记录bs权重信息的json文件不存在或为空，已返回空字典', warning=True)
            return {}
