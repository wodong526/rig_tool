# coding=gbk
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import math

nodeName = 'dongDong'  #�ڵ�������Ҳ�ǽڵ������ļ����ǲ��������
nodeId = om.MTypeId(0x00004)  #���� Maya �������ͱ�ʶ����


class WoDongNode(ompx.MPxNode):
    @classmethod
    def creatorNode(cls):
        return ompx.asMPxPtr(cls())

    @classmethod
    def nodeInitialize(cls):
        """
        ��ʼ���ڵ�
        :return:
        """
        nAttr = om.MFnMatrixAttribute()
        cls.output = nAttr.create('output', 'out', om.MFnMatrixAttribute.kDouble)  #���Գ�����������ֵ���͡�Ĭ��ֵ
        nAttr.setStorable(False)  #�ɴ���
        #nAttr.setWritable(False)#��д
        cls.addAttribute(cls.output)

        cls.input = nAttr.create('input', 'in', om.MFnMatrixAttribute.kDouble)  #���Գ�����������ֵ���͡�Ĭ��ֵ
        nAttr.setArray(True)
        nAttr.setStorable(True)  #�ɴ���
        nAttr.setConnectable(True)  #������
        nAttr.setWritable(True)  #��д
        nAttr.setKeyable(True)  #��k֡
        cls.addAttribute(cls.input)

        #���������Է����仯ʱ��ֻ����ָ����������ԡ�������Բ��ܱ�����Ϊ��k֡������÷���ʧЧ��
        # ����ڵ��ʼ��û��ʹ�ø÷������򲻻����compute����,�����������Է����ı䲻��ˢ��compute
        cls.attributeAffects(cls.input, cls.output)

    @classmethod
    def compute_center_matrix(cls, matrix_array):
        """
        ����MMatrixArray�����ĵ㣬����ת����������ֻ�ܼ�����ȷλ��
        :param matrix_array:MMatrixArray
        :return:
        """
        num_matrices = matrix_array.length()  #���鳤��
        if num_matrices < 2:
            return matrix_array[0]

        total = om.MMatrix()
        for i in range(num_matrices):
            total *= matrix_array[i]

        total = total * (1.0 / num_matrices)
        cls.get_mat(total)  #��ӡ����
        return total

    @staticmethod
    def get_mat(mat):
        """
        ��ӡMMatrix����
        :param mat: ����ӡ��MMatrix
        :return:
        """
        for row in range(4):
            row_values = []
            for col in range(4):
                element_value = mat(row, col)
                row_values.append(element_value)
            print(row_values)

    def __init__(self):
        super(WoDongNode, self).__init__()

    def compute(self, plug, dataBlok):
        """
        ���ݽڵ��������¼�����������plug������Ҫ���¼��������ֵ��dataBlok����ڵ��������ԵĴ洢��
        :param plug:��Ҫ���¼��������
        :param dataBlok:�����ڵ����Դ洢�����ݿ�
        :return:kSuccess����ɹ�;kFailure����ʧ��
        """
        if plug == self.output:
            inputValue = dataBlok.inputArrayValue(self.input)
            outHandle = dataBlok.outputValue(self.output)

            mat_arr = om.MMatrixArray()
            for i in range(inputValue.elementCount()):
                inputValue.jumpToElement(i)
                val = inputValue.inputValue().asMatrix()
                mat_arr.append(val)

            center = self.compute_center_matrix(mat_arr)
            outHandle.setMMatrix(center)
            dataBlok.setClean(plug)
            return True
        else:
            return om.kUnknownParameter


def initializePlugin(mobject):
    plugin = ompx.MFnPlugin(mobject, 'woDong', '0.1', 'Any')  #mobject,�����Ӧ�̣��汾��������õ�api�汾��anyΪ���У�
    try:
        plugin.registerNode(nodeName, nodeId, WoDongNode.creatorNode, WoDongNode.nodeInitialize,
                            ompx.MPxNode.kDependNode)  #�ڵ����������ڵ�id��������������ʼ������
        om.MGlobal.displayInfo('���سɹ���')
    except Exception as e:
        om.MGlobal.displayError('���ط�������{}��'.format(e))


def uninitializePlugin(mobject):
    plugin = ompx.MFnPlugin(mobject)
    try:
        plugin.deregisterNode(nodeId)
        om.MGlobal.displayInfo('ȡ�����سɹ���')
    except Exception as e:
        om.MGlobal.displayError('ȡ�����ط�������{}��'.format(e))
