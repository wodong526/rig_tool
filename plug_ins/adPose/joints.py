# coding:utf-8
import pymel.core as pm
import math
from maya.OpenMaya import *
from maya.OpenMayaAnim import *
import config
import bs as bs_api
from general_ui import *
import ADPose


def dot_qq(q1, q2):
    return q1.x * q2.x + q1.y * q2.y + q1.z * q2.z + q1.w * q2.w


def mul_qd(q, w):
    return pm.datatypes.Quaternion(q.x*w, q.y*w, q.z*w, q.w*w)


def add_qq(q1, q2):
    return pm.datatypes.Quaternion(q1.x + q2.x, q1.y + q2.y, q1.z + q2.z, q1.w + q2.w)


def slerp(q1, q2, t):
    cos_a = dot_qq(q1, q2)
    if cos_a < 0:
        cos_a = - cos_a
        mul_qd(q2, -1)
    if cos_a > 0.999999999:
        w1, w2 = 1-t, t
    else:
        sin_a = math.sqrt(1-cos_a*cos_a)
        a = math.atan2(sin_a, cos_a)
        in_sin_a = 1.0/sin_a
        w1 = math.sin((1-t)*a) * in_sin_a
        w2 = math.sin(t * a) * in_sin_a
    return add_qq(mul_qd(q1, w1), mul_qd(q2, w2))


def matrix_to_position_rotation(matrix):
    trans = pm.datatypes.TransformationMatrix(matrix)
    translate = trans.getTranslation("world")
    rotation = trans.getRotation().asQuaternion()
    return translate, rotation


def position_rotation_to_matrix(position, rotation):
    trnas = pm.datatypes.TransformationMatrix(rotation.matrix)
    trnas.setTranslation(position, space="world")
    return trnas.matrix


def ray_point(polygon, matrix, direction, point):
    dag_path = MDagPath()
    selection = MSelectionList()
    selection.add(polygon.name())
    selection.getDagPath(0, dag_path)
    fn_mesh = MFnMesh(dag_path)
    pm_ray_source = pm.datatypes.Point(0, 0, 0) * matrix
    pm_ray_direction = pm.datatypes.Vector(*direction) * matrix
    ray_source = MFloatPoint(*pm_ray_source)
    ray_direction = MFloatVector(*pm_ray_direction)
    hit_point = MFloatPoint()
    hit = fn_mesh.closestIntersection(ray_source, ray_direction, None, None, None, MSpace.kWorld, 10000, None, None,
                                      hit_point, None, None, None, None, None)
    if hit:
        return pm.datatypes.Point(hit_point[0], hit_point[1], hit_point[2])
    else:
        return point


def create_direction_joint(polygon, joint, i, matrix):
    direction = [[0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1], None][i]
    suffix = ["_ty_plus", "_ty_minus", "_tz_plus", "_tz_minus", "_half"][i]
    deform_joint = pm.joint(joint, n="corrective_" + joint.name()+suffix)
    deform_joint.setMatrix(matrix, ws=1)
    deform_joint.radius.set(joint.radius.get())
    if direction is None:
        point = pm.datatypes.Point(0, 0, 0.006) * matrix
    else:
        radius = pm.softSelect(q=1, ssd=1)
        point = pm.datatypes.Point(direction[0] * radius, direction[1]* radius, direction[2]* radius) * matrix
        if polygon:
            point = ray_point(polygon, matrix, direction, point)
    deform_joint.setTranslation(point, ws=1)
    return deform_joint


def find_mirror_joint(joint):
    joints = pm.ls(config.get_rl_names(joint.name().split("|")[-1].split(":")[-1]), type="joint")
    if len(joints) != 1:
        return
    return joints[0]


