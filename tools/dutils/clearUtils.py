# coding=gbk
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om
import maya.OpenMayaAnim as omain

from dutils import apiUtils
from feedback_tool import Feedback_info as fp


def clear_nameSpace(q=False):
    """
    删除场景内所有空间名
    """
    nsLs = mc.namespaceInfo(lon=True)
    defaultNs = ["UI", "shared", "mod"]
    pool = [item for item in nsLs if item not in defaultNs]
    if pool and q:
        return True, pool
    elif not pool and q:
        return False, []
    elif pool and not q:
        for ns in pool:
            try:
                mc.namespace(rm=ns, mnr=1, f=1)
                fp('已删除空间名{}。'.format(ns), info=True)
            except:
                fp('余空间名{}，删除失败。'.format(ns), error=True)
        clear_nameSpace()
    else:
        fp('已清理场景内所有空间名。', info=True)
        return False


def clear_key():
    '''
    删除场景内所有关键帧
    '''
    sel_lis = mc.ls(sl=True)
    mc.select('persp')
    mm.eval('doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","1","animationList","0","noOptions","0","0" };')
    fp('已删除场景中所有关键帧。', info=True)
    mc.select(sel_lis)
    return False


def clear_hik():
    '''
    删除场景里所有hik
    '''
    hik_lis = mc.ls(typ='HIKCharacterNode')
    if hik_lis:
        for hik in hik_lis:
            del_lis = mc.listConnections(hik, d=False)
            mc.delete(del_lis)
            fp('已删除HIK{}。'.format(hik), info=True)
    else:
        fp('场景里没有HIK。', info=True)
    return False


def clear_animLayer():
    '''
    删除场景内所有动画层
    '''
    for ani in mc.ls(type='animLayer'):
        try:
            mc.delete(ani)
            fp('已删除动画层{}。'.format(ani), info=True)
        except:
            fp('动画层{}删除失败，可能是因为它是其它层的子级，所以在删除父层时自动删除了子级层。'.format(ani), warning=True)
    fp('已删除所有动画层', info=True)
    return False


def clear_name():
    """
    查询场景中所有的重名
    """
    error_lis = []
    sel_lis = mc.ls()
    for obj in sel_lis:
        if '|' in obj:
            error_lis.append(obj)

    if error_lis:
        fp("重命名对象有{}个：{}".format(error_lis.__len__() / 2, ', '.join(error_lis)), info=True)
        return True
    fp("场景中没有重名物体对象", info=True)
    return False


def inspect_weight():
    """
    检测蒙皮模型各个点的权重和是否为1，当有不近似为1时报错
    :return:
    """
    error_dir = {}

    for skin in mc.ls(typ='skinCluster'):
        mobject = apiUtils.getApiNode(skin, dag=False)
        fn = omain.MFnSkinCluster(mobject)
        if apiUtils.get_skinModelType(fn) == 'mesh':  #检测蒙皮节点被蒙皮对象是否为模型
            dagPath, components = apiUtils.getGeometryComponents(fn)  #获取蒙皮节点蒙皮的组件信息
            weights = apiUtils.getCurrentWeights(fn, dagPath, components)  #获取权重列表（点1.关节1、点1.关节2、点2.关节1、点2关节2···）
            influencePaths = om.MDagPathArray()
            fn.influenceObjects(influencePaths)  #蒙皮关节对象datPath数组

            for i in range(0, len(weights), influencePaths.length()):  #遍历数组总长度，步长为蒙皮关节数，则每个i都是每个点的第一个蒙皮关节下标
                weight = 0.0
                for n in range(influencePaths.length()):
                    weight += weights[i + n]

                if round(weight, 5) != 1.0:  #取小数点后五位精度
                    skin_mod = apiUtils.get_skinModelName(fn)[0]
                    if skin_mod in error_dir.keys():
                        error_dir[skin_mod].append(str(i / 2))
                    else:
                        error_dir[skin_mod] = [str(i / 2)]
        else:
            fp('蒙皮节点{}的被蒙皮对象是{}类型的{}，已跳过'.format(fn.name(), apiUtils.get_skinModelType(fn),
                                                                        ','.join(apiUtils.get_skinModelName(fn))),
                     warning=True)
    else:
        if error_dir:
            fp('点总权重不为1的点有：{}'.format(''.join(
                ['\n{}.vtx[{}]'.format(mod, ','.join(vtx_lis)) for mod, vtx_lis in error_dir.items()])),
                info=True, viewMes=True)
            return True
        else:
            fp('场景中所有模型的点权重都近似为1', info=True, viewMes=True)
            return False

def clear_unknown_node():
    """
    清理未知节点
    :return:清理后场景中的未知节点
    """
    nuk_lis = mc.ls(typ='unknown')
    if nuk_lis:
        for node in nuk_lis:
            if mc.objExists(node):
                mc.lockNode(node, l=False)
                mc.delete(node)
                fp('已清理未知节点{}'.format(node), info=True)

    return mc.ls(typ='unknown')

def clear_unknown_plug():
    """
    清理未知插件
    :return: 清理后场景中的未知插件
    """
    [mc.unknownPlugin(p, r=True) for p in mc.unknownPlugin(q=True, l=True)] if mc.unknownPlugin(q=True, l=True) else None


    return mc.unknownPlugin(q=True, l=True)
