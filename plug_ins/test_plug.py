# coding=gbk
import maya.api.OpenMaya as om
import maya.OpenMayaMPx as ompx
import pdb

# nodeName = 'fromMeshGetDistance'  #�ڵ�������Ҳ�ǽڵ������ļ����ǲ��������
# nodeId = om.MTypeId(0x83002)  #���� Maya �������ͱ�ʶ����

class GetClosestIntersection(object):
    def __init__(self):
        self._mod = om.MFnMesh()
        self._ray_source = om.MPoint()
        self._ray_vector = om.MFloatVector()
        self._max_param = int()

    def set_fn_mesh(self, fn_mesh):
        self._mod = fn_mesh

    def set_ray_source(self, float_point):
        self._ray_source = float_point

    def set_ray_vector(self, float_vector):
        self._ray_vector = float_vector

    def set_max_param(self, param):
        self._max_param = param

    def get_distance(self):
        """
        ���طֱ��ǣ����е㣬����㵽���е�ľ��룬���е���id�����е�������id,���е����������ϵ���������

        ���е����������ϵ�����������һ���������������������飬��ʾ�����ڱ����е��������ϵ��������ꡣ��������������һ������һ���������ڲ�λ�õ�һ�ֳ��÷�����
        ��һ���������ڣ��κ�һ�㶼���Ա�ʾΪ��������ļ�Ȩ�ͣ���Щ�����Ϊ��������ϵ�Ļ��������������� ABC���������� (u, v, w) ��ʾΪ��
        u������ BC ���ϵľ������ AB �ĳ���֮�ȡ�
        v������ AC ���ϵľ������ BC �ĳ���֮�ȡ�
        w������ AB ���ϵľ������ AC �ĳ���֮�ȡ�
        ����������ܺ�ʼ��Ϊ 1����� (u, v, w) λ�ڵ�λ�������ڡ�����ζ�����������ڣ��κ�һ�㶼������������ֵ�������������ʾ���� P = uA + vB + wC������ A��B��C �������εĶ���
        :return:
        """
        _, distance, _, _, _, _ = self._mod.closestIntersection(self._ray_source, self._ray_vector,
                                                                om.MSpace.kWorld, self._max_param, False)
        if distance > 0:
            print(self._ray_source)
            print(self._ray_vector)
            print(distance)
            return distance
        else:
            return 0

