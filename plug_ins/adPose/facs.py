# coding:utf-8
import pymel.core as pm
import config
import re
import bs


def get_target_name(attr, default, value):
    if value > default:
        suffix = "max"
    else:
        suffix = "min"
    ctrl_name = attr.node().name().split("|")[-1].split(":")[-1]
    attr_name = attr.name(longName=0).split(".")[-1]
    return "_".join([ctrl_name, attr_name, suffix])


def find_add_sdk_data():
    data = []
    for ctrl in pm.selected(type="transform"):
        for trs in "trs":
            for xyz in "xyz":
                attr = ctrl.attr(trs + xyz)
                value = ctrl.attr(trs+xyz).get()
                default = dict(t=0, r=0, s=1)[trs]
                if abs(default-value) < 0.001:
                    continue
                target_name = get_target_name(attr, default, value)
                data.append(dict(attr=attr, value=value, default_value=default, target_name=target_name))
        for attr in ctrl.listAttr(ud=1):
            if pm.addAttr(attr, q=1, at=1) != "double":
                continue
            default = pm.addAttr(attr, q=1, dv=1)
            value = attr.get()
            if abs(default - value) < 0.001:
                continue
            target_name = get_target_name(attr, default, value)
            data.append(dict(attr=attr, value=value, default_value=default, target_name=target_name))
    return data


def get_bridge():
    if pm.objExists("CtrlAttrBsSdkBridge"):
        return pm.PyNode("CtrlAttrBsSdkBridge")
    else:
        return pm.group(em=1, n="CtrlAttrBsSdkBridge")


def add_sdk(attr, target_name, default_value, value):
    bridge = get_bridge()
    if bridge.hasAttr(target_name):
        return pm.warning(target_name + " already exists")
    bridge.addAttr(target_name, min=0, max=1, at="double", k=1)
    pm.setDrivenKeyframe(bridge.attr(target_name), cd=attr, dv=default_value, v=0, itt="linear", ott="linear")
    pm.setDrivenKeyframe(bridge.attr(target_name), cd=attr, dv=value, v=1, itt="linear", ott="linear")


def add_sdk_by_selected():
    u"""
    对选择的控制器添加驱动
    :return:
    """
    for kwargs in find_add_sdk_data():
        add_sdk(**kwargs)


def rest_ctrl(ctrl):
    for trs in "trs":
        attr = ctrl.attr(trs)
        if attr.inputs():
            continue
        if attr.isLocked():
            continue
        for xyz in "xyz":
            attr = ctrl.attr(trs + xyz)
            if attr.inputs():
                continue
            if attr.isLocked():
                continue
            default = dict(t=0, r=0, s=1)[trs]
            attr.set(default)
    for attr in ctrl.listAttr(ud=1):
        if pm.addAttr(attr, q=1, at=1) != "double":
            continue
        if attr.inputs():
            continue
        if attr.isLocked():
            continue
        default = pm.addAttr(attr, q=1, dv=1)
        attr.set(default)


def get_ib_by_targets(ib_names):
    for ib_name in ib_names:
        match = re.match(".+_IB([0-9]{2})$", ib_name)
        if match is None:
            continue
        ib = int(match.groups()[0])
        return ib
    return 60


def set_pose_by_targets(target_names, ib=60):
    orig_ib = get_ib_by_targets(target_names)
    target_names = [name for target_name in target_names for name in re.split("_COMB_|_IB[0-9]{2}", target_name) if name]
    bridge = get_bridge()
    ctrl_lists = []
    attr_value_list = []
    for target_name in get_targets():
        if not bridge.hasAttr(target_name):
            continue
        uu = bridge.attr(target_name).inputs(type="animCurveUU")
        if len(uu) != 1:
            continue
        uu = uu[0]
        attr = uu.inputs(p=1)
        if len(attr) != 1:
            continue
        attr = attr[0]
        ctrl = attr.node()
        if ctrl.type() == "unitConversion":
            attr = ctrl.inputs(p=1)
            if len(attr) != 1:
                continue
            attr = attr[0]
            ctrl = attr.node()
        if ctrl not in ctrl_lists:
            ctrl_lists.append(ctrl)
        if target_name not in target_names:
            continue
        if target_name[-4:] == "_max":
            value = pm.keyframe(uu, floatChange=1, q=1, index=1)[0]
        else:
            value = pm.keyframe(uu, floatChange=1, q=1, index=0)[0]
        attr_value_list.append([attr, value])
    for ctrl in ctrl_lists:
        rest_ctrl(ctrl)
    for attr, value in attr_value_list:
        attr.set(value*float(orig_ib)/60.0*float(ib)/60.0)


