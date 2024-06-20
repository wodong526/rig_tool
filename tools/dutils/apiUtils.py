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


def getMPoint(obj):
    """
    ��ȡ�������������xyz����
    :param obj: Ҫ��ȡ����Ķ���
    :return: MPoint����
    """
    pos = mc.xform(obj, q=True, t=True, ws=True)

    return om.MPoint(pos[0], pos[1], pos[2], 1.0)


def getGeometryComponents(fn_skin):
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
