# coding:utf-8
from maya.OpenMaya import *
import pymel.core as pm
from maya import cmds
import os


def load_ocd_plug():
    version = int(round(float(pm.about(q=1, v=1))))
    path = os.path.abspath(__file__+"/../plug-ins/maya%04d/ocd.mll" % version)
    if not os.path.isfile(path):
        return pm.warning("can not find ocd")
    if not pm.pluginInfo(path, q=1, l=1):
        pm.loadPlugin(path)
    path = os.path.abspath(__file__+"/../plug-ins/maya%04d/SSDR2.mll" % version)
    if not os.path.isfile(path):
        return pm.warning("can not find sdr")
    if not pm.pluginInfo(path, q=1, l=1):
        pm.loadPlugin(path)


def get_fn_mesh_by_name(name):
    selection_list = MSelectionList()
    selection_list.add(name)
    dag_path = MDagPath()
    selection_list.getDagPath(0, dag_path)
    fn_mesh = MFnMesh(dag_path)
    return fn_mesh


def get_polygon_points_by_name(name, points):
    fn_mesh = get_fn_mesh_by_name(name)
    fn_mesh.getPoints(points)


def set_polygon_points_by_name(name, points):
    fn_mesh = get_fn_mesh_by_name(name)
    fn_mesh.setPoints(points)


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


def matrix_set_data(matrix, data):
    for i in range(4):
        for j in range(4):
            MScriptUtil.setDoubleArray(matrix[i], j, data[i][j])


def init_bs_target_points(bs, index):
    fn_component_list = MFnComponentListData()
    component_data = fn_component_list.create()
    fn_points = MFnPointArrayData()
    phy_points = MPointArray()
    points_data = fn_points.create(phy_points)
    ipt, ict = get_bs_ipt_ict(bs.name(), index)
    ict.setMObject(component_data)
    ipt.setMObject(points_data)


def get_bs_ids_points(polygon, name):
    ids = MIntArray()
    points = MPointArray()
    bs = get_bs(polygon)
    if not bs.hasAttr(name):
        return ids, points
    index = bs.attr(name).logicalIndex()
    ipt, ict = get_bs_ipt_ict(bs.name(), index)
    fn_component_list = MFnComponentListData(ict.asMObject())
    for i in range(fn_component_list.length()):
        fn_component = MFnSingleIndexedComponent(fn_component_list[i])
        _ids = MIntArray()
        fn_component.getElements(_ids)
        for j in range(_ids.length()):
            ids.append(_ids[j])
    fn_points = MFnPointArrayData(ipt.asMObject())
    fn_points.copyTo(points)
    return ids, points


def set_bs_ids_points(polygon, name, ids, points):
    bs = get_bs(polygon)
    add_target(polygon, name)
    index = bs.attr(name).logicalIndex()
    ipt, ict = get_bs_ipt_ict(bs.name(), index)
    fn_component = MFnSingleIndexedComponent()
    fn_component_obj = fn_component.create(MFn.kMeshVertComponent)
    fn_component.addElements(ids)
    fn_component_list = MFnComponentListData()
    fn_component_list_obj = fn_component_list.create()
    fn_component_list.add(fn_component_obj)
    fn_points = MFnPointArrayData()
    fn_points_obj = fn_points.create(points)
    ict.setMObject(fn_component_list_obj)
    ipt.setMObject(fn_points_obj)


def test_copy_bs():
    src = pm.PyNode("pSphere2")
    dst = pm.PyNode("pSphere3")
    name = "pSphere1"
    ids, points = get_bs_ids_points(src, name)
    set_bs_ids_points(dst, name, ids, points)


# -----------------


def is_polygon(polygon):
    if polygon.type() != "transform":
        return False
    shape = polygon.getShape()
    if not shape:
        return False
    if shape.type() != "mesh":
        return False
    return True


def get_child_polygons(group):
    polygons = group.listRelatives(ad=1, type="transform")
    polygons.insert(0, group)
    return [poly for poly in polygons if is_polygon(poly)]


def get_name_polygon_by_hierarchy(group):
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


def get_polygon_matrix_by_root(*roots):
    return get_polygon_matrix_by_map([get_name_polygon_by_hierarchy(root) for root in roots])


def get_name_polygon_by_short_name(polygons):
    return {polygon.name().split("|")[-1]:polygon for polygon in polygons}


def get_polygon_matrix_by_polygons(*polygons):
    return get_polygon_matrix_by_map([get_name_polygon_by_short_name(poly) for poly in polygons])


def get_polygon_matrix_by_map(name_polygons):
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
            if not shape.outputs(type="groupParts"):
                pm.delete(shape)
    for shape in polygon.getShapes():
        if shape.io.get():
            if shape.outputs(type="groupParts"):
                return shape


def edit_target(target, base, name):
    bs = get_bs(base)
    if not bs.hasAttr(name):
        return
    index = bs.attr(name).logicalIndex()
    orig = get_orig(base)
    cmds.edit_target(bs.name(), index, target.name(), base.name(), orig.name())


def bridge_connect(attr, dst):
    name = attr.name(includeNode=False)
    add_target(dst, name)
    bs = get_bs(dst)
    if bs.attr(name) not in attr.outputs(p=1):
        attr.connect(bs.attr(name), f=1)


def bridge_connect_edit(attr, src, dst):
    bridge_connect(attr, dst)
    edit_target(src, dst, attr.name(includeNode=False))


def edit_static_target(target, base, name):
    bs = get_bs(base)
    if not bs.hasAttr(name):
        return
    index = bs.attr(name).logicalIndex()
    orig = base.getShape()
    cmds.edit_no_skin_target(bs.name(), index, target.name(), base.name(), orig.name())


def bridge_static_connect_edit(attr, src, dst):
    bridge_connect(attr, dst)
    edit_static_target(src, dst, attr.name(includeNode=False))


def get_mirror_data(polygon):
    for shape in polygon.getShapes():
        if shape.io.get():
            box = shape.boundingBox()
            box = list(box[0]) + list(box[1])
            center = [(box[i] + box[3 + i]) / 2.0 for i in range(3)]
            size = max([abs(box[i] - box[3 + i]) / 2.0 for i in range(3)])
            return shape, center, size


def mirror_targets(polygon, names):
    bs = get_bs(polygon)
    src_indexes = []
    dst_indexes = []
    for src, dst in names:
        if not bs.hasAttr(src):
            continue
        if not bs.hasAttr(dst):
            continue
        src_indexes.append(bs.attr(src).logicalIndex())
        dst_indexes.append(bs.attr(dst).logicalIndex())
    orig, center, size = get_mirror_data(polygon)
    cmds.mirror_target(orig.name(), bs.name(), src_indexes, dst_indexes)


def check_mirror():
    polygons = set(mesh.getParent() for mesh in pm.ls(type="mesh"))
    pm.select(polygons)
    cmds.mirror_check()


load_ocd_plug()
