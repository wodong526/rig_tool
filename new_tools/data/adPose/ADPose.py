# coding:utf-8
import math
import re
import pymel.core as pm
import bs
import config
reload(bs)


def create_group(n="|FaceGroup|SkeletonGroup", d=False, v=None, i=None):
    if d:
        if pm.objExists(n):
            pm.delete(n)
    if pm.objExists(n):
        return pm.PyNode(n)
    fields = n.split("|")
    n = fields.pop(-1)
    if len(fields) > 1:
        result = pm.group(em=1, n=n, p=create_group("|".join(fields)))
    else:
        result = pm.group(em=1, n=n)
    if v is not None:
        result.v.set(v)
    if i is not None:
        result.inheritsTransform.set(i)
    return result


def free_joints():
    print 2414
    polygons = get_selected_polygons()
    skins = []
    for polygon in polygons:
        for skin in pm.listHistory(polygon, type="skinCluster"):
            if skin not in skins:
                skins.append(skin)
    joints = []
    for skin in skins:
        for joint in skin.influenceObjects():
            if joint not in joints:
                joints.append(joint)
    has_rotate_joints = []
    for joint in joints:
        rotate = sum([abs(xyz) for xyz in joint.r.get()])
        if rotate > 0.00001:
            has_rotate_joints.append(joint)
    for joint in has_rotate_joints:
        matrix = joint.getMatrix()
        print matrix
        trans = pm.datatypes.TransformationMatrix(matrix)
        rotate = trans.getRotation()
        joint.jointOrient.set(rotate[0]/math.pi*180.0, rotate[1]/math.pi*180.0, rotate[2]/math.pi*180.0)


def find_node_by_name(name):
    nodes = pm.ls(name)
    if len(nodes) == 1:
        return nodes[0]
    return pm.displayInfo("can not find " + name)


def comb_target_to_targets(targets):
    new_targets = []
    for target in targets:
        if target[-5:-2] == "_IB":
            target = target[:-5]
        new_targets.append(target)
    return list(set([target for comb in new_targets for target in comb.split("_COMB_") if target]))


def get_selected_polygons():
    polygons = []
    for polygon in pm.selected(type="transform"):
        shape = polygon.getShape()
        if shape is None:
            continue
        if shape.type() != "mesh":
            continue
        polygons.append(polygon)
    return polygons


UI_JOINT = None
UI_CTRL = None


def find_ui_ctrl(joint):
    global UI_JOINT, UI_CTRL
    if UI_JOINT is None:
        return
    if UI_CTRL is None:
        return
    if joint.name() != UI_JOINT:
        return
    ctrl_list = pm.ls(UI_CTRL)
    if len(ctrl_list) != 1:
        return
    return ctrl_list[0]


def update_ui_ctrl(joint, ctrl):
    global UI_JOINT, UI_CTRL
    UI_JOINT, UI_CTRL = None, None
    if not isinstance(joint, (str, unicode)):
        return
    if not isinstance(ctrl, (str, unicode)):
        return
    if joint == u"":
        return
    if ctrl == u"":
        return
    print "up date"
    UI_JOINT = joint
    UI_CTRL = ctrl


def find_ctrl_by_joint(joint):
    if "Part" in joint.name():
        return
    ctrl_list = pm.ls(config.get_ctrl_names(joint.name().split("|")[-1].split(":")[-1]), type="transform")
    if len(ctrl_list) == 1:
        return ctrl_list[0]
    else:
        return find_ui_ctrl(joint)


def find_mirror_joint(joint):
    joints = pm.ls(config.get_rl_names(joint.name().split("|")[-1].split(":")[-1]), type="joint")
    if len(joints) != 1:
        return
    return joints[0]


def create_node(typ, n):
    if pm.objExists(n):
        pm.delete(n)
    return pm.createNode(typ, n=n)


