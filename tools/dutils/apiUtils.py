# coding=gbk
import maya.cmds as mc
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as omain

from feedback_tool import Feedback_info as fp


def getApiNode(obj=None, dag=True, com=False):
    """
    ��ȡ�����MDagPath
    :param com: �����Ҫ��ȡ����������򷵻������dagPath
    :param dag: �Ƿ�ֻ����dag�ڵ�
    :param obj:(str) Ҫ��ȡ�Ķ���
    :return:
    """
    if obj:
        sel = om.MGlobal.getSelectionListByName(obj)
    else:
        sel = om.MGlobal.getActiveSelectionList()

    if sel.isEmpty():
        fp('û��ָ���κζ���', error=True)
        return None

    if dag:
        if com:
            return sel.getComponent(0)
        else:
            return sel.getDagPath(0)
    else:
        return sel.getDependNode(0)


def rename(objs=None, prefix=None, suffix=None, replace=None, lower=False, upper=False, select=False):
    # type: ([str], str, str, list[str, str], bool, bool, bool) -> None
    """
    ����������
    :param objs: Ҫ�������Ķ���,��������ʱ�����볤��
    :param prefix: ǰ׺
    :param suffix: ��׺
    :param replace: �滻�б�
    :param lower: Сд
    :param upper: ��д
    :param select: �Ƿ�ֻ����ѡ�ж���
    :return:
    """
    if select:
        sel = om.MGlobal.getActiveSelectionList()
    else:
        sel = om.MSelectionList()
        for obj in objs:
            sel.add(obj)
    mit = om.MItSelectionList(sel)

    while not mit.isDone():
        node = om.MFnDependencyNode(mit.getDependNode())
        old_name = node.name()

        if prefix:
            old_name = prefix + old_name
        if suffix:
            old_name = old_name + suffix
        if replace:
            old_name = old_name.replace(replace[0], replace[1])
        if lower:
            old_name = old_name.lower()
        if upper:
            old_name = old_name.upper()

        node.setName(old_name)
        mit.next()

def create_node(node_type, name=None, dg=False):
    # type: (str, str|None, bool|None) -> om.MObject
    """
    �����ڵ�
    :param node_type: �ڵ�����
    :param name: �ڵ���,�����ָ������node_type����
    :param dg: �����Ľڵ���dg�ڵ�ʱ��Ҫ����Ϊtrue
    :return: �ڵ��object����
    """
    if dg:
        mod = om.MDGModifier()
    else:
        mod = om.MDagModifier()
    obj = mod.createNode(node_type)
    mod.renameNode(obj, name if name else '{}*'.format(node_type))
    mod.doIt()

    return obj

def connect_plug(sor_node, sor_attr, end_node, end_attr):
    # type: (str, str, str, str) -> bool
    """
    ��������plug
    :param end_node: ���νڵ���
    :param sor_node: ���νڵ���
    :param sor_attr:����������
    :param end_attr:����������
    :return:
    """
    mod = om.MDGModifier()
    mod.connect(get_attr(sor_node, sor_attr), get_attr(end_node, end_attr))
    mod.doIt()
    return True

def get_attr(node, attr):
    # type: (str, str) -> om.MPlug
    """
    ��ȡ�ڵ����Ե�plug����
    :param node: �ڵ���
    :param attr: ������
    :return: ���Ե�plug����
    """
    return om.MFnDependencyNode(getApiNode(node, dag=False)).findPlug(attr.split('.')[-1], False)

def get_sub_plug(node, attr):
    # type: (str, str) -> list[str]
    """
    ��ȡ������
    :param node: �ڵ���
    :param attr: ������
    :return: ��������������list
    """
    compound_attr_obj = om.MFnDependencyNode(node).attribute(attr)
    compound_attr = om.MFnCompoundAttribute(compound_attr_obj)

    child_attrs = []
    for i in range(compound_attr.numChildren()):
        child_attr = om.MFnAttribute(compound_attr.child(i))
        child_attrs.append(child_attr.name)

    return child_attrs

