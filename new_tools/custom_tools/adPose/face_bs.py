# coding:utf-8
from maya.OpenMaya import *
import pymel.core as pm
from maya import cmds
import os


def is_polygon(polygon):
    if polygon.type() != "transform":
        return False
    shape = polygon.getShape()
    if not shape:
        return False
    if shape.type() != "mesh":
        return False
    return True


def get_name_polygon(group):
    data = {}
    polygons = group.listRelatives(ad=1, type="transform")
    polygons.insert(0, group)
    length = len(group.fullPath()) + 1
    for polygon in polygons:
        name = "|" + polygon.fullPath()[length:]
        if not is_polygon(polygon):
            continue
        data[name] = polygon
    return data


def get_polygon_matrix(*roots):
    name_polygons = [get_name_polygon(root) for root in roots]
    polygon_matrix = []
    for name in name_polygons[0].keys():
        polygons = [name_polygon.get(name, None) for name_polygon in name_polygons]
        if None in polygons:
            continue
        polygon_matrix.append(polygons)
    return polygon_matrix


def get_bs(polygon):
    bs = polygon.listHistory(type="blendShape")
    if bs:
        bs = bs[0]
    else:
        try:
            bs = pm.blendShape(polygon, automatic=True, n=polygon.name().split("|")[-1] + "_bs")[0]
        except TypeError:
            dup = polygon.duplicate()[0]
            bs = pm.blendShape(dup, polygon, frontOfChain=1, n=polygon.name().split("|")[-1] + "_bs")[0]
            pm.delete(dup)
            delete_target(bs.weight[0])
    return bs


def get_bs_ipt_ict(bs, index):
    selection_list = MSelectionList()
    selection_list.add(bs)
    depend_node = MObject()
    selection_list.getDependNode(0, depend_node)
    fn_depend_node = MFnDependencyNode(depend_node)
    iti = fn_depend_node.findPlug("it").elementByLogicalIndex(0).child(0).elementByLogicalIndex(index).child(0).\
        elementByLogicalIndex(6000)
    ipt = iti.child(3)
    ict = iti.child(4)
    return ipt, ict


def init_bs_target_points(bs, index):
    fn_component_list = MFnComponentListData()
    component_data = fn_component_list.create()
    fn_points = MFnPointArrayData()
    phy_points = MPointArray()
    points_data = fn_points.create(phy_points)
    ipt, ict = get_bs_ipt_ict(bs.name(), index)
    ict.setMObject(component_data)
    ipt.setMObject(points_data)


def add_target(polygon, name):
    bs = get_bs(polygon)
    if bs.hasAttr(name):
        return
    ids = [bs.weight.elementByPhysicalIndex(i).logicalIndex() for i in range(bs.weight.numElements())]
    index = -1
    while True:
        index += 1
        if index not in ids:
            break
    bs.weight[index].set(1)
    pm.aliasAttr(name, bs.weight[index])
    init_bs_target_points(bs, index)


def delete_target(weight_attr):
    index = weight_attr.logicalIndex()
    bs = weight_attr.node()
    pm.removeMultiInstance(weight_attr, b=1)
    pm.removeMultiInstance(bs.it[0].itg[index], b=1)


def get_orig(polygon):
    for shape in polygon.getShapes():
        if shape.io.get():
            return shape


def edit_bridge_target(attr, src, dst):
    name = attr.name(includeNode=False)
    bs = get_bs(dst)
    if not bs.hasAttr(name):
        add_target(dst, name)
        attr.connect(bs.attr(name))
    index = bs.attr(name).logicalIndex()
    orig = get_orig(dst)
    cmds.edit_no_skin_target(bs.name(), index, src.name(), orig.name())


def edit_bridge_targets(attr, src, dst):
    for src, dst in get_polygon_matrix(src, dst):
        print src, dst
        edit_bridge_target(attr, src, dst)


def load_ocd_plug():
    version = int(round(float(pm.about(q=1, v=1))))
    path = os.path.abspath(__file__+"/../ocd/maya%04d/ocd.mll" % version)
    if not os.path.isfile(path):
        return pm.warning("can not find ocd")
    if not pm.pluginInfo("ocd", q=1, l=1):
        pm.loadPlugin(path)


def auto_edit_bridge_targets(bridge, src, dst):
    load_ocd_plug()
    bridge = pm.PyNode(bridge)
    src = pm.PyNode(src)
    dst = pm.PyNode(dst)
    attr_list = [attr for attr in bridge.listAttr(ud=1) if attr.get() ==1]
    if len(attr_list) != 1:
        return pm.warning("no one bridge attr")
    edit_bridge_targets(attr_list[0], src, dst)


def auto_mirror_bridge_targets(bridge, group, src, dst):
    load_ocd_plug()
    bridge = pm.PyNode(bridge)
    group = pm.PyNode(group)
    attr_list = [attr for attr in bridge.listAttr(ud=1) if attr.get() == 1 and src in attr.name(includeNode=False)]
    for polygon in get_name_polygon(group).values():
        src_indexes, dst_indexes = [], []
        bs = get_bs(polygon)
        for attr in attr_list:
            src_name = attr.name(includeNode=False)
            if src_name[-len(src):] != src:
                continue
            dst_name = src_name[:-len(src)] + dst
            if not bs.hasAttr(dst_name):
                add_target(polygon, dst_name)
                bridge.attr(dst_name).connect(bs.attr(dst_name))
            src_indexes.append(bs.attr(src_name).logicalIndex())
            dst_indexes.append(bs.attr(dst_name).logicalIndex())
        orig = get_orig(polygon)
        cmds.mirror_target(orig.name(), bs.name(), src_indexes, dst_indexes)
