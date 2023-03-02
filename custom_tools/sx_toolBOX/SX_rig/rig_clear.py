# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
import copy
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def clear_name():
    """
    查询场景中所有的重名
    """
    obj_lis = mc.ls()
    dup_lis = copy.deepcopy(obj_lis)
    chongfu_lis = []
    for n in range(len(dup_lis)):
        if "|" in dup_lis[n]:
            dup_lis[n] = dup_lis[n].split("|")[-1]
            continue
    for inf in range(len(obj_lis)):
        dup_lis.remove(dup_lis[0])
        slp_obj = ""
        if "|" in obj_lis[inf]:
            slp_obj = obj_lis[inf].split("|")[-1]
        if slp_obj in dup_lis:
            chongfu_lis.append(obj_lis[inf])
            continue
    if chongfu_lis:
        log.info("重命名对象有：{}。".format(chongfu_lis))
        return True
    log.info("场景中没有重名物体对象。")
    return False


def clear_face():
    """
    查询选中对象上所有非四边面。
    """
    triangle_lis = []
    Multiple_lis = []
    for inf in mc.ls(sl=True):
        if mc.nodeType(mc.listRelatives(inf, s=True)[0]) == 'mesh':
            mc.select(inf, r=True)
            mc.SelectFacetMask()
            mc.SelectAll()
            for face_i in mc.ls(sl=True, fl=True):
                mc.select(face_i, r=True)
                mel.eval("PolySelectConvert 3;")
                if len(mc.ls(sl=True, fl=True)) <= 3:
                    triangle_lis.append(face_i)
                    continue
                if len(mc.ls(sl=True, fl=True)) > 4:
                    Multiple_lis.append(face_i)
                    continue
            mel.eval("maintainActiveChangeSelectMode {} 1;".format(inf))
            continue
        else:
            log.warning("{}不是多边形模型。".format(inf))
    mc.select(triangle_lis, r=True)
    if triangle_lis:
        log.warning("大于四边面的有{}".format(Multiple_lis))
        log.warning("小于四边面的有{}".format(triangle_lis))
    else:
        log.info('选中对象全是四边面。')


def clear_boundary():
    """
    查询选中对象的边界边。
    """
    error_lis = []
    if mc.ls(sl=True):
        for inf in mc.ls(sl=True):
            if mc.listRelatives(inf, s=True):
                if mc.nodeType(mc.listRelatives(inf, s=True)[0]) == 'mesh':
                    mc.select(inf)
                    mel.eval('ConvertSelectionToEdgePerimeter;')
                    for edge in mc.ls(sl=True):
                        error_lis.append(edge)
                else:
                    log.warning("{}不是多边形模型，已跳过。".format(inf))
                    continue
            else:
                log.warning("{}不是多边形模型，已跳过。".format(inf))
                continue
    else:
        log.error('没有选中对象。')
        return False
    mc.select(error_lis)
    if error_lis:
        log.info("边界边有{}".format(error_lis))
    else:
        log.info("选中对象没有边界边。")


def clear_frozen():
    """
    查询场景中的模型和组是否有未冻结的属性。
    """
    obj = mc.ls(sl=True)
    trans_lis = []
    for inf in obj:
        if mc.listRelatives(inf, s=1):
            if mc.nodeType(mc.listRelatives(inf, s=1)[0]) == "mesh":
                trans_lis.append(inf)
            elif len(mc.listRelatives(inf, ad=True)) > 1:
                trans_lis.append(inf)
    erro_lis = []
    for trans_obj in trans_lis:
        for attr in [
            "translateX",
            "translateY",
            "translateZ",
            "rotateX",
            "rotateY",
            "rotateZ",
        ]:
            if mc.getAttr("{}.{}".format(trans_obj, attr)):
                erro_lis.append([trans_obj, attr])
                continue
        for attr in ["scaleX", "scaleY", "scaleZ"]:
            if mc.getAttr("{}.{}".format(trans_obj, attr)) != 1:
                erro_lis.append([trans_obj, attr])
                continue
    if erro_lis:
        for i in range(len(erro_lis)):
            log.warning(
                "{}有未冻结的属性{}。".format(erro_lis[i][0], erro_lis[i][1]))
    else:
        log.info(
            "场景中的组和模型都已冻结。"
        )


