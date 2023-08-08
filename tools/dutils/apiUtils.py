# coding=gbk
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as omain

from feedback_tool import Feedback_info as fb_print, LIN as lin


def getApiNode(obj, dag=True):
    """
    ��ȡ�����MDagPath
    :param dag: �Ƿ�ֻ����dag�ڵ�
    :param obj:(str) Ҫ��ȡ�Ķ���
    :return:
    """
    sel = om.MSelectionList()
    sel.add(obj)

    if dag:
        m_dag = om.MDagPath()
        sel.getDagPath(0, m_dag)
        return m_dag
    else:
        mobject = om.MObject()
        sel.getDependNode(0, mobject)
        return mobject


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
    fnSet = om.MFnSet(fn_skin.deformerSet())
    members = om.MSelectionList()
    fnSet.getMembers(members, False)
    dagPath = om.MDagPath()
    components = om.MObject()
    members.getDagPath(0, dagPath, components)

    return dagPath, components


def getCurrentWeights(fn_skin, dag_path, components):
    """
    ͨ��MFnSkinCluster�����ȡ����Ƥ�ڵ��Ȩ���б�
    :param fn_skin: MFnSkinCluster�ڵ�
    :param dag_path: ��Ƥ�ڵ��dagPath����
    :param components: ��Ƥ�ڵ������ڵ�
    :return:Ȩ�����飬��������Ϊ����һ����İ��ؽ�˳���Ȩ��ֵ���ڶ�����ġ�������
    """
    weights = om.MDoubleArray()
    util = om.MScriptUtil()
    util.createFromInt(0)
    pUInt = util.asUintPtr()
    fn_skin.getWeights(dag_path, components, weights, pUInt)
    return weights


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
    influenceIndices = om.MIntArray(influences_num)
    for ii in range(influences_num):
        influenceIndices.set(ii, ii)
    fn.setWeights(dag_path, components, influenceIndices, weights, False)


def get_skinModelName(skin_cluster_fn):
    """
    ͨ��MFnSkinCluster�����ȡ����Ƥ���������
    :param skin_cluster_fn:
    :return:
    """
    if type(skin_cluster_fn) == omain.MFnSkinCluster:
        pass
    elif mc.nodeType(skin_cluster_fn) == 'skinCluster':
        mobject = getApiNode(skin_cluster_fn, dag=False)
        skin_cluster_fn = omain.MFnSkinCluster(mobject)
    else:
        fb_print('����{}�Ȳ���MFnSkinCluster����Ҳ����skinCluster�ڵ�'.format(skin_cluster_fn))

    influenced_objects = om.MObjectArray()
    skin_cluster_fn.getOutputGeometry(influenced_objects)

    influenced_model_names = []
    for i in range(influenced_objects.length()):
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
    elif mc.nodeType(skin_cluster_fn) == 'skinCluster':
        mobject = getApiNode(skin_cluster_fn, dag=False)
        skin_cluster_fn = omain.MFnSkinCluster(mobject)
    else:
        fb_print('����{}�Ȳ���MFnSkinCluster����Ҳ����skinCluster�ڵ�'.format(skin_cluster_fn))

    influenced_objects = om.MObjectArray()
    skin_cluster_fn.getInputGeometry(influenced_objects)
    for i in range(influenced_objects.length()):
        input_object = influenced_objects[i]
        dg_iterator = om.MItDependencyGraph(input_object, om.MFn.kInvalid, om.MItDependencyGraph.kUpstream,
                                            om.MItDependencyGraph.kDepthFirst, om.MItDependencyGraph.kPlugLevel)

        while not dg_iterator.isDone():
            current_node = dg_iterator.currentItem()
            if current_node.hasFn(om.MFn.kNurbsSurface):
                return 'nurbsSurface'
            elif current_node.hasFn(om.MFn.kNurbsCurve):
                return 'nurbsCurve'
            elif current_node.hasFn(om.MFn.kMesh):
                return 'mesh'

            dg_iterator.next()


def fromObjGetRigNode(obj, skin=True, blend_shape=False, path_name=True):
    """
    ���ַ�����transform�����ȡ��ģ�͵İ�������ͽڵ�
    :param blend_shape: ��ȡbs�ڵ�
    :param skin: ��Ƥ�ڵ�
    :param obj: transform�����ַ���
    :param path_name: ����ʱ�Ƿ񷵻�api�����б�Ϊ�棨Ĭ�ϣ�ʱ���ؽڵ������б�
    :return:����ؽڵ��б�
    """
    dagNode = getApiNode(obj)
    try:
        dagNode.extendToShape()
    except RuntimeError:
        fb_print('����{}û��shape�ڵ��ֹһ��shape�ڵ㡣'.format(dagNode.partialPathName()), error=True)
    m_object = dagNode.node()

    if skin:
        itDG = om.MItDependencyGraph(m_object, om.MFn.kSkinClusterFilter, om.MItDependencyGraph.kUpstream)
    elif blend_shape:
        itDG = om.MItDependencyGraph(m_object, om.MFn.kBlendShape, om.MItDependencyGraph.kUpstream)
    else:
        fb_print('û��ָ��Ҫ��ȡ�Ľڵ����', error=True)

    ret_lis = []
    while not itDG.isDone():
        item = itDG.currentItem()
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
    influencePaths = om.MDagPathArray()
    fn_skin.influenceObjects(influencePaths)
    return [influencePaths[i].partialPathName() for i in range(influencePaths.length()) if
            om.MFnDagNode(influencePaths[i]).typeName() == 'joint']