def create_joint(polygon, joint, directions, rotate_offset):
    matrix = joint.getMatrix(ws=1)
    if rotate_offset:
        parent_matrix = joint.getParent().getMatrix(ws=1)
        local_matrix = joint.getMatrix(ws=0)
        position, rotation = matrix_to_position_rotation(local_matrix)
        half_rotation = slerp(rotation, pm.datatypes.Quaternion(0, 0, 0, 1), 0.5)
        matrix = position_rotation_to_matrix(position, half_rotation) * parent_matrix
    deform_joints = []
    for i, direction in enumerate(directions):
        if direction:
            deform_joint = create_direction_joint(polygon, joint, i, matrix)
            deform_joints.append(deform_joint)
    return deform_joints


def world_fip_matrix(matrix):
    matrix.a01 *= -1
    matrix.a11 *= -1
    matrix.a21 *= -1
    matrix.a02 *= -1
    matrix.a12 *= -1
    matrix.a22 *= -1
    matrix.a30 *= -1
    return matrix


def mirror_joints(joints=None):
    if joints is None:
        joints = pm.ls(sl=1, type="joint")
    parent_joints = {}
    for joint in joints:
        parent = joint.getParent()
        if parent.type() != "joint":
            continue
        parent_joints.setdefault(parent, []).append(joint)
    for parent, children in parent_joints.items():
        mirror_parent = find_mirror_joint(parent)
        if not mirror_parent:
            continue
        for child in children:
            name = child.name().replace(parent.name(), mirror_parent.name())
            if "_plus" in name:
                name = name.replace("_plus", "_minus")
            elif "_minus" in name:
                name = name.replace("_minus", "_plus")
            if name == child.name():
                name = child.name()+"_mirror"
            if pm.ls(name, type="joint"):
                mirror_joint = pm.ls(name, type="joint")[0]
            else:
                mirror_joint = pm.joint(mirror_parent, name=name)
            mirror_joint.radius.set(child.radius.get())
            mirror_joint.setMatrix(world_fip_matrix(child.getMatrix(ws=1)), ws=1)


def mirror_selected_joints():
    src, dst = pm.selected(type="joint")
    src.setMatrix(world_fip_matrix(dst.getMatrix(ws=1)), ws=1)


def create_joints(polygon, joints, directions, rotate_offset, mirror):
    deform_joints = []
    for joint in joints:
        deform_joints += create_joint(polygon, joint, directions, rotate_offset)
    if mirror:
        mirror_joints(deform_joints)


def create_attach(prefix, parent, i, pl):
    msa = pm.group(em=1, p=parent, n=prefix+"Attach")
    pm.createNode("cMuscleSurfAttach", p=msa, n=prefix+"AttachShape")
    pl.worldMesh.connect(msa.surfIn)
    msa.rotateOrder.connect(msa.inRotOrder)
    msa.outTranslate.connect(msa.translate)
    msa.outRotate.connect(msa.rotate)
    msa.edgeIdx1.set(i * 4 + 0)
    msa.edgeIdx2.set(i * 4 + 3)
    msa.uLoc.set(0.5)
    msa.vLoc.set(0.5)
    return msa


def create_plane(name, parent, transforms, r):
    u"""
    :param name: 前缀
    :param parent: 父对象
    :param transforms: 空组
    :param r: 半径
    :return: 面片模型
    """
    pl = pm.polyPlane(w=1, h=1, sx=1, sy=1, ch=1)[0]
    pl.r.set(90, 0, 90)
    pl.s.set(r, r, r)
    pm.makeIdentity(apply=1, r=1, s=1)
    planes = []
    for transform in transforms:
        dup = pl.duplicate()[0]
        dup.setMatrix(transform.getMatrix(ws=1), ws=1)
        planes.append(dup)
    pm.delete(pl)
    if len(planes) > 1:
        pl = pm.polyUnite(planes, ch=0)[0]
    else:
        pl = planes[0]
        pm.makeIdentity(pl, apply=1, t=1, r=1, s=1)
    pl.setParent(parent)
    pl.rename(name)
    pl.v.set(0)
    return pl


def sdk_group():
    if pm.objExists("PlaneSdkSystem"):
        group = pm.PyNode("PlaneSdkSystem")
    else:
        group = pm.group(em=1, n="PlaneSdkSystem")
    group.inheritsTransform.set(0)
    return group


