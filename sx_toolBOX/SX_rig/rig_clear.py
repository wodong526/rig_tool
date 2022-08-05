# -*- coding:GBK -*- 
import maya.cmds as mc
import maya.mel as mel
import copy
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def clear_name():
    """
    ��ѯ���������е�����
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
        log.info("�����������У�{}��".format(chongfu_lis))
        return True
    log.info("������û�������������")
    return False


def clear_face():
    """
    ��ѯѡ�ж��������з��ı��档
    """
    triangle_lis = []
    Multiple_lis = []
    for inf in mc.ls(sl=True):
        if mc.listRelatives(inf, s=True) == 'mesh':
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
        log.warning("{}���Ƕ����ģ�͡�".format(inf))
    mc.select(triangle_lis, r=True)
    if triangle_lis:
        log.warning("�����ı������{}".format(Multiple_lis))
        log.warning("С���ı������{}".format(triangle_lis))
    else:
        log.info('ѡ�ж���ȫ���ı��档')


def clear_boundary():
    """
    ��ѯѡ�ж���ı߽�ߡ�
    """
    error_lis = []
    for inf in mc.ls(sl=True):
        if mc.listRelatives(inf, s=True):
            mc.select(inf, r=True)
            mc.SelectEdgeMask()
            mc.SelectAll()
            mc.ConvertSelectionToShellBorder()
            if mc.ls(sl=True):
                for e in mc.ls(sl=True):
                    error_lis.append(e)
            mel.eval("maintainActiveChangeSelectMode {} 1;".format(inf))
            continue
        log.warning("{}���Ƕ����ģ�͡�".format(inf))
    mc.select(error_lis)
    if error_lis:
        log.info("�߽����{}".format(error_lis))
    else:
        log.info("ѡ�ж���û�б߽�ߡ�")


def clear_frozen():
    """
    ��ѯ�����е�ģ�ͺ����Ƿ���δ��������ԡ�
    """
    obj = mc.ls(typ="transform")
    trans_lis = []
    for inf in obj:
        if mc.listRelatives(inf, s=1):
            if mc.nodeType(mc.listRelatives(inf, s=1)[0]) == "mesh":
                trans_lis.append(inf)
            elif len(mc.listRelatives(inf, ad=True)) > 1:
                trans_lis.append(inf)
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
                "{}��δ���������{}��".format(erro_lis[i][0], erro_lis[i][1]))
    else:
        log.info(
            "�����е����ģ�Ͷ��Ѷ��ᡣ"
        )


def clear_history():
    """
    ��ѯ����������ģ���Ƿ�����ʷ��
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
                log.warning("{}����ʷ{}".format(inf, his_lis[inf]))
                continue
    log.info('����������ģ�Ͷ�û����ʷ��')


def clear_minimum():
    """
    ��ѯѡ�ж������͵��Ƿ��ڵ��档
    """
    obj = mc.ls(sl=1)
    if obj:
        point_n = mc.polyEvaluate(obj[0], v=1)
        pos_lis = []
        for v in range(point_n):
            pos_y = mc.xform("{}.vtx[{}]".format(obj[0], v), q=1, ws=1, t=1)[1]
            pos_lis.append(pos_y)
    else:
        log.warning("û��ѡ���κζ���")
        return False
    if min(pos_lis) < -0.001 or min(pos_lis) >0.001:
        log.warning("{}����͵�Ϊ{}".format(obj[0], min(pos_lis)))
    else:
        log.info("{}����͵��ڵ�ƽ���ϡ�".format(obj[0]))


def clear_material():
    '''
    ����������ظ�������ĩβ�������֣���ʵ����������ǲ�������������߱���Ͳ�ͬ�������ֶ��Ų�
    '''
    mat_lis = mc.ls(typ="lambert")
    repeat_lis = []
    for mat in mat_lis:
        if mat == "lambert1":
            continue
            continue
        if mat[-1] in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0"):
            repeat_lis.append(mat)
            continue
    if repeat_lis:
        log.warning(
            "������{}�����ظ��������ֶ��Ų顣".format(repeat_lis))
        return True
    log.info("û�м�鵽�����ظ��Ĳ����򣬵����ǽ����ֶ��Ƚϡ�")
    return False


def clear_uv(i):
    '''
   ͨ���ж����ý�����ģ���ļ���ÿ�������uvbbox�Աȣ������в����rig�ļ�
   '''
    mc.CreateReference()
    ref_file = mc.file(q=True, reference=True)[0]
    ref_name = ref_file.split("/")[-1].split(".")[0]
    uv_bol = 0
    for mesh in mc.ls(typ="mesh"):
        trs = mc.listRelatives(mesh, p=1)[0]
        if ref_name in trs or mc.polyEvaluate(trs, b2=1) != mc.polyEvaluate(trs.split(":")[-1], b2=1):
            log.warning("ģ��{}��uvλ�ò�ƥ�䡣".format(trs.split(":")[-1]))
            uv_bol = 1
    if uv_bol == 0 and i == 0:
        mc.file(ref_file, rr=1)
        log.info("����ģ���볡��ģ��λ��ƥ�䣬�������ֶ���顣")
        return False
    if uv_bol == 1 and i == 1:
        mc.file(ref_file, rr=1)
        return False


def clear_key():
    '''
    ɾ�����������йؼ�֡
    '''
    sel = mc.ls(sl = True)
    if len(sel) == 0:
        log.error('ɾ�����йؼ�֡Ҫ������ѡ��һ������ʵ��û��ѡ�����')
        return False
    else:
        mel.eval('doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","1","animationList","0","noOptions","0","0" };')
        log.info('��ɾ�����������йؼ�֡��')