def set_attr(node, attr, value):
    # type: (str, str, str|float|int|bool|list|tuple) -> None
    """
    ���ö��������
    :param node: �ڵ���
    :param attr: ������
    :param value: ����ֵ
    :return:
    """
    if get_attr(node, attr).isCompound:
        if isinstance(value, list) or isinstance(value, tuple):
            for attr, val in zip(get_sub_plug(getApiNode(node, dag=False), attr), value):
                set_attr(node, attr, val)
        else:
            fp('����{}�Ǹ������ԣ�Ӧ����[list|tuple]���ͣ�ʵ��Ϊ{}����'.format(attr, type(value)), error=True)
        return

    if isinstance(value, str):
        get_attr(node, attr).setString(value)
    elif isinstance(value, float):
        get_attr(node, attr).setFloat(value)
    elif isinstance(value, int):
        get_attr(node, attr).setInt(value)
    elif isinstance(value, bool):
        get_attr(node, attr).setBool(value)
    else:
        print('{}Ϊ��֧�ֵ��������ͣ�{}'.format(value, type(value)))

def getMPoint(obj):
    # type: (str) -> om.MPoint
    """
    ��ȡ�������������xyz����
    :param obj: Ҫ��ȡ����Ķ���
    :return: MPoint����
    """
    pos = mc.xform(obj, q=True, t=True, ws=True)

    return om.MPoint(pos[0], pos[1], pos[2], 1.0)


def getGeometryComponents(fn_skin):
    # type: (omain.MFnSkinCluster) -> tuple[om.MDagPath, om.MObject]
    """
    ��MFnSkinCluster���Ͷ����ȡ�ýڵ��dagPath�������Ƥ�������
    :param fn_skin:MFnSkinCluster�ڵ�
    :return:��Ƥ�ڵ��dagPath������Ƥ�ڵ������ڵ�
    """
    for ii in range(fn_skin.findPlug("input", False).evaluateNumElements()):
        # get the input shape and component for this index
        shape_obj = fn_skin.inputShapeAtIndex(ii)
        shape_dag_path = om.MDagPath.getAPathTo(shape_obj)
        transform_dag_path = om.MDagPath(shape_dag_path)
        transform_dag_path.pop()
        component = fn_skin.getComponentAtIndex(ii)

        return transform_dag_path, component

def getCurrentWeights(fn_skin, dag_path, components, influences_nam=None):
    """
    ͨ��MFnSkinCluster�����ȡ����Ƥ�ڵ��Ȩ���б�
    :param influences_nam: ��ָ���ؽ�����ʱ���ظùؽڵ�Ȩ��
    :param fn_skin: MFnSkinCluster�ڵ�
    :param dag_path: ��Ƥ�����dagPath����
    :param components: ��Ƥ������������
    :return:Ȩ�����飬��������Ϊ����һ����İ��ؽ�˳���Ȩ��ֵ���ڶ�����ġ�������
    """
    if not influences_nam:
        return fn_skin.getWeights(dag_path, components)[0]

    try:
        return fn_skin.getWeights(dag_path, components, fromSkinGetInfluence(fn_skin).index(influences_nam))
    except ValueError:
        fp('��Ƥ�ؽ�{}������'.format(influences_nam), warning=True)
        return None

def setCurrentWeights(fn, weights, influences_num, dag_path, components):
    """
    ��Ȩ���б��ֵ���赽MFnSkinCluster����
    :param fn: MFnSkinCluster�ڵ�
    :param weights: Ȩ��ֵ�б�
    :param influences_num: Ӱ��ؽڶ���
    :param dag_path: ��Ƥ�ڵ��dagPath����
    :param components: ��Ƥ�ڵ������ڵ�
    :return:
    """
    influenceIndices = om.MIntArray()
    for ii in range(influences_num):
        influenceIndices.insert(ii, ii)
    fn.setWeights(dag_path, components, influenceIndices, weights)

