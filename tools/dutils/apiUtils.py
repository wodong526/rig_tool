# coding=gbk
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as omain

from feedback_tool import Feedback_info as fb_print, LIN as lin


def getApiNode(obj, dag=True):
    """
    获取对象的MDagPath
    :param dag: 是否只返回dag节点
    :param obj:(str) 要获取的对象
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
    获取给定对象的世界xyz坐标
    :param obj: 要获取坐标的对象
    :return: MPoint类型
    """
    pos = mc.xform(obj, q=True, t=True, ws=True)

    return om.MPoint(pos[0], pos[1], pos[2], 1.0)


def getGeometryComponents(fn_skin):
    """
    从MFnSkinCluster类型对象获取该节点的dagPath对象和蒙皮组件对象
    :param fn_skin:MFnSkinCluster节点
    :return:蒙皮节点的dagPath对象、蒙皮节点的组件节点
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
    通过MFnSkinCluster对象获取该蒙皮节点的权重列表
    :param fn_skin: MFnSkinCluster节点
    :param dag_path: 蒙皮节点的dagPath对象
    :param components: 蒙皮节点的组件节点
    :return:权重数组，排列依据为：第一个点的按关节顺序的权重值、第二个点的····
    """
    weights = om.MDoubleArray()
    util = om.MScriptUtil()
    util.createFromInt(0)
    pUInt = util.asUintPtr()
    fn_skin.getWeights(dag_path, components, weights, pUInt)
    return weights


def setCurrentWeights(fn, weights, influences_num, dag_path, components):
    """
    将权重列表的值赋予到MFnSkinCluster对象
    :param fn: MFnSkinCluster节点
    :param weights: 权重值列表
    :param influences_num: 影响关节对象
    :param dag_path: 蒙皮节点的dagPath对象
    :param components: 蒙皮节点的组件节点
    :return:
    """
    influenceIndices = om.MIntArray(influences_num)
    for ii in range(influences_num):
        influenceIndices.set(ii, ii)
    fn.setWeights(dag_path, components, influenceIndices, weights, False)


def get_skinModelName(skin_cluster_fn):
    """
    通过MFnSkinCluster对象获取被蒙皮对象的名字
    :param skin_cluster_fn:
    :return:
    """
    if type(skin_cluster_fn) == omain.MFnSkinCluster:
        pass
    elif mc.nodeType(skin_cluster_fn) == 'skinCluster':
        mobject = getApiNode(skin_cluster_fn, dag=False)
        skin_cluster_fn = omain.MFnSkinCluster(mobject)
    else:
        fb_print('参数{}既不是MFnSkinCluster对象也不是skinCluster节点'.format(skin_cluster_fn))

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
    通过MFnSkinCluster对象获取被蒙皮对象的类型
    :param skin_cluster_fn: MFnSkinCluster节点
    :return:被蒙皮对象类型名称
    """
    if type(skin_cluster_fn) == omain.MFnSkinCluster:
        pass
    elif mc.nodeType(skin_cluster_fn) == 'skinCluster':
        mobject = getApiNode(skin_cluster_fn, dag=False)
        skin_cluster_fn = omain.MFnSkinCluster(mobject)
    else:
        fb_print('参数{}既不是MFnSkinCluster对象也不是skinCluster节点'.format(skin_cluster_fn))

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
    从字符串的transform对象获取该模型的绑定相关类型节点
    :param blend_shape: 获取bs节点
    :param skin: 蒙皮节点
    :param obj: transform对象字符串
    :param path_name: 返回时是否返回api对象列表，为真（默认）时返回节点名字列表
    :return:绑定相关节点列表
    """
    dagNode = getApiNode(obj)
    try:
        dagNode.extendToShape()
    except RuntimeError:
        fb_print('对象{}没有shape节点或不止一个shape节点。'.format(dagNode.partialPathName()), error=True)
    m_object = dagNode.node()

    if skin:
        itDG = om.MItDependencyGraph(m_object, om.MFn.kSkinClusterFilter, om.MItDependencyGraph.kUpstream)
    elif blend_shape:
        itDG = om.MItDependencyGraph(m_object, om.MFn.kBlendShape, om.MItDependencyGraph.kUpstream)
    else:
        fb_print('没有指定要获取的节点对象。', error=True)

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
    从MFnSkinCluster对象获影响关节
    :param fn_skin:MFnSkinCluster对象
    :return:影响关节列表
    """
    influencePaths = om.MDagPathArray()
    fn_skin.influenceObjects(influencePaths)
    return [influencePaths[i].partialPathName() for i in range(influencePaths.length()) if
            om.MFnDagNode(influencePaths[i]).typeName() == 'joint']