def get_targets():
    if not pm.objExists("CtrlAttrBsSdkBridge"):
        return []
    return [attr.name(includeNode=False) for attr in get_bridge().listAttr(ud=1)]


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


def edit_target(target_name):
    selected = get_selected_polygons()
    if len(selected) != 2:
        return pm.warning("please selected two polygon")
    bridge = get_bridge()
    if not bridge.hasAttr(target_name):
        return pm.warning("can not find " + target_name)
    src, dst = selected
    attr = bridge.attr(target_name)
    bs.bridge_connect_edit(attr, src, dst)


def edit_static_target(target_name):
    selected = get_selected_polygons()
    if len(selected) != 2:
        return pm.warning("please selected two polygon")
    bridge = get_bridge()
    if not bridge.hasAttr(target_name):
        return pm.warning("can not find " + target_name)
    src, dst = selected
    attr = bridge.attr(target_name)
    bs.bridge_static_connect_edit(attr, src, dst)


def add_comb(target_names):
    comb_name = "_COMB_".join(list(sorted(target_names)))
    bridge = get_bridge()
    if bridge.hasAttr(comb_name):
        return pm.warning(comb_name + " already exists")
    for target_name in target_names:
        if not bridge.hasAttr(target_name):
            return pm.warning("can not find " + target_name)
        if not bridge.inputs():
            return pm.warning("can not find " + target_name + "inputs")
    bridge.addAttr(comb_name, min=0, max=1, at="double", k=1)
    com = pm.createNode("combinationShape", n=comb_name)
    com.outputWeight.connect(bridge.attr(comb_name))
    com.combinationMethod.set(1)
    for i, target_name in enumerate(target_names):
        bridge.attr(target_name).inputs(p=1)[0].connect(com.inputWeight[i])


def update_ib(target_name):
    bridge = get_bridge()
    if not bridge.hasAttr(target_name):
        return pm.warning("can not find" + target_name)
    ibs = []
    for ib_name in get_targets():
        match = re.match(target_name+"_IB([0-9]{2})$", ib_name)
        if match is None:
            continue
        ib = int(match.groups()[0])
        ibs.append(ib)
    ibs = list(sorted(ibs))
    ibs = [0] + ibs + [60]
    for i in range(len(ibs)-2):
        ib_name = target_name + "_IB%02d" % ibs[i+1]
        pm.delete(bridge.attr(ib_name).inputs())
        for dv, v in zip([1.0/60.0*ibs[i+j] for j in range(3)], [0, 1, 0]):
            pm.setDrivenKeyframe(bridge.attr(ib_name), cd=bridge.attr(target_name), dv=dv, v=v, itt="linear", ott="linear")


def _add_ib(bridge, target_name, ib):
    ib_name = target_name + "_IB%02d" % ib
    if bridge.hasAttr(ib_name):
        return pm.warning(target_name + " already exists")
    bridge.addAttr(ib_name, min=0, max=1, at="double", k=1)
    update_ib(target_name)
    return ib_name


def add_ib(target_name):
    bridge = get_bridge()
    if re.match(".+_IB[0-9]{2}$", target_name):
        return pm.warning("can not insert in-between")
    if not bridge.hasAttr(target_name):
        return pm.warning("can not find" + target_name)
    attr = bridge.attr(target_name)
    value = attr.get()
    ib = int(round(value * 60))
    if ib == 60:
        return pm.warning("can not insert ib-between 60")
    if ib == 0:
        return pm.warning("can not insert ib-between 0")
    _add_ib(bridge, target_name, ib)


def delete_target(target_name):
    bridge = get_bridge()
    if not bridge.hasAttr(target_name):
        return pm.warning("can not find" + target_name)
    for bs_node in bridge.attr(target_name).outputs(type="blendShape"):
        bs.delete_target(bs_node.attr(target_name))
    pm.deleteAttr(bridge.attr(target_name))
    match = re.match("(.+)_IB[0-9]{2}$", target_name)
    if match is None:
        return
    update_ib(match.groups()[0])


