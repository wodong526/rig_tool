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
    ��ѯ���������е�����
    """
    error_lis = []
    repeat_lis = []
    sel_lis = mc.ls()
    for obj in sel_lis:
        if '|' in obj:
            repeat_lis.append(obj.split('|')[-1])
        else:
            repeat_lis.append(obj)

    for i, obj in enumerate(repeat_lis):
        if repeat_lis.count(obj) > 1:
            if sel_lis[i] not in error_lis:
                error_lis.append(sel_lis[i])

    if error_lis:
        log.info("������������{}����{}��".format(error_lis.__len__()/2, ', '.join(error_lis)))
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
    if mc.ls(sl=True):
        for inf in mc.ls(sl=True):
            if mc.listRelatives(inf, s=True):
                if mc.nodeType(mc.listRelatives(inf, s=True)[0]) == 'mesh':
                    mc.select(inf)
                    mel.eval('ConvertSelectionToEdgePerimeter;')
                    for edge in mc.ls(sl=True):
                        error_lis.append(edge)
                else:
                    log.warning("{}���Ƕ����ģ�ͣ���������".format(inf))
                    continue
            else:
                log.warning("{}���Ƕ����ģ�ͣ���������".format(inf))
                continue
    else:
        log.error('û��ѡ�ж���')
        return False
    mc.select(error_lis)
    if error_lis:
        log.info("�߽����{}".format(error_lis))
    else:
        log.info("ѡ�ж���û�б߽�ߡ�")


def clear_frozen():
    """
    ��ѯ�����е�ģ�ͺ����Ƿ���δ��������ԡ�
    """
    erro_lis = []
    for trans_obj in mc.ls(typ='transform'):
        if trans_obj in ['persp', 'top', 'front', 'side']:
            continue

        for attr in ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]:
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
    his_dir = {}
    for shp in shp_lis:
        his = mc.listHistory(shp, ha=1, pdo=1)
        if his:
            for h in his:
                if mc.nodeType(h) == 'groupId' or mc.nodeType(h) == 'shadingEngine':
                    continue
                else:
                    if shp in his_dir:
                        his_dir[shp].append(h)
                    else:
                        his_dir[shp] = [h]

    if his_dir:
        for inf in his_dir:
            if his_dir[inf]:
                log.warning("{}����ʷ{}".format(inf, his_dir[inf]))
    else:
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