def action_group():
    if pm.objExists("PlaneSdkAttaches"):
        group = pm.PyNode("PlaneSdkAttaches")
    else:
        group = pm.group(em=1, n="PlaneSdkAttaches", p=sdk_group())
    group.inheritsTransform.set(0)
    return group


def get_shape(polygon):
    for shape in polygon.getShapes():
        if not shape.io.get():
            return shape


def assert_geometry(geometry=None, shape_type="mesh"):
    u"""
    :param geometry: 几何体
    :param shape_type: 形节点类型
    :return:
    判断物体是否为集合体
    """
    if geometry is None:
        selected = pm.selected(o=1)
        if len(selected) == 0:
            return pm.warning("please select a " + shape_type)
        geometry = selected[0]
    if geometry.type() == shape_type:
        return geometry.getParent()
    if geometry.type() != "transform":
        return pm.warning("please select a " + shape_type)
    shape = get_shape(geometry)
    if not shape:
        return pm.warning("please select a " + shape_type)
    if shape.type() != shape_type:
        return pm.warning("please select a " + shape_type)
    return geometry


def get_skin_cluster(polygon=None):
    u"""
    :param polygon: 多边形
    :return: 蒙皮节点
    """
    if polygon is None:
        polygon = assert_geometry(shape_type="mesh")
    if polygon is None:
        return
    for history in polygon.history(type="skinCluster"):
        return history
    pm.warning("\ncan not find skinCluster")


def get_weight_data(polygon):
    polygon = assert_geometry(polygon, shape_type="mesh")
    if polygon is None:
        return
    sk = get_skin_cluster(polygon)
    joints = sk.getInfluence()
    indices = MIntArray()
    indices.setLength(len(joints))
    for i, _ in enumerate(joints):
        indices[i] = i
    selected = MSelectionList()
    selected.add(sk.name())
    selected.add(get_shape(polygon).name()+".vtx[*]")
    depend_node = MObject()
    selected.getDependNode(0, depend_node)
    fn_skin = MFnSkinCluster(depend_node)
    path = MDagPath()
    components = MObject()
    weights = MDoubleArray()
    selected.getDagPath(1, path, components)
    fn_skin.getWeights(path, components, indices, weights)
    return weights, len(joints), polygon.getShape().numVertices()


def set_weight_data(polygon=None, weights=None):
    polygon = assert_geometry(polygon, shape_type="mesh")
    if polygon is None:
        return pm.warning("can not find polygon")
    sk = get_skin_cluster(polygon)
    joints = sk.getInfluence()
    indices = MIntArray()
    indices.setLength(len(joints))
    for i, _ in enumerate(joints):
        indices[i] = i
    selected = MSelectionList()
    selected.add(sk.name())
    selected.add(get_shape(polygon).name()+".vtx[*]")
    depend_node = MObject()
    selected.getDependNode(0, depend_node)
    fn_skin = MFnSkinCluster(depend_node)
    path = MDagPath()
    components = MObject()
    selected.getDagPath(1, path, components)
    fn_skin.setWeights(path, components, indices, weights)


def init_plane_weights(plane=None):
    weights, joint_len, vtx_len = get_weight_data(plane)
    for face_id in range(vtx_len/4):
        for joint_id in range(joint_len):
            sum_weights = 0.0
            for i in range(4):
                vtx_id = face_id * 4 + i
                weight_id = vtx_id * joint_len + joint_id
                weight = weights[weight_id]
                sum_weights += weight
            weight = sum_weights / 4.0
            for i in range(4):
                vtx_id = face_id * 4 + i
                weight_id = vtx_id * joint_len + joint_id
                weights[weight_id] = weight
    set_weight_data(plane, weights)


def half_plane_skin(plane):
    weights, joint_len, vtx_len = get_weight_data(plane)
    for face_id in range(vtx_len / 4):
        for joint_id in range(joint_len):
            for i in range(4):
                vtx_id = face_id * 4 + i
                weight_id = vtx_id * joint_len + joint_id
                weights[weight_id] = 0.5
    set_weight_data(plane, weights)