def pose_to_matrix(pose):
    angle, direction = float(pose[0]), float(pose[1])
    sin = math.sin(math.pi * direction / 180)
    cos = math.cos(math.pi * direction / 180)
    data = [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, cos, sin, 0.0],
        [0.0, -sin, cos, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]
    direction_matrix = pm.datatypes.Matrix(data)
    sin = math.sin(math.pi * angle / 180)
    cos = math.cos(math.pi * angle / 180)
    data = [
        [cos, sin, 0, 0.0],
        [-sin, cos, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]
    angle_matrix = pm.datatypes.Matrix(data)
    matrix = direction_matrix.inverse() * angle_matrix * direction_matrix
    return matrix


def break_delete(nodes):
    for node in nodes:
        for src, dst in node.inputs(c=1, p=1):
            dst.disconnect(src)
    pm.delete(nodes)


def update_sdk(node, dvs, cd, name, keep):
    if node.hasAttr(name):
        if keep:
            return node.attr(name)
    else:
        node.addAttr(name, k=0, at="double", min=0, max=1)
    break_delete(node.attr(name).inputs(type="animCurveUU"))
    for dv, v in dvs:
        pm.setDrivenKeyframe(node.attr(name), cd=cd, dv=dv, v=v, itt="linear", ott="linear")
    return node.attr(name)


def get_sorted_poses(poses):
    direction_angles = {}
    for angle, direction in poses:
        direction_angles.setdefault(direction, []).append(angle)
    for direction, angles in direction_angles.items():
        direction_angles[direction] = list(sorted(angles))
    directions = sorted(direction_angles.keys())
    poses = []
    for direction in directions:
        for angle in direction_angles[direction]:
            poses.append(tuple([angle, direction]))
    return poses


def target_is_pose(target_name):
    return "_COMB_" not in target_name


def target_is_comb(target_name):
    return "_COMB_" in target_name and target_name[-5:-2] != "_IB"


def target_is_ib(target_name):
    return "_COMB_" in target_name and target_name[-5:-2] == "_IB"


def dup_target(target_name, polygons):
    create_group("|adPoses").v.set(1)
    group = create_group("|adPoses|edit_" + target_name, d=True, v=True)
    for polygon in polygons:
        polygon.v.set(0)
        dup = polygon.duplicate()[0]
        for shape in dup.getShapes():
            if shape.io.get():
                pm.delete(shape)
        dup.setParent(group)
        dup.rename(target_name+"_"+polygon.name().split("|")[-1])
        dup.v.set(1)
        for shape in dup.getShapes():
            shape.overrideEnabled.set(True)
            shape.overrideColor.set(13)
    panels = pm.getPanel(all=True)
    for panel in panels:
        if pm.modelPanel(panel, ex=1):
            pm.modelEditor(panel, e=1, wireframeOnShaded=True)
    pm.select(cl=1)


class ADPoses(object):

    # get install
    @classmethod
    def load_by_name(cls, name):
        joint = find_node_by_name(name)
        if joint is None:
            return None
        control = find_ctrl_by_joint(joint)
        if control is None:
            return None
        return cls(joint, control)

    @classmethod
    def get_targets(cls):
        ad_poses = []
        for joint in pm.ls(type="joint"):
            if not joint.hasAttr("angle"):
                continue
            ctrl = find_ctrl_by_joint(joint)
            if ctrl is None:
                continue
            ad_poses.append(cls(joint, ctrl))

        targets = []
        for ad in ad_poses:
            for pose in ad.get_poses():
                target_name = ad.target_name(pose)
                targets.append(target_name)
                comb_name = "COMB_" + target_name
                if not ad.joint.hasAttr(comb_name):
                    continue
                for node in ad.joint.attr(comb_name).outputs(type="combinationShape"):
                    if target_name not in node.name():
                        continue
                    for attr in node.listAttr(ud=1):
                        comb_target_name = attr.name().split(".")[-1]

                        if comb_target_name in targets:
                            continue
                        targets.append(comb_target_name)
        return targets

    # get info by targets
    @classmethod
    def targets_to_ad_poses(cls, targets):
        data = {}
        for target in targets:
            match = re.match("(.+)_a([0-9]{1,3})_d([0-9]{1,3})", target)
            if match is None:
                continue
            joint_name, angle, direction = match.groups()
            angle, direction = int(angle), int(direction)
            data.setdefault(joint_name, []).append((angle, direction))
        ad_poses = []
        for joint_name, poses in data.items():
            joint = find_node_by_name(joint_name)
            if joint is None:
                continue
            ctrl = find_ctrl_by_joint(joint)
            if ctrl is None:
                continue
            ad = cls(joint, ctrl)
            ad_poses.append([ad, poses])
        return ad_poses

    @classmethod
    def target_to_ad_pose(cls, target):
        ad, poses = cls.targets_to_ad_poses([target])[0]
        return ad, poses[0]

    @classmethod
    def target_to_comb_ib(cls, target):
        comb_node = find_node_by_name(target[:-5])
        ib = int(target[-2:])
        return comb_node, ib

    @classmethod
    def target_to_combs(cls, target):
        return [[ad, poses[0]] for ad, poses in cls.targets_to_ad_poses(target.split("_COMB_"))]

    # get target name
    def target_name(self, pose):
        angle, direction = pose
        return "{self.prefix}_a{angle}_d{direction}".format(self=self, angle=angle, direction=direction)

    @staticmethod
    def comb_name(combs):
        return "_COMB_".join(sorted([ad.target_name(pose) for ad, pose in combs]))

    @classmethod
    def ib_name(cls, comb_name, ib):
        return comb_name + "_IB%02d" % ib

    # set ctrl
    def set_pose(self, pose):
        angle, direction = pose
        if self.joint.hasAttr("angle_direction_scale"):
            angle *= self.joint.angle_direction_scale.get()
        self.control.setMatrix(pose_to_matrix([angle, direction]))
        joint_pose = self.get_control_pose(init=False, int_round=False)
        if abs(pose[0] - joint_pose[0]) > 0.0001 or abs(pose[1] - joint_pose[1]) > 0.0001:
            if self.joint.hasAttr("angle_direction_scale"):
                return
            if abs(joint_pose[0]) < 0.0001:
                return
            scale = pose[0] / joint_pose[0]
            angle *= scale
            self.control.setMatrix(pose_to_matrix([angle, direction]))
            joint_pose = self.get_control_pose(init=False, int_round=False)
            if abs(pose[0] - joint_pose[0]) > 0.0001 or abs(pose[1] - joint_pose[1]) > 0.0001:
                return
            self.joint.addAttr("angle_direction_scale", at="double", k=1)
            self.joint.angle_direction_scale.set(scale)

    @classmethod
    def set_pose_by_targets(cls, pose_targets, all_targets=None, ib=None):
        if all_targets is None:
            all_targets = cls.get_targets()
        if ib is None:
            ib = 60
            for target in pose_targets:
                if target[-5:-2] == "_IB":
                    ib = int(target[-2:])
        pose_targets = comb_target_to_targets(pose_targets)
        all_targets = comb_target_to_targets(all_targets)
        for ad, _ in cls.targets_to_ad_poses(all_targets):
            ad.set_pose([0, 0])
        for ad, poses in cls.targets_to_ad_poses(pose_targets):
            angle, direction = poses[-1]
            angle = float(angle) * ib / 60.0
            ad.set_pose((angle, direction))

    # add
    def add_comb(self, pose):
        comb_name = "COMB_" + self.target_name(pose)
        if not self.joint.hasAttr(comb_name):
            self.joint.addAttr(comb_name, k=1, at="double", min=0, max=1)
        angle, direction = pose
        direction_attr = self.joint.attr("direction_%i" % direction)
        dvs = [[0, 0], [pose[0], 1], [180, 1]]
        angle_attr = self.update_sdk(dvs, self.joint.angle, "angle_%i_%i_%i" % (dvs[0][0], dvs[1][0], dvs[2][0]), True)
        bw = create_node("blendWeighted", n=self.prefix+comb_name)
        angle_attr.connect(bw.input[0])
        direction_attr.connect(bw.weight[0])
        bw.output.connect(self.joint.attr(comb_name))

    @classmethod
    def add_combs(cls, comb_poses):
        comb_name = cls.comb_name(comb_poses)
        if pm.objExists(comb_name):
            return find_node_by_name(comb_name).attr(comb_name)
        comb = create_node("combinationShape", comb_name)
        comb.combinationMethod.set(1)
        for i, (ad, pose) in enumerate(comb_poses):
            ad.add_comb(pose)
            ad.joint.attr("COMB_" + ad.target_name(pose)).connect(comb.inputWeight[i])
        dvs = [[0, 0], [1, 1]]
        update_sdk(comb, dvs, comb.attr("outputWeight"), comb_name, True)
        return comb.attr(comb_name)

    @classmethod
    def add_ib(cls, comb_node, ib):
        ib_target_name = comb_node.name() + "_IB%02d" % ib
        if comb_node.hasAttr(ib_target_name):
            return comb_node.attr(ib_target_name)
        if ib == 0:
            return comb_node.attr(ib_target_name)
        if not comb_node.hasAttr(ib_target_name):
            comb_node.addAttr(ib_target_name)
        cls.update_comb_sdk(comb_node)
        return comb_node.attr(ib_target_name)

    @classmethod
    def update_comb_sdk(cls, comb_node):
        comb_name = comb_node.name()
        attr_ibs = []
        for attr in comb_node.listAttr(ud=1):
            attr_name = attr.name().split(".")[-1]
            if attr_name == comb_name:
                ib = 60
            else:
                str_ib = attr_name[len(comb_name)+3:]
                if not str_ib.isdigit():
                    continue
                ib = int(str_ib)
            if ib == 0:
                continue
            attr_ibs.append([attr_name, ib])
        ibs = list(sorted(set([ib for _, ib in attr_ibs] + [0, 61])))
        for attr, ib in attr_ibs:
            index = ibs.index(ib)
            dvs = [[float(ibs[index + i])/60.0, v] for i, v in [[-1, 0], [0, 1], [1, 0]]]
            update_sdk(comb_node, dvs, comb_node.outputWeight, attr, False)

    def add_pose(self, pose):
        poses = self.get_poses()
        if pose not in poses:
            poses.append(pose)
            self.update_poses(poses)
        name = self.target_name(pose)
        return self.joint.attr(name)

    @classmethod
    def add_by_target(cls, target):
        if target_is_ib(target):
            comb, ib = cls.target_to_comb_ib(target)
            return cls.add_ib(comb, ib)
        elif target_is_comb(target):
            return cls.add_combs(cls.target_to_combs(target))
        elif target_is_pose(target):
            ad, pose = cls.target_to_ad_pose(target)
            return ad.add_pose(pose)

    @classmethod
    def add_by_targets(cls, target_names, polygons=None):
        for target in target_names:
            attr = cls.add_by_target(target)
            if polygons is None:
                continue
            for polygon in polygons:
                bs.bridge_connect(attr, polygon)

    # delete
    @classmethod
    def delete_comb(cls, comb_name):
        comb_node = find_node_by_name(comb_name)
        if comb_node is None:
            return
        for attr in comb_node.listAttr(ud=1):
            for bs_attr in attr.outputs(type="blendShape", p=1):
                bs.delete_target(bs_attr)
        joint_attrs = comb_node.inputs(type="joint", p=1)
        pm.delete(comb_node)
        for joint_attr in joint_attrs:
            if joint_attr.outputs(type="combinationShape"):
                continue
            pm.deleteAttr(joint_attr)

    @classmethod
    def delete_pose(cls, pose_target):
        for ad, poses in cls.targets_to_ad_poses([pose_target]):
            ad.delete_poses(poses)

    def delete_poses(self, poses):
        old_poses = self.get_poses()
        for pose in poses:
            if pose not in old_poses:
                continue
            name = self.target_name(pose)
            for bs_node in self.joint.attr(name).outputs(type="blendShape"):
                bs.delete_target(bs_node.attr(name))
            old_poses.remove(pose)
        self.update_poses(old_poses)

    @classmethod
    def delete_ib(cls, ib_name):
        if ib_name[-5:-2] != "_IB":
            return
        comb_name = ib_name[:-5]
        comb_node = find_node_by_name(comb_name)
        if comb_node is None:
            return
        if not comb_node.hasAttr(ib_name):
            return
        for bs_attr in comb_node.attr(ib_name).outputs(type="blendShape", p=1):
            bs.delete_target(bs_attr)
        pm.delete(comb_node.attr(ib_name).inputs(type="animCurveUU"))
        pm.deleteAttr(comb_node.attr(ib_name))
        cls.update_comb_sdk(comb_node)

    @classmethod
    def delete_by_targets(cls, target_names):
        for target_name in target_names:
            if target_is_ib(target_name):
                cls.delete_ib(target_name)
            elif target_is_comb(target_name):
                cls.delete_comb(target_name)
            elif target_is_pose(target_name):
                cls.delete_pose(target_name)

    # edit
    def edit_by_selected_ctrl_pose(self):
        polygons = get_selected_polygons()
        pose = self.get_control_pose()
        attr = self.add_pose(pose)
        if not len(polygons) == 2:
            return pose
        src, dst = polygons
        bs.bridge_connect_edit(attr, src, dst)
        return pose

    @classmethod
    def edit_by_selected_target(cls, target_name):
        polygons = get_selected_polygons()
        if not len(polygons) == 2:
            return pm.warning(u"please selected two ")
        src, dst = polygons
        attr = cls.add_by_target(target_name)
        bs.bridge_connect_edit(attr, src, dst)

    @classmethod
    def auto_edit_by_selected_target(cls, joints):
        polygons = get_selected_polygons()
        target_name = cls.get_auto_target_name(joints)
        if target_name is None:
            return
        attr = cls.add_by_target(target_name)
        if not len(polygons) == 2:
            return
        src, dst = polygons
        bs.bridge_connect_edit(attr, src, dst)

    @staticmethod
    def edit_by_duplicate(duplicate, attr, edit=True):
        target_name = attr.name().split(".")[-1]
        src_polygons = bs.get_name_polygon_by_short_name(bs.get_child_polygons(duplicate))
        src_polygons = {k[len(target_name)+1:]: v for k, v in src_polygons.items()}
        dst_polygons = bs.get_name_polygon_by_short_name(pm.ls(src_polygons.keys()))
        for src, dst in bs.get_polygon_matrix_by_map([src_polygons, dst_polygons]):
            dst.v.set(True)
            if edit:
                bs.bridge_connect_edit(attr, src, dst)
        duplicate.v.set(0)
        duplicate.getParent().v.set(0)
        pm.select(cl=True)

    @classmethod
    def auto_edit(cls, edit=True):
        all_targets = cls.get_targets()
        group = create_group("|adPoses")
        for duplicate in group.listRelatives():
            if not duplicate.v.get():
                continue
            target_name = duplicate.name()
            if target_name[:5] != "edit_":
                continue
            target_name = target_name[5:]
            attr = cls.add_by_target(target_name)
            cls.set_pose_by_targets([target_name], all_targets=all_targets)
            cls.edit_by_duplicate(duplicate, attr, edit)

    def get_max_pose(self):
        poses = self.get_poses()
        direction_angles = {}
        for angle, direction in poses:
            direction_angles.setdefault(direction, []).append(angle)
        max_poses = []
        for direction, angles in direction_angles.items():
            max_poses.append((max(angles), direction))
        return max_poses

    def on_pose(self):
        if not self.joint.hasAttr("angle"):
            return False
        pose = self.get_control_pose(init=False)
        poses = self.get_max_pose()
        if pose in poses:
            return pose
        else:
            return False

    def comb_pose_ib(self):
        if not self.joint.hasAttr("angle"):
            return None, None
        poses = self.get_poses()
        direction_angles = {}
        for angle, direction in poses:
            direction_angles.setdefault(direction, []).append(angle)
        direction = int(round(self.joint.direction.get()))
        if direction not in direction_angles:
            return None, None
        angle = max(direction_angles[direction])
        comb_target_name = "COMB_" + self.target_name((angle, direction))
        if self.joint.hasAttr(comb_target_name):
            ib = int(round(self.joint.attr(comb_target_name).get()*60.0))
            return (angle, direction), ib
        else:
            return None, None

    @staticmethod
    def get_pose_target_by_ads(ads):
        if len(ads) != 1:
            return pm.warning("can not find pose")
        ad = ads[0]
        pose = ad.get_control_pose()
        if pose == (0, 0):
            return pm.warning("can not find pose")
        return ad.target_name(pose)

    @classmethod
    def get_comb_target_by_ads(cls, ads):
        if len(ads) <= 1:
            return pm.warning("can not find comb pose")
        comb_poses = []
        for ad in ads:
            pose = ad.on_pose()
            if pose:
                comb_poses.append([ad, pose])
        if len(comb_poses) <= 1:
            return pm.warning("can not find comb pose")
        return cls.comb_name(comb_poses)

    @classmethod
    def get_ib_target_by_ads(cls, ads):
        if len(ads) <= 1:
            return pm.warning("can not find ib pose")
        ib_poses = dict()
        for ad in ads:
            pose, ib = ad.comb_pose_ib()
            ib_poses.setdefault(ib, []).append([ad, pose])
        if len(ib_poses.keys()) != 1:
            return pm.warning("can not find ib pose")
        if ib_poses.keys()[0] is None:
            return pm.warning("can not find ib pose")
        comb_poses = ib_poses.values()[0]
        comb_name = cls.comb_name(comb_poses)
        comb_node = find_node_by_name(comb_name)
        if comb_node is None:
            return pm.warning("can not find ib pose")
        ib = ib_poses.keys()[0]
        return cls.ib_name(comb_name, ib)

    @classmethod
    def get_auto_target_name(cls, joints):
        if joints:
            joints = pm.ls(joints, type="joint")
        polygons = get_selected_polygons()
        if not joints:
            skins = []
            for polygon in polygons:
                for skin in pm.listHistory(polygon, type="skinCluster"):
                    if skin not in skins:
                        skins.append(skin)
            joints = []
            for skin in skins:
                for joint in skin.influenceObjects():
                    if joint not in joints:
                        joints.append(joint)
        has_rotate_joints = []
        for joint in joints:
            rotate = sum([abs(xyz) for xyz in joint.r.get()])
            if rotate > 0.00001:
                has_rotate_joints.append(joint)
        ads = []
        for joint in has_rotate_joints:
            ctrl = find_ctrl_by_joint(joint)
            if ctrl is None:
                continue
            ads.append(cls(joint, ctrl))
        for ctrl in pm.ls("FKIK*_R", "FKIK*_L"):
            if ctrl.hasAttr("FKIKBlend"):
                ctrl.FKIKBlend.set(0)
        target_name = None
        if target_name is None:
            target_name = cls.get_pose_target_by_ads(ads)
        if target_name is None:
            target_name = cls.get_comb_target_by_ads(ads)
        if target_name is None:
            target_name = cls.get_ib_target_by_ads(ads)
        if target_name is None:
            for ad in ads:
                ad.set_pose([0, 0])
            return pm.displayInfo("auto to zero")
        return target_name

    @classmethod
    def auto_dup(cls, joints=None):
        polygons = get_selected_polygons()
        target_name = cls.get_auto_target_name(joints)
        if target_name is None:
            return
        cls.set_pose_by_targets([target_name], [], None)
        dup_target(target_name, polygons)

    @classmethod
    def dup_targets(cls, targets):
        polygons = get_selected_polygons()
        for target in targets:
            cls.set_pose_by_targets([target], targets)
            dup_target(target, polygons)
        for polygon in polygons:
            polygon.v.set(1)
        for target in targets:
            cls.add_by_target(target)

    @classmethod
    def auto_apply(cls, joints=None):
        selected = pm.selected()
        if not pm.objExists("|adPoses"):
            create_group("|adPoses").v.set(0)
            pm.select(selected)
        group = create_group("|adPoses")
        if group.v.get():
            return cls.auto_edit(edit=True)
        else:
            return cls.auto_dup(joints)

    @staticmethod
    def targets_to_mirror(targets):
        targets = [t for t in targets if "_COMB_" not in t]+[t for t in targets if "_COMB_" in t]
        joints = []
        for target in targets:
            for field in re.split("_COMB_|_IB[0-9]{2}", target):
                pattern = re.match("^(.+)_a([0-9]{1,3})_d([0-9]{1,3})$", field)
                if pattern is None:
                    continue
                joint, _, _ = pattern.groups()
                if joint not in joints:
                    joints.append(joint)

        replace_joints = []
        for joint_name in joints:
            joint = find_node_by_name(joint_name)
            if joint is None:
                continue
            joints = pm.ls(config.get_rl_names(joint_name), type="joint")
            if len(joints) != 1:
                continue
            mirror_name = joints[0].name().split("|")[-1]
            replace_joints.append([joint_name, mirror_name])

        target_mirrors = []
        for target in targets:
            mirror = target
            for src, dst in replace_joints:
                mirror = mirror.replace(src, dst)
            target_mirrors.append([target, mirror])
        return target_mirrors

    @classmethod
    def mirror_by_targets(cls,  targets):
        polygons = get_selected_polygons()
        target_mirrors = cls.targets_to_mirror(targets)
        cls.add_by_targets([m for _, m in target_mirrors], polygons)
        for polygon in polygons:
            bs.mirror_targets(polygon, target_mirrors)

    @classmethod
    def warp_copy_targets(cls, targets):
        polygons = get_selected_polygons()
        if not len(polygons) == 2:
            return pm.warning("please selected two polygon")
        targets = [t for t in targets if "_COMB_" not in t]+[t for t in targets if "_COMB_" in t]
        src, dst = polygons
        cls.set_pose_by_targets([])
        pm.refresh()
        warp = dst.duplicate()[0]
        bs.get_orig(warp)
        pm.select(warp, src)
        pm.mel.CreateWrap()
        for target in targets:
            cls.set_pose_by_targets([target])
            pm.select(warp, dst)
            cls.edit_by_selected_target(target)
            pm.refresh()
        pm.delete(warp)

    def __init__(self, joint, control):
        self.joint = joint
        self.control = control
        self.prefix = joint.name().split("|")[-1]
        self.convert_old_to_new()

    def convert_old_to_new(self):
        old_ads = []
        bs_nodes = []
        nodes = []
        for multiply in pm.ls(self.prefix + "*_a*_d*", type="multiplyDivide"):
            pattern = re.match(".+_a([0-9]{1,3})_d([0-9]{1,3})_mul", multiply.name())
            if pattern is None:
                continue
            nodes.append(multiply)
            angle, direction = pattern.groups()
            angle, direction = int(angle), int(direction)
            old_ads.append([angle, direction])
            for bs_node in multiply.outputs(type="blendShape"):
                if bs_node not in bs_nodes:
                    bs_nodes.append(bs_node)
        convert = False
        for angle, direction in old_ads:
            name = self.target_name([angle, direction])
            if not self.joint.hasAttr(name):
                convert = True
                break
        if not convert:
            return
        pm.delete(nodes)
        self.update_angle_direction()
        self.update_poses(old_ads)
        for pose in old_ads:
            name = self.target_name(pose)
            if not self.joint.hasAttr(name):
                continue
            for bs_node in bs_nodes:
                if not bs_node.hasAttr(name):
                    continue
                self.joint.attr(name).connect(bs_node.attr(name), f=1)

    def update_angle_direction(self):
        if not pm.pluginInfo("matrixNodes", q=1, l=1):
            pm.loadPlugin("matrixNodes")
        if self.joint.hasAttr("angle"):
            return
        if self.joint.hasAttr("direction"):
            return
        self.joint.addAttr("angle", k=1, at="double", min=0, max=180)
        self.joint.addAttr("direction", k=1, at="double", min=0, max=360)

        compose = create_node("composeMatrix", n=self.prefix + "_compose")
        self.joint.rotateX.connect(compose.inputRotateX)
        self.joint.rotateZ.connect(compose.inputRotateZ)
        self.joint.rotateY.connect(compose.inputRotateY)
        self.joint.rotateOrder.connect(compose.inputRotateOrder)

        point = create_node("pointMatrixMult", n=self.prefix + "_pointMatrix")
        point.inPointX.set(1)
        compose.outputMatrix.connect(point.inMatrix)

        angle = create_node("angleBetween", n=self.prefix + "_angle")
        angle.vector1.set(1, 0, 0)
        point.outputX.connect(angle.vector2X)
        point.outputY.connect(angle.vector2Y)
        point.outputZ.connect(angle.vector2Z)

        angle_unit = create_node("unitConversion", n=self.prefix + "_angleUnit")
        angle_unit.conversionFactor.set(180 / math.pi)
        angle.angle.connect(angle_unit.input)
        angle_unit.output.connect(self.joint.angle)

        direction = create_node("angleBetween", n=self.prefix + "_direction")
        direction.vector1.set(0, 0, 0)
        direction.vector1.set(0, 1, 0)
        point.outputY.connect(direction.vector2Y)
        point.outputZ.connect(direction.vector2Z)

        direction_unit = create_node("unitConversion", n=self.prefix + "_directionUnit")
        direction_unit.conversionFactor.set(180 / math.pi)
        direction.angle.connect(direction_unit.input)

        minus = create_node("plusMinusAverage", n=self.prefix + "_minus")
        minus.input1D[0].set(360)
        minus.operation.set(2)
        direction_unit.output.connect(minus.input1D[1])

        condition = create_node("condition", n=self.prefix + "_condition")
        point.outputZ.connect(condition.firstTerm)
        condition.operation.set(2)
        direction_unit.output.connect(condition.colorIfTrueR)
        minus.output1D.connect(condition.colorIfFalseR)
        condition.outColorR.connect(self.joint.direction)

    def update_sdk(self, dvs, cd, name, keep=1):
        return update_sdk(self.joint, dvs, cd, name, keep)

    def update_poses(self, poses):
        self.update_angle_direction()
        direction_angles = {}
        for angle, direction in poses:
            direction_angles.setdefault(direction, []).append(angle)
        for direction, angles in direction_angles.items():
            direction_angles[direction] = list(sorted(angles))
        directions = sorted(direction_angles.keys())
        _sdk_ds = list(sorted(set([direction+offset for direction in directions for offset in [-360, 0, 360]])))
        use_attr_list = [self.joint.angle, self.joint.direction]
        for direction in directions:
            if direction == 360:
                direction = 0
            sdk_ds = list(sorted(set(_sdk_ds+[direction+90, direction-90])))
            index = sdk_ds.index(direction)
            dvs = [[sdk_ds[index+i]+o, v] for i, v in [[-1, 0], [0, 1], [1, 0]] for o in [-360, 0, 360]]
            direction_attr = self.update_sdk(dvs, self.joint.direction, "direction_%i" % direction, False)
            angles = direction_angles[direction]
            sdk_as = list(sorted(set(angles+[-1, 0, 180])))
            use_attr_list.append(direction_attr)
            for angle in angles:
                index = sdk_as.index(angle)
                dvs = [[sdk_as[index + i], v] for i, v in [[-1, 0], [0, 1], [1, 0]]]
                if dvs[-1][0] == 180:
                    dvs[-1][1] = 1
                angle_attr = self.update_sdk(dvs, self.joint.angle,
                                             "angle_%i_%i_%i" % (dvs[0][0], dvs[1][0], dvs[2][0]), True)
                name = self.target_name([angle, direction])
                if not self.joint.hasAttr(name):
                    self.joint.addAttr(name, k=1, at="double", min=0, max=1)
                pm.delete(self.joint.attr(name).inputs(type="blendWeighted"))
                bw = create_node("blendWeighted",  n=name)
                angle_attr.connect(bw.input[0])
                direction_attr.connect(bw.weight[0])
                bw.output.connect(self.joint.attr(name))
                use_attr_list.extend([angle_attr, self.joint.attr(name)])
        for attr in self.joint.listAttr(ud=1):
            if attr in use_attr_list:
                continue
            if not any([field in attr.name(includeNode=False) for field in [self.prefix, "angle", "direction"]]):
                continue
            pm.delete(attr.inputs(type="multiplyDivide"))
            pm.deleteAttr(attr)

    def get_control_pose(self, init=True, int_round=True):
        self.update_angle_direction()
        angle, direction = self.joint.angle.get(), self.joint.direction.get()
        if int_round:
            angle, direction = int(round(angle)), int(round(direction))
        if abs(direction - 360) < 0.0001:
            direction = 0
        if abs(angle - 0) < 0.0001:
            direction = 0
        if init:
            self.set_pose([angle, direction])
        return tuple([angle, direction])

    def get_poses(self):
        poses = []
        for attr in self.joint.listAttr(ud=1):
            name = attr.name(includeNode=False)
            if self.prefix not in name:
                continue
            pattern = re.match("^%s_a([0-9]{1,3})_d([0-9]{1,3})$" % self.prefix, name)
            if pattern is None:
                continue
            if not self.joint.hasAttr(name):
                continue
            angle, direction = pattern.groups()
            angle, direction = int(angle), int(direction)
            poses.append(tuple([angle, direction]))
        return get_sorted_poses(poses)