def get_skinModelName(skin_cluster_fn):
    """
    ͨ��MFnSkinCluster�����ȡ����Ƥ���������
    :param skin_cluster_fn:
    :return:
    """
    if type(skin_cluster_fn) == omain.MFnSkinCluster:
        pass
    else:
        fp('����{}����MFnSkinCluster����'.format(skin_cluster_fn))

    influenced_objects = skin_cluster_fn.getOutputGeometry()
    influenced_model_names = []
    for i in range(influenced_objects.__len__()):
        influenced_model_fn = om.MFnDagNode(influenced_objects[i])
        influenced_model_name = influenced_model_fn.partialPathName()
        influenced_model_names.append(influenced_model_name)

    return influenced_model_names

def get_skinModelType(skin_cluster_fn):
    """
    ͨ��MFnSkinCluster�����ȡ����Ƥ���������
    :param skin_cluster_fn: MFnSkinCluster�ڵ�
    :return:����Ƥ������������
    """
    if type(skin_cluster_fn) == omain.MFnSkinCluster:
        pass
    else:
        fp('����{}����MFnSkinCluster����'.format(skin_cluster_fn))

    influenced_objects = skin_cluster_fn.getInputGeometry()
    for i in range(influenced_objects.__len__()):
        input_object = influenced_objects[i]
        dg_iterator = om.MItDependencyGraph(input_object, om.MFn.kInvalid, om.MItDependencyGraph.kUpstream,
                                            om.MItDependencyGraph.kDepthFirst, om.MItDependencyGraph.kPlugLevel)

        while not dg_iterator.isDone():
            current_node = dg_iterator.currentNode()
            if current_node.hasFn(om.MFn.kNurbsSurface):
                return 'nurbsSurface'
            elif current_node.hasFn(om.MFn.kNurbsCurve):
                return 'nurbsCurve'
            elif current_node.hasFn(om.MFn.kMesh):
                return 'mesh'

            dg_iterator.next()


def fromObjGetRigNode(obj=None, skin=True, blend_shape=False, path_name=True):
    """
    ���ַ�����transform�����ȡ��ģ�͵İ�������ͽڵ�
    :param blend_shape: ��ȡbs�ڵ�
    :param skin: ��Ƥ�ڵ�
    :param obj: transform�����ַ���
    :param path_name: ����ʱ�Ƿ񷵻�api�����б�Ϊ�棨Ĭ�ϣ�ʱ���ؽڵ������б�
    :return:����ؽڵ��б�
    """
    if not isinstance(obj, om.MDagPath):
        dagNode = getApiNode(obj)
    else:
        dagNode = obj

    try:
        dagNode.extendToShape()
    except RuntimeError:
        fp('����{}û��shape�ڵ��ֹһ��shape�ڵ㡣'.format(dagNode.partialPathName()), error=True)
    m_object = dagNode.node()

    if skin:
        itDG = om.MItDependencyGraph(m_object, om.MFn.kSkinClusterFilter, om.MItDependencyGraph.kUpstream)
    elif blend_shape:
        itDG = om.MItDependencyGraph(m_object, om.MFn.kBlendShape, om.MItDependencyGraph.kUpstream)
    else:
        fp('û��ָ��Ҫ��ȡ�Ľڵ����', error=True)

    ret_lis = []
    while not itDG.isDone():
        item = itDG.currentNode()

        skin = omain.MFnSkinCluster(item) if skin else omain.MFnBlendShapeDeformer(item)
        ret_lis.append(skin)
        itDG.next()


    if path_name:
        return [node.name() for node in ret_lis]
    else:
        return ret_lis


def fromSkinGetInfluence(fn_skin):
    """
    ��MFnSkinCluster�����Ӱ��ؽ�
    :param fn_skin:MFnSkinCluster����
    :return:Ӱ��ؽ��б�
    """
    influence_lis = []
    dagArr = fn_skin.influenceObjects()
    for i in range(dagArr.__len__()):
        if om.MFnDagNode(dagArr[i]).typeName == 'joint':
            influence_lis.append(dagArr[i].partialPathName())

    return influence_lis