def comb_plane_dk(planes=None):
    if len(planes) <= 1:
        return pm.warning("can not find plane")
    group = sdk_group()
    # combine planes
    dup_pls = []
    for polygon in planes:
        dup = polygon.duplicate()[0]
        for s in dup.getShapes():
            if s.io.get():
                pm.delete(s)
        dup.setParent(w=1)
        dup_pls.append(dup)
    combine_polygon = pm.polyUnite(dup_pls, ch=0)[0]
    combine_polygon.setParent(group)
    combine_polygon.v.set(0)
    # comb blend shape
    bs_names = []
    bs_inputs = []
    for pl in planes:
        bs = bs_api.get_bs(pl)
        for name in bs.weight.elements():
            if name in bs_names:
                continue
            bs_names.append(name)
            inputs = bs.attr(name).inputs(p=1)
            if len(inputs) == 1:
                bs_inputs.append(inputs[0])
            else:
                bs_inputs.append(None)

    for index, name in enumerate(bs_names):
        ids = MIntArray()
        points = MPointArray()
        count = 0
        for pl in planes:
            _ids, _points = bs_api.get_bs_ids_points(pl, name)
            for i in range(_ids.length()):
                ids.append(_ids[i]+count)
            for i in range(_points.length()):
                points.append(_points[i])
            count += pl.getShape().numEdges()
        bs_api.add_target(combine_polygon, name)
        bs_api.set_bs_ids_points(combine_polygon, name, ids, points)
        attr = bs_inputs[index]
        if attr is None:
            continue
        bs_api.bridge_connect(attr, combine_polygon)
    # replace attach
    count = 0
    for pl in planes:
        attaches = pl.getShape().worldMesh[0].outputs(type="cMuscleSurfAttach")
        for att in attaches:
            combine_polygon.getShape().worldMesh[0].connect(att.surfIn, f=1)
            att.edgeIdx1.set(att.edgeIdx1.get() + count)
            att.edgeIdx2.set(att.edgeIdx2.get() + count)
        count += pl.getShape().numVertices()
    # comb weights
    joints = []
    for polygon in planes:
        sks = polygon.getShape().inputs(type="skinCluster")
        if sks:
            sk = sks[0]

            influences = sk.influenceObjects()
            for jnt in influences:
                if jnt not in joints:
                    joints.append(jnt)
    if not joints:
        return
    combine_sk = pm.skinCluster(joints, combine_polygon, tsb=1)
    weights = []
    for polygon in planes:
        sks = polygon.getShape().inputs(type="skinCluster")
        number = polygon.getShape().numVertices()
        wts = []
        if sks:
            sk = sks[-1]
        else:
            sk = None
        for jnt in joints:
            if sk is None:
                if jnt.name().split("|")[-1] == "StaticSkin":
                    wts.append([1.0] * number)
                else:
                    wts.append([0.0] * number)
            else:
                influences = sk.influenceObjects()
                if jnt in influences:
                    wts.append(list(sk.getWeights(sk.getGeometry()[0], influences.index(jnt))))
                else:
                    wts.append([0.0] * number)
        weights.extend([w for ws in zip(*wts) for w in ws])
    combine_sk.setWeights(combine_sk.getGeometry()[0], range(len(joints)), weights)
    # comb bs
    name = planes[0].name()
    pm.delete(planes)
    combine_polygon.rename(name)
    return combine_polygon


def create_plane_by_joints(joints):
    group = sdk_group()
    skins = []
    for joint in joints:
        skin = joint.getParent()
        if skin.type() != "joint":
            continue
        if skin not in skins:
            skins.append(skin)
        skin = skin.getParent()
        if skin.type() != "joint":
            continue
        if skin not in skins:
            skins.append(skin)
    plane = create_plane("Temp_PL", group, joints, 0.1)
    _attach_group = action_group()
    for i, joint in enumerate(joints):
        attach = create_attach(joint.name()+"Attach", _attach_group, i, plane)
        attach.v.set(0)
        pm.parent(pm.parentConstraint(attach, joint), attach)
    pm.skinCluster(skins, plane, tsb=1, mi=2)
    if len(skins) == 2:
        half_plane_skin(plane)
    return plane


