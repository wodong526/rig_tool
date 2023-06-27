# coding=gbk
import maya.cmds as mc
import maya.mel as mm

from feedback_tool import Feedback_info as fb_print, LIN as lin

FILE_PATH = __file__


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
                fb_print('已删除空间名{}。'.format(ns), info=True)
            except:
                fb_print('余空间名{}，删除失败。'.format(ns), error=True)
        clear_nameSpace()
    else:
        fb_print('已清理场景内所有空间名。', info=True)

def clear_key():
    '''
    删除场景内所有关键帧
    '''
    sel_lis = mc.ls(sl=True)
    mc.select('persp')
    mm.eval('doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","1","animationList","0","noOptions","0","0" };')
    fb_print('已删除场景中所有关键帧。', info=True)
    mc.select(sel_lis)

def clear_hik():
    '''
    删除场景里所有hik
    '''
    hik_lis = mc.ls(typ='HIKCharacterNode')
    if hik_lis:
        for hik in hik_lis:
            del_lis = mc.listConnections(hik, d=False)
            mc.delete(del_lis)
            fb_print('已删除HIK{}。'.format(hik), info=True)
    else:
        fb_print('场景里没有HIK。', info=True)

def clear_animLayer():
    '''
    删除场景内所有动画层
    '''
    for ani in mc.ls(type='animLayer'):
        try:
            mc.delete(ani)
            fb_print('已删除动画层{}。'.format(ani), info=True)
        except:
            fb_print('动画层{}删除失败，可能是因为它是其它层的子级，所以在删除父层时自动删除了子级层。'.format(ani), warning=True)

def inspect_weight():
    error_lis = []
    for skin in mc.ls(typ='skinCluster'):
        shape = mc.skinCluster(skin, query=True, g=True)[0]

        verts = mc.ls(shape + '.vtx[*]', fl=True)

        for v in verts:
            wgt_lis = mc.skinPercent(skin, v, query=True, v=True)
            if len(wgt_lis) > 1:
                weight = sum(wgt_lis)
            else:
                weight = wgt_lis[0]
            if abs(weight - 1) >= 0.001:
                error_lis.append((v, weight))

    if error_lis:
        fb_print('模型{}有点权重合不为1的点：{}'.format(shape, ['\n'+vtx[0]+vtx[1] for vtx in error_lis]), error=True)
    else:
        fb_print('场景中所有模型的点权重都近似为1', info=True)


