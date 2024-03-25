# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mel
import maya.api.OpenMaya as oma

import os
from collections import Counter
import re

from feedback_tool import Feedback_info as fp
from dutils import fileUtils as fu

class ProtectiveTools(object):
    """
    �����ļ�������
    """
    @classmethod
    def clear_pyFile(cls):
        """
        �����������ű��ļ�
        :return:
        """
        py_path_lis = ['scripts/vaccine', 'scripts/fuckVirus']
        userSetUp_path = mc.internalVar(uad=True) + 'scripts/userSetUp.py'
        for path in py_path_lis:
            map(fu.delete_files, [mc.internalVar(uad=True) + path + typ for typ in ['.py', '.pyc']])

        if os.path.exists(userSetUp_path):
            tag_txt_lis = ['leukocyte.occupation()', 'leukocyte = vaccine.phage()']
            is_vaccine = False
            with open(userSetUp_path, 'r') as file_obj:
                for line in file_obj.readlines():
                    for tag in tag_txt_lis:
                        if tag in line:
                            is_vaccine = True
                            break
                    if is_vaccine:
                        break
            if is_vaccine:
                map(fu.delete_files, [userSetUp_path])

    @classmethod
    def get_dubious_scriptNodes(cls):
        del_script_lis = []
        rfenc_script_lis = []
        script_nodes = mc.ls(type='script')
        for script_node in script_nodes:
            script_before_string = mc.getAttr('{}.before'.format(script_node))
            script_after_string = mc.getAttr('{}.after'.format(script_node))
            for script_string in [script_before_string, script_after_string]:
                if not script_string:
                    continue
                if 'internalVar' in script_string or 'userSetup' in script_string:
                    if mc.referenceQuery(script_node, inr=True):
                        rfenc_script_lis.append(script_node)
                    else:
                        del_script_lis.append(script_node)

        return del_script_lis, rfenc_script_lis

    @classmethod
    def get_dubious_scriptJob(cls):
        dangerous_jobs = ['leukocyte.antivirus()']

        del_scriptJob_lis = []
        script_jobs = mc.scriptJob(lj=True)
        for script_job in script_jobs:
            for bad_job in dangerous_jobs:
                if bad_job in script_job:
                    del_scriptJob_lis.append(script_job)
        return del_scriptJob_lis

    def __init__(self):
        self.clear_pyFile()
        self.create_callback()

    def del_scriptNode(self, *args):
        self.clear_pyFile()

        del_lis, rfenc_lis = self.get_dubious_scriptNodes()
        if del_lis:
            for del_script_node in del_lis:
                mc.lockNode(del_script_node, l=False)
                mc.delete(del_script_node)
                print('��ɾ��scriptNode��{}'.format(del_script_node))

        if rfenc_lis:
            dubious_lis = []
            for node in dict(Counter(rfenc_lis)):
                dubious_lis.append(node)
            mes = '���¿���script�ڵ��޷���ɾ������Ϊ�������������ļ���\n    {}'.format('\n    '.join(dubious_lis))
            mc.confirmDialog(title='����', message=mes, button=['ȷ��'])

    def del_scriptJob(self, *args):
        self.clear_pyFile()

        JOB_INDEX_REGEX = re.compile(r'^(\d+):')
        del_lis = self.get_dubious_scriptJob()
        if del_lis:
            for script_job in del_lis:
                bad_script_job_index = int(JOB_INDEX_REGEX.findall(script_job)[0])
                mc.scriptJob(kill=bad_script_job_index, force=True)
                print('��ɾ��scriptJob��{}'.format(script_job))

    def create_callback(self):
        oma.MSceneMessage.addCallback(oma.MSceneMessage.kAfterOpen, self.del_scriptNode)
        oma.MSceneMessage.addCallback(oma.MSceneMessage.kBeforeSave, self.del_scriptJob)
        print('����Ч���ѽ�����')



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
        fp("������������{}����{}��".format(error_lis.__len__()/2, ', '.join(error_lis)), info=True)
        return True
    fp("������û�������������", info=True)
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
            fp("{}���Ƕ����ģ�͡�".format(inf), warning=True)
    mc.select(triangle_lis, r=True)
    if triangle_lis:
        fp("�����ı������{}".format(Multiple_lis), warning=True)
        fp("С���ı������{}".format(triangle_lis), warning=True)
    else:
        fp('ѡ�ж���ȫ���ı��档', warning=True)


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
                    fp("{}���Ƕ����ģ�ͣ���������".format(inf), warning=True)
                    continue
            else:
                fp("{}���Ƕ����ģ�ͣ���������".format(inf), warning=True)
                continue
    else:
        fp('û��ѡ�ж���', error=True)
        return False
    mc.select(error_lis)
    if error_lis:
        fp("�߽����{}".format(error_lis), warning=True)
    else:
        fp("ѡ�ж���û�б߽�ߡ�", info=True)


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
            fp("{}��δ���������{}��".format(erro_lis[i][0], erro_lis[i][1]), warning=True)
    else:
        fp("�����е����ģ�Ͷ��Ѷ��ᡣ", info=True)


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
                fp("{}����ʷ{}".format(inf, his_dir[inf]), warning=True)
    else:
        fp('����������ģ�Ͷ�û����ʷ��', info=True)


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
        fp("û��ѡ���κζ���", warning=True)
        return False
    if min(pos_lis) < -0.001 or min(pos_lis) >0.001:
        fp("{}����͵�Ϊ{}".format(obj[0], min(pos_lis)), warning=True)
    else:
        fp("{}����͵��ڵ�ƽ���ϡ�".format(obj[0]), info=True)

def clear_uv(i):
    """
    ͨ���ж����ý�����ģ���ļ���ÿ�������uvbbox�Աȣ������в����rig�ļ�
    """
    mc.CreateReference()
    ref_file = mc.file(q=True, reference=True)[0]
    ref_name = ref_file.split("/")[-1].split(".")[0]
    uv_bol = 0
    for mesh in mc.ls(typ="mesh"):
        trs = mc.listRelatives(mesh, p=1)[0]
        if ref_name in trs or mc.polyEvaluate(trs, b2=1) != mc.polyEvaluate(trs.split(":")[-1], b2=1):
            fp("ģ��{}��uvλ�ò�ƥ�䡣".format(trs.split(":")[-1]), warning=True)
            uv_bol = 1
    if uv_bol == 0 and i == 0:
        mc.file(ref_file, rr=1)
        fp("����ģ���볡��ģ��λ��ƥ�䣬�������ֶ���顣", info=True)
        return False
    if uv_bol == 1 and i == 1:
        mc.file(ref_file, rr=1)
        return False