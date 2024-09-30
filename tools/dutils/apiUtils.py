# coding=gbk
import re

import maya.cmds as mc
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as omain

from feedback_tool import Feedback_info as fp


def getApiNode(obj=None, dag=True, com=False):
    """
    获取对象的MDagPath
    :param com: 如果需要获取的是组件，则返回组件的dagPath
    :param dag: 是否只返回dag节点
    :param obj:(str) 要获取的对象
    :return:
    """
    if obj:
        sel = om.MGlobal.getSelectionListByName(obj)
    else:
        sel = om.MGlobal.getActiveSelectionList()

    if sel.isEmpty():
        fp('没有指定任何对象。', error=True)
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
    重命名对象
    :param objs: 要重命名的对象,当有重名时，传入长名
    :param prefix: 前缀
    :param suffix: 后缀
    :param replace: 替换列表
    :param lower: 小写
    :param upper: 大写
    :param select: 是否只操作选中对象
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
    创建节点
    :param node_type: 节点类型
    :param name: 节点名,如果不指定则以node_type命名
    :param dg: 创建的节点是dg节点时需要设置为true
    :return: 节点的object对象
    """
    if dg:
        mod = om.MDGModifier()
    else:
        mod = om.MDagModifier()
    obj = mod.createNode(node_type)
    mod.renameNode(obj, name if name else '{}*'.format(node_type))
    mod.doIt()

    return obj

def connect_plug(sor_node, sor_attr, end_node, end_attr, force=False):
    # type: (str, str, str, str, bool) -> bool
    """
    连接两个plug
    :param end_node: 上游节点名
    :param sor_node: 下游节点名
    :param sor_attr:上游属性名
    :param end_attr:下游属性名
    :param force: 是否强制连接
    :return:
    """
    mod = om.MDGModifier()
    sor_result = re.match(r'(\w+)\[(\d+)]', sor_attr)
    end_result = re.match(r'(\w+)\[(\d+)]', end_attr)
    if sor_result:
        sor_attr, sor_index = sor_result.group(1), int(sor_result.group(2))
        sor = get_attr(sor_node, sor_attr).elementByLogicalIndex(sor_index)
    else:
        sor = get_attr(sor_node, sor_attr)
    if end_result:
        end_attr, end_index = end_result.group(1), int(end_result.group(2))
        end = get_attr(end_node, end_attr).elementByLogicalIndex(end_index)
    else:
        end = get_attr(end_node, end_attr)

    if force and not end.isNull:
        conn_plug = end.source()
        if not conn_plug.isNull:
            mod.disconnect(sor, end)
    mod.connect(sor, end)
    mod.doIt()
    return True

def get_attr(node, attr):
    # type: (str, str) -> om.MPlug
    """
    获取节点属性的plug对象
    :param node: 节点名
    :param attr: 属性名
    :return: 属性的plug对象
    """
    return om.MFnDependencyNode(getApiNode(node, dag=False)).findPlug(attr.split('.')[-1], False)

def get_sub_plug(node, attr):
    # type: (str, str) -> list[str]
    """
    获取子属性
    :param node: 节点名
    :param attr: 属性名
    :return: 包含子属性名的list
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
    设置对象的属性
    :param node: 节点名
    :param attr: 属性名
    :param value: 属性值
    :return:
    """
    result = re.match(r'(\w+)\[(\d+)]', attr)
    if result:
        attr, index = result.group(1), int(result.group(2))

    if get_attr(node, attr).isCompound and (isinstance(value, list) or isinstance(value, tuple)):
        for attr, val in zip(get_sub_plug(getApiNode(node, dag=False), attr), value):
            set_attr(node, attr, val)
        return

    if isinstance(value, str):
        get_attr(node, attr).setString(value)
    elif isinstance(value, int):
        get_attr(node, attr).setInt(value)
    elif isinstance(value, bool):
        get_attr(node, attr).setBool(value)
    elif isinstance(value, float):
        if get_plug_type(node, attr) == 'kDoubleAngleAttribute':
            get_attr(node, attr).setMAngle(om.MAngle(value, om.MAngle.kDegrees))
        else:
            get_attr(node, attr).setFloat(value)
    elif isinstance(value, list) or isinstance(value, tuple):
        api_type = get_plug_type(node, attr)
        if api_type == 'kMatrixAttribute':
            matrix_data = om.MFnMatrixData()
            matrix_data.create(om.MMatrix(value))
            if 'index' in locals() or 'index' in globals():
                get_attr(node, attr).elementByLogicalIndex(index).setMObject(matrix_data.object())
            else:
                get_attr(node, attr).setMObject(matrix_data.object())
    else:
        om.MGlobal.displayError('{}为不支持的数据类型：{}'.format(value, type(value)))

def get_plug_type(node, attr):
    # type: (str, str) -> str
    """
    获取plug的类型
    :param node: 节点名
    :param attr: 属性名
    :return:
    """
    return om.MFnDependencyNode(getApiNode(node, dag=False)).attribute(attr).apiTypeStr

def getMPoint(obj):
    # type: (str) -> om.MPoint
    """
    获取给定对象的世界xyz坐标
    :param obj: 要获取坐标的对象
    :return: MPoint类型
    """
    pos = mc.xform(obj, q=True, t=True, ws=True)

    return om.MPoint(pos[0], pos[1], pos[2], 1.0)

def get_plug_value(node, attr):
    # type: (str, str) -> list
    """
    获取plug具体的值
    :param node: 节点名
    :param attr: 属性名
    :return:
    """
    plug_obj = get_attr(node, attr)
    node_obj = getApiNode(node, dag=False)
    fn_dep = om.MFnDependencyNode(node_obj)
    attr_obj = fn_dep.attribute(attr)

    ret_lis = []
    if plug_obj.isCompound:
        fn_attr = om.MFnCompoundAttribute(attr_obj)
        for i in range(fn_attr.numChildren()):
            child_obj = fn_attr.child(i)
            ret_lis.append(get_plug_value(node, om.MPlug(node_obj, child_obj).name().split('.')[-1])[0])
    else:
        api_type = get_plug_type(node, attr)
        if api_type == 'kDoubleLinearAttribute':  #float
            ret_lis.append(plug_obj.asDouble())
        elif api_type == 'kEnumAttribute':        #enum
            ret_lis.append(plug_obj.asInt())
        elif api_type == 'kDoubleAngleAttribute':
            ret_lis.append(plug_obj.asMAngle().asDegrees())
        elif api_type == 'kMatrixAttribute':
            mMatrix = plug_obj.asMDataHandle().asMatrix()
            ret_lis.extend([mMatrix.getElement(row, col) for row in range(4) for col in range(4)])
        elif api_type == 'kTypedAttribute':
            attr_fn = om.MFnTypedAttribute(attr_obj)
            if attr_fn.attrType() == om.MFnData.kString:
                ret_lis.append(plug_obj.asString())
            elif attr_fn.attrType() == om.MFnData.kMatrix:
                mMatrix = om.MFnMatrixData(plug_obj.asMObject()).matrix()
                ret_lis.extend([mMatrix.getElement(row, col) for row in range(4) for col in range(4)])
            else:
                om.MGlobal.displayError('未知属性类型：{}'.format(attr_fn.attrType()))
        elif api_type == 'kNumericAttribute':
            fn_num_type = om.MFnNumericAttribute(fn_dep.attribute(attr)).numericType()
            if fn_num_type == 7:    #int
                ret_lis.append(plug_obj.asInt())
            elif fn_num_type == 1:  #bool
                ret_lis.append(plug_obj.asBool())
            elif fn_num_type in [14, 11]:
                ret_lis.append(plug_obj.asDouble())
            else:
                om.MGlobal.displayError('不支持的数字属性类型：{}'.format(fn_num_type))
        else:
            om.MGlobal.displayError('不支持的属性类型：{}'.format(api_type))

    return ret_lis

def getGeometryComponents(fn_skin):
    # type: (omain.MFnSkinCluster) -> tuple[om.MDagPath, om.MObject]
    """
    从MFnSkinCluster类型对象获取该节点的dagPath对象和蒙皮组件对象
    :param fn_skin:MFnSkinCluster节点
    :return:蒙皮节点的dagPath对象、蒙皮节点的组件节点
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
    通过MFnSkinCluster对象获取该蒙皮节点的权重列表
    :param influences_nam: 当指定关节名称时返回该关节的权重
    :param fn_skin: MFnSkinCluster节点
    :param dag_path: 蒙皮对象的dagPath对象
    :param components: 蒙皮对象的组件对象
    :return:权重数组，排列依据为：第一个点的按关节顺序的权重值、第二个点的····
    """
    if not influences_nam:
        return fn_skin.getWeights(dag_path, components)[0]

    try:
        return fn_skin.getWeights(dag_path, components, fromSkinGetInfluence(fn_skin).index(influences_nam))
    except ValueError:
        fp('蒙皮关节{}不存在'.format(influences_nam), warning=True)
        return None

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
    influenceIndices = om.MIntArray()
    for ii in range(influences_num):
        influenceIndices.insert(ii, ii)
    fn.setWeights(dag_path, components, influenceIndices, weights)

def get_skinModelName(skin_cluster_fn):
    """
    通过MFnSkinCluster对象获取被蒙皮对象的名字
    :param skin_cluster_fn:
    :return:
    """
    if type(skin_cluster_fn) == omain.MFnSkinCluster:
        pass
    else:
        fp('参数{}不是MFnSkinCluster对象'.format(skin_cluster_fn))

    influenced_objects = skin_cluster_fn.getOutputGeometry()
    influenced_model_names = []
    for i in range(influenced_objects.__len__()):
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
    else:
        fp('参数{}不是MFnSkinCluster对象'.format(skin_cluster_fn))

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
    从字符串的transform对象获取该模型的绑定相关类型节点
    :param blend_shape: 获取bs节点
    :param skin: 蒙皮节点
    :param obj: transform对象字符串
    :param path_name: 返回时是否返回api对象列表，为真（默认）时返回节点名字列表
    :return:绑定相关节点列表
    """
    if not isinstance(obj, om.MDagPath):
        dagNode = getApiNode(obj)
    else:
        dagNode = obj

    try:
        dagNode.extendToShape()
    except RuntimeError:
        fp('对象{}没有shape节点或不止一个shape节点。'.format(dagNode.partialPathName()), error=True)
    m_object = dagNode.node()

    if skin:
        itDG = om.MItDependencyGraph(m_object, om.MFn.kSkinClusterFilter, om.MItDependencyGraph.kUpstream)
    elif blend_shape:
        itDG = om.MItDependencyGraph(m_object, om.MFn.kBlendShape, om.MItDependencyGraph.kUpstream)
    else:
        fp('没有指定要获取的节点对象。', error=True)

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
    从MFnSkinCluster对象获影响关节
    :param fn_skin:MFnSkinCluster对象
    :return:影响关节列表
    """
    influence_lis = []
    dagArr = fn_skin.influenceObjects()
    for i in range(dagArr.__len__()):
        if om.MFnDagNode(dagArr[i]).typeName == 'joint':
            influence_lis.append(dagArr[i].partialPathName())

    return influence_lis