def clear_history():
    """
    查询场景中所有模型是否有历史。
    """
    shp_lis = mc.ls(typ="mesh")
    his_lis = {}
    n = 0
    for shp in shp_lis:
        trs = mc.listRelatives(shp, p=1)[0]
        his = mc.listHistory(trs, ha=1, pdo=1)
        his_lis[trs] = his
        if his:
            n = 1
            continue
    if n:
        for inf in his_lis:
            if his_lis[inf]:
                log.warning("{}有历史{}".format(inf, his_lis[inf]))
                continue
    else:
        log.info('场景中所有模型都没有历史。')


def clear_minimum():
    """
    查询选中对象的最低点是否在地面。
    """
    obj = mc.ls(sl=1)
    if obj:
        point_n = mc.polyEvaluate(obj[0], v=1)
        pos_lis = []
        for v in range(point_n):
            pos_y = mc.xform("{}.vtx[{}]".format(obj[0], v), q=1, ws=1, t=1)[1]
            pos_lis.append(pos_y)
    else:
        log.warning("没有选中任何对象。")
        return False
    if min(pos_lis) < -0.001 or min(pos_lis) >0.001:
        log.warning("{}的最低点为{}".format(obj[0], min(pos_lis)))
    else:
        log.info("{}的最低点在地平面上。".format(obj[0]))

def clear_uv(i):
    '''
   通过判断引用进来的模型文件里每个物体的uvbbox对比，查找有差异的rig文件
   '''
    mc.CreateReference()
    ref_file = mc.file(q=True, reference=True)[0]
    ref_name = ref_file.split("/")[-1].split(".")[0]
    uv_bol = 0
    for mesh in mc.ls(typ="mesh"):
        trs = mc.listRelatives(mesh, p=1)[0]
        if ref_name in trs or mc.polyEvaluate(trs, b2=1) != mc.polyEvaluate(trs.split(":")[-1], b2=1):
            log.warning("模型{}的uv位置不匹配。".format(trs.split(":")[-1]))
            uv_bol = 1
    if uv_bol == 0 and i == 0:
        mc.file(ref_file, rr=1)
        log.info("引用模型与场景模型位置匹配，建议再手动检查。")
        return False
    if uv_bol == 1 and i == 1:
        mc.file(ref_file, rr=1)
        return False

def clear_key():
    '''
    删除场景内所有关键帧
    '''
    sel_lis = mc.ls(sl=True)
    mc.select('persp')
    mel.eval('doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","1","animationList","0","noOptions","0","0" };')
    log.info('已删除场景中所有关键帧。')
    mc.select(sel_lis)

def clear_animLayer():
    '''
    删除场景内所有动画层
    '''
    for ani in mc.ls(type='animLayer'):
        try:
            mc.delete(ani)
            log.info('已删除动画层{}。'.format(ani))
        except:
            log.warning('动画层{}删除失败，可能是因为它是其它层的子级，所以在删除父层时自动删除了子级层。'.format(ani))

def clear_hik():
    '''
    删除场景里所有hik
    '''
    hik_lis = mc.ls(typ='HIKCharacterNode')
    if hik_lis:
        for hik in hik_lis:
            del_lis = mc.listConnections(hik, d=False)
            mc.delete(del_lis)
            log.info('已删除HIK{}。'.format(hik))
    else:
        log.info('场景里没有HIK。')

def clear_nameSpace():
    '''
    删除场景内所有空间名
    '''
    nsLs = mc.namespaceInfo(lon=True)
    defaultNs = ["UI", "shared", "mod"]
    pool = [item for item in nsLs if item not in defaultNs]
    if pool:
        for ns in pool:
            try:
                mc.namespace(rm=ns, mnr=1, f=1)
                log.info('已删除空间名{}。'.format(ns))
            except:
                om.MGlobal.displayError('余空间名{}，删除失败。'.format(ns))
                return None
        clear_nameSpace()
    else:
        log.info('已清理场景内所有空间名。')