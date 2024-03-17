# coding=gbk
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import math

nodeName = 'cuttingImages'  #节点类型名也是节点名，文件名是插件的名字
nodeId = om.MTypeId(0x00004)  #管理 Maya 对象类型标识符。


class WoDongNode(ompx.MPxNode):
    outputU = None
    outputV = None

    @classmethod
    def creatorNode(cls):
        return ompx.asMPxPtr(cls())

    @classmethod
    def nodeInitialize(cls):
        """
        初始化节点
        :return:
        """
        nAttr = om.MFnNumericAttribute()
        cls.outputU = nAttr.create('outputU', 'outu', om.MFnNumericData.kDouble, 0.0)  #属性长名、短名、值类型、默认值
        nAttr.setStorable(False)#可储存
        nAttr.writable = False
        cls.addAttribute(cls.outputU)

        cls.outputV = nAttr.create('outputV', 'outv', om.MFnNumericData.kDouble, 0.0)  #属性长名、短名、值类型、默认值
        nAttr.setStorable(False)  #可储存
        nAttr.writable = False
        cls.addAttribute(cls.outputV)

        cls.input = nAttr.create('inputValue', 'inV', om.MFnNumericData.kInt, 0.0)  #属性长名、短名、值类型、默认值
        nAttr.setConnectable(True)  #可链接
        nAttr.setWritable(True)  #可写
        nAttr.setKeyable(True)#可k帧
        cls.addAttribute(cls.input)

        #当输入属性发生变化时，只计算指定的输出属性。输出属性不能被设置为可k帧，否则该方法失效。
        # 如果节点初始化没有使用该方法，则不会调用compute函数,即该输入属性发生改变不会刷新compute
        cls.attributeAffects(cls.input, cls.outputU)
        cls.attributeAffects(cls.input, cls.outputV)

    def __init__(self):
        super(WoDongNode, self).__init__()

    def compute(self, plug, dataBlok):
        """
        根据节点输入重新计算给定输出。plug代表需要重新计算的数据值，dataBlok保存节点所有属性的存储。
        :param plug:需要重新计算的属性
        :param dataBlok:包含节点属性存储的数据块
        :return:kSuccess计算成功;kFailure计算失败
        """
        if plug == self.outputU or plug == self.outputV:
            inputValue = dataBlok.inputValue(self.input).asInt()
            outU = dataBlok.outputValue(self.outputU)
            outV = dataBlok.outputValue(self.outputV)

            u = (inputValue+5)%5*0.2
            v = (4-inputValue/5)*0.2

            outU.setDouble(u)
            outV.setDouble(v)

            dataBlok.setClean(plug)


def initializePlugin(mobject):
    plugin = ompx.MFnPlugin(mobject, 'woDong', '0.1', 'Any')  #mobject,插进供应商，版本，插件适用的api版本（any为所有）
    try:
        plugin.registerNode(nodeName, nodeId, WoDongNode.creatorNode, WoDongNode.nodeInitialize,
                            ompx.MPxNode.kDependNode)  #节点类型名，节点id，创建函数，初始化函数
        om.MGlobal.displayInfo('加载成功！')
    except Exception as e:
        om.MGlobal.displayError('加载发生错误：{}。'.format(e))


def uninitializePlugin(mobject):
    plugin = ompx.MFnPlugin(mobject)
    try:
        plugin.deregisterNode(nodeId)
        om.MGlobal.displayInfo('取消加载成功！')
    except Exception as e:
        om.MGlobal.displayError('取消加载发生错误：{}。'.format(e))