def create_plane_by_selected():
    joints = pm.selected(type="joint")
    skin_joints = {}
    for joint in joints:
        if joint.tx.inputs(type="parentConstraint"):
            continue
        skin = joint.getParent()
        if skin.type() != "joint":
            continue
        skin_joints.setdefault(skin, []).append(joint)
    planes = []
    for joints in skin_joints.values():
        plane = create_plane_by_joints(joints)
        planes.append(plane)
    if pm.objExists("BodyDeformSdkPlane"):
        planes.insert(0, pm.PyNode("BodyDeformSdkPlane"))
    else:
        planes[0].rename("BodyDeformSdkPlane")
    if len(planes) > 1:
        plane = comb_plane_dk(planes)
    else:
        plane = planes[0]
    create_target_plane(plane)


def create_target_plane(plane):
    attaches = []
    for attach in plane.getShape().outputs(type="cMuscleSurfAttach"):
        attaches.append(attach)

    def key(_attach):
        return _attach.edgeIdx1.get()

    attaches = list(sorted(attaches, key=key))
    joints = []
    for attach in attaches:
        joint = attach.t.outputs(type="parentConstraint")[0].constraintTranslateX.outputs(type="joint")[0]
        joints.append(joint)
    group = sdk_group()
    if pm.objExists("*|PlaneSdkSystem|BodyDeformSdkTarget"):
        pm.delete("*|PlaneSdkSystem|BodyDeformSdkTarget")
    target = create_plane("BodyDeformSdkTarget", group, joints, 0.1)
    skin = pm.skinCluster(joints, target, mi=1, tsb=1)
    target.inheritsTransform.set(0)
    wts = []
    for i in range(len(joints)):
        for j in range(4):
            for k in range(len(joints)):
                if i == k:
                    wts.append(1)
                else:
                    wts.append(0)
    skin.setWeights(skin.getGeometry()[0], range(len(joints)),  wts)


def create_joint_test():
    polygon = pm.PyNode("body")
    joints = [pm.PyNode("Wrist_L")]
    directions = [True, True, True, True, False]
    rotate_offset = True
    mirror = True
    create_joints(polygon, joints, directions, rotate_offset, mirror)


class CreateJointTool(Tool):
    title = u"创建骨骼"
    button_text = u"创建"

    def __init__(self, parent=None):
        Tool.__init__(self, parent=get_host_app())
        self.polygon = MayaObjLayout(u"模型：", 40)
        self.kwargs_layout.addLayout(self.polygon)
        self.parents = JointList()
        self.kwargs_layout.addLayout(self.parents)
        self.directions = [QCheckBox(tex) for tex in ["+y", "-y", "+z", "-z", "center"]]
        self.kwargs_layout.addLayout(h_layout(*self.directions))
        self.kwargs = [QCheckBox(tex) for tex in [u"旋转偏移", u"镜像"]]
        self.kwargs_layout.addLayout(h_layout(*self.kwargs))
        for check in self.directions+self.kwargs:
            check.setChecked(True)
        self.directions[4].setChecked(False)

    def apply(self):
        polygon = self.polygon.obj
        parents = pm.ls(self.parents.get_joints(), type="joint")

        directions = [check.isChecked() for check in self.directions]
        rotate_offset = self.kwargs[0].isChecked()
        mirror = self.kwargs[1].isChecked()
        create_joints(polygon, parents, directions, rotate_offset, mirror)


def body_deform_sdk(joints=None):
    target = pm.ls("*|PlaneSdkSystem|BodyDeformSdkTarget", type="transform")
    driver = pm.ls("*|PlaneSdkSystem|BodyDeformSdkPlane", type="transform")
    if len(target) != 1:
        return pm.warning("can not find target")
    if len(driver) != 1:
        return pm.warning("can not find driver")
    temp = target[0].duplicate()[0]
    pm.select(temp, driver[0])
    ADPose.ADPoses.auto_edit_by_selected_target(joints)
    pm.delete(temp)