def delete_targets(target_names):
    for target_name in target_names:
        delete_target(target_name)


def reset_face_ctrl():
    for ctrl in pm.ls("FCtrl*", "*Control", type="transform"):
        if "FaceGroup" not in ctrl.fullPath():
            continue
        rest_ctrl(ctrl)


def face_sdk(target_name):
    sel = pm.selected()
    target = pm.ls("*|Planes|Target", type="transform")
    driver = pm.ls("*|Planes|Driver", type="transform")
    if len(target) != 1:
        return pm.warning("can not find target")
    if len(driver) != 1:
        return pm.warning("can not find driver")
    temp = target[0].duplicate()[0]
    pm.select(temp, driver[0])
    reset_face_ctrl()
    set_pose_by_targets([target_name])
    edit_static_target(target_name)
    pm.select(sel)
    pm.delete(temp)


def find_mirror_ctrl(ctrl):
    ctrl_list = pm.ls(config.get_rl_names(ctrl.name().split("|")[-1].split(":")[-1]))
    if len(ctrl_list) != 1:
        return
    return ctrl_list[0]


def add_mirror_base_target(bridge, target_name):
    uu = bridge.attr(target_name).inputs(type="animCurveUU")
    if len(uu) != 1:
        return
    uu = uu[0]
    attr = uu.inputs(p=1)
    if len(attr) != 1:
        return
    attr = attr[0]
    ctrl = attr.node()
    if ctrl.type() == "unitConversion":
        attr = ctrl.inputs(p=1)
        if len(attr) != 1:
            return
        attr = attr[0]
        ctrl = attr.node()
    if target_name[-4:] == "_max":
        value = pm.keyframe(uu, floatChange=1, q=1, index=1)[0]
        default_value = pm.keyframe(uu, floatChange=1, q=1, index=0)[0]
    else:
        value = pm.keyframe(uu, floatChange=1, q=1, index=0)[0]
        default_value = pm.keyframe(uu, floatChange=1, q=1, index=1)[0]
    mirror_ctrl = find_mirror_ctrl(ctrl)
    if mirror_ctrl is None:
        return
    attr = mirror_ctrl.attr(attr.name(includeNode=False))
    target_name = get_target_name(attr, default_value, value)
    if not bridge.hasAttr(target_name):
        add_sdk(attr, target_name, default_value, value)
    return target_name


def add_mirror_target(bridge, target_name):
    math = re.match("(.+)_IB([0-9]{2})$", target_name)
    if math:
        target_name = math.groups()[0]
        ib = int(math.groups()[1])
    else:
        ib = None
    target_names = [name for name in target_name.split("_COMB_") if name]
    mirror_target_names = []
    for target_name in target_names:
        mirror_target_name = add_mirror_base_target(bridge, target_name)
        if mirror_target_name is None:
            continue
        mirror_target_names.append(mirror_target_name)
    mirror_target_names = list(sorted(mirror_target_names))
    if len(mirror_target_names) > 1:
        add_comb(mirror_target_names)
        mirror_target_name = "_COMB_".join(mirror_target_names)
    else:
        mirror_target_name = mirror_target_names[0]
    if ib is None:
        return mirror_target_name
    return _add_ib(bridge, mirror_target_name, ib)


def mirror_targets(target_names):
    polygons = get_selected_polygons()
    driver = pm.ls("*|Planes|Driver", type="transform")
    if len(driver) == 1:
        polygons.append(driver[0])
    bridge = get_bridge()
    target_mirrors = []
    for target_name in target_names:
        if not bridge.hasAttr(target_name):
            continue
        mirror_target_name = add_mirror_target(bridge, target_name)
        target_mirrors.append([target_name, mirror_target_name])
    for polygon in polygons:
        _bs = bs.get_bs(polygon)
        for src, dst in target_mirrors:
            if not _bs.hasAttr(src):
                continue
            if _bs.hasAttr(dst):
                continue
            bs.bridge_connect(bridge.attr(dst), polygon)
        bs.mirror_targets(polygon, target_mirrors)
