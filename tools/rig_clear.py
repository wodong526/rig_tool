# -*- coding:GBK -*-
import maya.cmds as mc
import maya.mel as mel
import maya.api.OpenMaya as oma

import os
from collections import Counter
import re
import base64
import subprocess

from feedback_tool import Feedback_info as fp
from dutils import fileUtils as fu
import data_path

class ProtectiveTools(object):
    """
    清理文件贼健康
    """
    @classmethod
    def clear_pyFile(cls):
        """
        清理贼健康脚本文件
        :return:
        """
        py_path_lis = ['scripts/vaccine', 'scripts/fuckVirus']
        userSetUp_path = mc.internalVar(uad=True) + 'scripts/userSetUp.py'
        for path in py_path_lis:
            list(map(fu.delete_files, [mc.internalVar(uad=True) + path + typ for typ in ['.py', '.pyc']]))

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
                list(map(fu.delete_files, [userSetUp_path]))

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
        if not script_jobs:
            return None
        for script_job in script_jobs:
            for bad_job in dangerous_jobs:
                if bad_job in script_job:
                    del_scriptJob_lis.append(script_job)
        return del_scriptJob_lis


    @classmethod
    def clear_base64_virus(cls):
        """
        清理240429特征病毒脚本文件
        :return:
        """
        Virus_240429(auto=True)

    def __init__(self):
        self.clear_pyFile()
        self.clear_base64_virus()
        self.create_callback()

    def del_scriptNode(self, *args):
        self.clear_pyFile()
        self.clear_base64_virus()

        del_lis, rfenc_lis = self.get_dubious_scriptNodes()
        if del_lis:
            for del_script_node in del_lis:
                mc.lockNode(del_script_node, l=False)
                mc.delete(del_script_node)
                fp('已删除scriptNode：{}'.format(del_script_node), info=True)

        if rfenc_lis:
            dubious_lis = []
            for node in dict(Counter(rfenc_lis)):
                dubious_lis.append(node)
            mes = '以下可疑script节点无法被删除，因为他们来自引用文件：\n    {}'.format('\n    '.join(dubious_lis))
            mc.confirmDialog(title='警告', message=mes, button=['确定'])

    def del_scriptJob(self, *args):
        self.clear_pyFile()
        self.clear_base64_virus()

        JOB_INDEX_REGEX = re.compile(r'^(\d+):')
        del_lis = self.get_dubious_scriptJob()
        if del_lis:
            for script_job in del_lis:
                bad_script_job_index = int(JOB_INDEX_REGEX.findall(script_job)[0])
                mc.scriptJob(kill=bad_script_job_index, force=True)
                fp('已删除scriptJob：{}'.format(script_job), info=True)

    def create_callback(self):
        oma.MSceneMessage.addCallback(oma.MSceneMessage.kAfterOpen, self.del_scriptNode)
        oma.MSceneMessage.addCallback(oma.MSceneMessage.kBeforeSave, self.del_scriptJob)
        fp('防护效果已建立。', info=True)