class WoDongNode(om.MPxNode):
    rayMesh = om.MObject()#ģ�Ͷ���
    sourceArray = om.MObject()#����Դ��
    targetArray = om.MObject()#�����յ�
    startArray = om.MObject()#�����
    max_param = om.MObject()#������
    outDistance = om.MObject()  #����㵽ģ�͵ľ���

    nodeName = 'fromMeshGetDistance'  # �ڵ�������Ҳ�ǽڵ������ļ����ǲ��������
    nodeId = om.MTypeId(0x83002)  # ���� Maya �������ͱ�ʶ����

    @classmethod
    def update_attr_properties(cls, attr):
        attr.storable = True#�ɴ���
        attr.readable = True#�ɶ�
        attr.connectable = True
        if attr.type() == om.MFn.kNumericAttribute:  #�����������������
            attr.keyable = True#��k֡

    @classmethod
    def creatorNode(cls):
        return WoDongNode()

    @classmethod
    def nodeInitialize(cls):
        """
        ��ʼ���ڵ�
        :return:
        """
        typeAttr = om.MFnTypedAttribute()
        numAttr = om.MFnNumericAttribute()
        mAttr = om.MFnMatrixAttribute()
        compAttr = om.MFnCompoundAttribute()

        WoDongNode.rayMesh = typeAttr.create("inputMesh", "inMesh", om.MFnData.kMesh)
        cls.update_attr_properties(typeAttr)
        om.MPxNode.addAttribute(WoDongNode.rayMesh)

        WoDongNode.sourceArray = mAttr.create("sourceArray", "sorArry", om.MFnMatrixAttribute.kDouble)
        om.MPxNode.addAttribute(WoDongNode.sourceArray)#������ʼ��

        WoDongNode.targetArray = mAttr.create("targetArray", "tagArry", om.MFnMatrixAttribute.kDouble)
        om.MPxNode.addAttribute(WoDongNode.targetArray)#�����յ�

        WoDongNode.array = compAttr.create("array", "arry")
        cls.update_attr_properties(compAttr)
        compAttr.addChild(WoDongNode.sourceArray)
        compAttr.addChild(WoDongNode.targetArray)
        om.MPxNode.addAttribute(WoDongNode.array)#��������

        WoDongNode.startArray = mAttr.create("startArray", "starArry", om.MFnMatrixAttribute.kDouble)
        om.MPxNode.addAttribute(WoDongNode.startArray)#�����

        WoDongNode.max_param = numAttr.create('maxParam', 'mp', om.MFnNumericData.kInt, 9999)
        cls.update_attr_properties(numAttr)
        om.MPxNode.addAttribute(WoDongNode.max_param)

        WoDongNode.outDistance = numAttr.create("Distance", "dis", om.MFnNumericData.kFloat, 0.0)
        numAttr.readable = True
        numAttr.writable = False
        numAttr.storable = True
        numAttr.keyable = False
        om.MPxNode.addAttribute(WoDongNode.outDistance)#�������

        om.MPxNode.attributeAffects(WoDongNode.rayMesh, WoDongNode.outDistance)
        om.MPxNode.attributeAffects(WoDongNode.array, WoDongNode.outDistance)
        om.MPxNode.attributeAffects(WoDongNode.startArray, WoDongNode.outDistance)
        om.MPxNode.attributeAffects(WoDongNode.max_param, WoDongNode.outDistance)

    def __init__(self):
        super(WoDongNode, self).__init__()
        self.ray = GetClosestIntersection()

    def compute(self, plug, dataBlok):
        if plug == WoDongNode.outDistance:
            mfn_mesh = self.get_upstream_nod()
            sor_array = om.MTransformationMatrix(dataBlok.inputValue(WoDongNode.sourceArray).asMatrix()).translation(om.MSpace.kWorld)
            tag_array = om.MTransformationMatrix(dataBlok.inputValue(WoDongNode.targetArray).asMatrix()).translation(om.MSpace.kWorld)
            star_array = om.MTransformationMatrix(dataBlok.inputValue(WoDongNode.startArray).asMatrix()).translation(om.MSpace.kWorld)
            max_param = dataBlok.inputValue(WoDongNode.max_param).asInt()
            outputAttr = dataBlok.outputValue(WoDongNode.outDistance)

            if mfn_mesh:
                sor_point = om.MFloatPoint(star_array)
                vector_fVector = om.MFloatVector(tag_array - sor_array).normal()

                self.ray.set_ray_source(sor_point)
                self.ray.set_ray_vector(vector_fVector)
                self.ray.set_max_param(max_param)
                self.ray.set_fn_mesh(mfn_mesh)
                distance = self.ray.get_distance()
                outputAttr.setFloat(distance) if distance else outputAttr.setFloat(0.0)
            else:
                outputAttr.setFloat(0.0)
        return

    def get_upstream_nod(self):
        """
        ��ȡ����mesh�ڵ�
        :return:
        """
        dpd_nod = om.MFnDependencyNode(self.thisMObject())
        plug = dpd_nod.findPlug('inputMesh', False)

        mit = om.MItDependencyGraph(plug, om.MFn.kMesh, om.MItDependencyGraph.kUpstream,
                                    om.MItDependencyGraph.kDepthFirst, om.MItDependencyGraph.kNodeLevel)
        mesh_node = None
        while not mit.isDone():
            mesh_node = mit.currentNode()
            break

        if isinstance(mesh_node, om.MObject):
            fn_dag_node = om.MFnDagNode(mesh_node)
            dag_node = fn_dag_node.getPath()
            return om.MFnMesh(dag_node)
        return None

    def doIt(self, args):
        pass

    def redoIt(self):
        pass

    def undoIt(self):
        """
        ���������Ա�����ʱ��ʹ�ó�������øú���
        :return:
        """
        self.fn_mesh.setPoints(self.initial, om.MSpace.kWorld)

    def isUndoable(self):
        """
        Ĭ�Ϸ���false��������Ϊfalse��ʾdoIt�еĲ������ɳ��������к��������٣�����true��ᱣ���������������������ڳ���ʱ����undoIt
        ����doIt����������øú������жϸò����Ƿ�Ϊ�ɳ���
        :return: True
        """
        return True

def maya_useNewAPI():
    pass

def initializePlugin(obj):
    plugin = om.MFnPlugin(obj, 'woDong', '0.1', 'Any')  #mobject,�����Ӧ�̣��汾��������õ�api�汾��anyΪ���У�
    try:
        plugin.registerNode(WoDongNode.nodeName, WoDongNode.nodeId, WoDongNode.creatorNode, WoDongNode.nodeInitialize,
                            om.MPxNode.kDependNode)  #�ڵ����������ڵ�id��������������ʼ������
        om.MGlobal.displayInfo('���سɹ���')
    except Exception as e:
        om.MGlobal.displayError('���ط�������{}��'.format(e))


def uninitializePlugin(mobject):
    plugin = om.MFnPlugin(mobject)
    try:
        plugin.deregisterNode(WoDongNode.nodeId)
        om.MGlobal.displayInfo('ȡ�����سɹ���')
    except Exception as e:
        om.MGlobal.displayError('ȡ�����ط�������{}��'.format(e))