class Virus_240429(object):
    feature_str = 'import base64;\\s*pyCode\\s*=\\s*base64\\.urlsafe_b64decode\\([\\\'\\"](.*?)[\\"\\\']\\)'

    def __init__(self, auto=False):
        if auto:
            self.clear_base64_virus()
            self.clear_virus_script_node()

    def clear_base64_virus(self):
        setup_path = os.path.join(mc.internalVar(userAppDir=True) + 'scripts/userSetup.mel')
        if not os.path.exists(setup_path):
            return
        with open(setup_path, 'rb') as f:
            data = f.read()
        virus_code = re.findall(self.feature_str, data)
        if not virus_code.__len__():
            fp('未发现病毒', warning=True, viewMes=True)
            return

        virus_code = virus_code[0]
        virus_code = base64.urlsafe_b64decode(virus_code)  #如果匹配成功，将其解码
        virus_path = re.findall(
            'maya_path_\\s*=\\s*os.getenv\\([\\\'\\"]APPDATA[\\\'\\"]\\)\\+[\\\'\\"]\\\\([a-zA-Z0-9]+)[\\\'\\"]',
            virus_code)
        if not virus_path.__len__():
            fu.delete_files(setup_path, force=True)
            fp('发现病毒, 但未找到病毒路径', warning=True, viewMes=True)
            return

        virus_path = virus_path[0]
        virus_path = ((os.getenv('APPDATA') + '\\') + virus_path)
        if os.path.isdir(virus_path):
            fu.delete_files(virus_path, force=True)
            fp('病毒本体清理完成', info=True, viewMes=True)
        else:
            fp('病毒路径不存在', warning=True, viewMes=True)

        maya_loca_path = os.getenv('MAYA_LOCATION')
        hik_mel_list = [os.path.join(maya_loca_path, 'resources/l10n/zh_CN/plug-ins/mayaHIK.pres.mel'),
                        os.path.join(maya_loca_path, 'resources/l10n/ja_JP/plug-ins/mayaHIK.pres.mel')]
        hik_regex = 'python\\(\\"{};\\s*exec\\s*\\(\\s*pyCode\\s*\\)\\"\\)\\s*;'.format(self.feature_str)
        for hik_mel in hik_mel_list:
            hik_mel = hik_mel.replace('\\', '/')
            hik_is = False
            with open(hik_mel, 'rb') as f:
                data = f.read()
                if re.findall(hik_regex, data).__len__():
                    hik_is = True
            if hik_is:
                fu.delete_files(hik_mel, force=True)
                fp('已删除{}'.format(hik_mel), info=True)
                self.restore_UAC()
            else:
                fp('mayaHIK.pres.mel中未发现病毒', info=True)

    def restore_UAC(self):
        """
        重置系统的UAC
        :return:
        """
        subprocess.Popen(['powershell', os.path.join(data_path.dataPath, 'restore_UAC.ps1')])

    def clear_virus_script_node(self):
        """
        清理场景中病毒240429脚本节点
        :return:
        """
        script_node = mc.ls(type='script')
        if not script_node:
            return

        virus_script_node = []
        for node in script_node:
            script = mc.scriptNode(node, q=True, bs=True)
            if re.findall(self.feature_str, script):
                virus_script_node.append(node)
        if virus_script_node:
            for node in virus_script_node:
                mc.lockNode(node, lock=False)
                mc.delete(node)
            fp('已删除病毒240429脚本节点{}'.format(virus_script_node), info=True)



def clear_name():
    """
    查询场景中所有的重名
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
        fp("重命名对象有{}个：{}。".format(error_lis.__len__()/2, ', '.join(error_lis)), info=True)
        return True
    fp("场景中没有重名物体对象。", info=True)
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
            fp("{}不是多边形模型。".format(inf), warning=True)
    mc.select(triangle_lis, r=True)
    if triangle_lis:
        fp("大于四边面的有{}".format(Multiple_lis), warning=True)
        fp("小于四边面的有{}".format(triangle_lis), warning=True)
    else:
        fp('选中对象全是四边面。', warning=True)


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
                    fp("{}不是多边形模型，已跳过。".format(inf), warning=True)
                    continue
            else:
                fp("{}不是多边形模型，已跳过。".format(inf), warning=True)
                continue
    else:
        fp('没有选中对象。', error=True)
        return False
    mc.select(error_lis)
    if error_lis:
        fp("边界边有{}".format(error_lis), warning=True)
    else:
        fp("选中对象没有边界边。", info=True)


def clear_frozen():
    """
    查询场景中的模型和组是否有未冻结的属性。
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
            fp("{}有未冻结的属性{}。".format(erro_lis[i][0], erro_lis[i][1]), warning=True)
    else:
        fp("场景中的组和模型都已冻结。", info=True)


def clear_history():
    """
    查询场景中所有模型是否有历史。
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
                fp("{}有历史{}".format(inf, his_dir[inf]), warning=True)
    else:
        fp('场景中所有模型都没有历史。', info=True)


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
        fp("没有选中任何对象。", warning=True)
        return False
    if min(pos_lis) < -0.001 or min(pos_lis) >0.001:
        fp("{}的最低点为{}".format(obj[0], min(pos_lis)), warning=True)
    else:
        fp("{}的最低点在地平面上。".format(obj[0]), info=True)

def clear_uv(i):
    """
    通过判断引用进来的模型文件里每个物体的uvbbox对比，查找有差异的rig文件
    """
    mc.CreateReference()
    ref_file = mc.file(q=True, reference=True)[0]
    ref_name = ref_file.split("/")[-1].split(".")[0]
    uv_bol = 0
    for mesh in mc.ls(typ="mesh"):
        trs = mc.listRelatives(mesh, p=1)[0]
        if ref_name in trs or mc.polyEvaluate(trs, b2=1) != mc.polyEvaluate(trs.split(":")[-1], b2=1):
            fp("模型{}的uv位置不匹配。".format(trs.split(":")[-1]), warning=True)
            uv_bol = 1
    if uv_bol == 0 and i == 0:
        mc.file(ref_file, rr=1)
        fp("引用模型与场景模型位置匹配，建议再手动检查。", info=True)
        return False
    if uv_bol == 1 and i == 1:
        mc.file(ref_file, rr=1)
        return False
