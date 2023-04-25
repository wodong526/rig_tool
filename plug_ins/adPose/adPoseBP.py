import unreal
import re
import math

@unreal.uclass()
class getContentBrowser(unreal.GlobalEditorUtilityBase):
    pass


def get_selected_asset():
    editor_util = getContentBrowser()
    return editor_util.get_selected_assets()


def get_selected_skeletal_mesh():
    for sel in get_selected_asset():
        if isinstance(sel, unreal.SkeletalMesh):
            return sel


def create_rbf_bp(skeletal_mesh):
    factory = unreal.ControlRigBlueprintFactory()
    return factory.create_control_rig_from_skeletal_mesh_or_skeleton(skeletal_mesh)


def get_ad_pose_data(control_rig_bp):
    # get joints and targets
    joints = []
    targets = []
    hierarchy_modifier = control_rig_bp.get_hierarchy_modifier()
    elem_keys = hierarchy_modifier.get_elements()
    for elem_key in elem_keys:
        typ = elem_key.get_editor_property("type")
        name = str(elem_key.get_editor_property("name"))
        if typ == unreal.RigElementType.CURVE:
            targets.append(name)
        elif typ == unreal.RigElementType.BONE:
            bone = hierarchy_modifier.get_bone(elem_key)
            transform = bone.get_editor_property("local_transform")
            joints.append(name)
    # re joint ad
    joint_ads = dict()
    for curve in targets:
        match = re.match(r"^(?P<joint>\w+)_a(?P<a>[0-9]{1,3})_d(?P<d>[0-9]{1,3})$", curve)
        if not match:
            continue
        group_dict = match.groupdict()
        joint = group_dict["joint"]
        if joint not in joints:
            continue
        joint_ads.setdefault(group_dict["joint"], set()).add((int(group_dict["a"]), int(group_dict["d"])))
    return joint_ads


def graph_info(controller):
    graph = controller.get_graph()
    for node in graph.get_select_nodes():
        node = graph.find_node_by_name(node)
        # print(node.get_pins())
        # pin = node.find_pin("curve")
        # print(pin)
        # value = "(EditorCurveData=(Keys=((Time=0,Value=0),(Time=0.5,Value=1),(Time=1,Value=0))))"
        # controller.set_pin_default_value(pin.get_pin_path(), value)
        # print(type(node))
        # print(node)
        print(node.get_script_struct())
        print(node.get_method_name())
        print(node.get_struct_default_value())
        # print(node.get_node_path())


def create_struct_node(controller, cls, i, j):
    size = 400
    node = controller.add_struct_node(
        script_struct=getattr(unreal, cls)().static_struct(),
        method_name="Execute",
        position=[size*j, size*i],
        node_name=cls)
    return node


def create_if_node(controller, typ, i, j):
    size = 400
    path = controller.get_path_name().split(":")[0]+":RigVMModel"
    return controller.add_if_node(typ, path, [size*j, size*i], "if")


def create_angle_direction(controller, joint, i):
    bone = create_struct_node(controller, "RigUnit_GetTransform", i+0, 0)
    initial = create_struct_node(controller, "RigUnit_GetTransform", i+1, 0)

    rotate = create_struct_node(controller, "RigUnit_MathQuaternionRotateVector", i + 0, 1)
    mul = create_struct_node(controller, "RigUnit_MathQuaternionMul", i + 1, 1)
    inverse = create_struct_node(controller, "RigUnit_MathQuaternionInverse", i + 2, 1)

    greater = create_struct_node(controller, "RigUnit_MathFloatGreater", i + 1, 2)
    direction = create_struct_node(controller, "RigUnit_MathVectorAngle", i + 2, 2)

    angle = create_struct_node(controller, "RigUnit_MathVectorAngle", i + 0, 3)
    condition = create_if_node(controller, "float",  i + 1, 3)
    sub = create_struct_node(controller, "RigUnit_MathFloatSub", i + 2, 3)

    angle_scale = create_struct_node(controller, "RigUnit_MathFloatDiv", i + 0, 4)
    direction_scale = create_struct_node(controller, "RigUnit_MathFloatDiv", i + 1, 4)

    controller.add_link(bone.find_pin("Transform.Rotation").get_pin_path(),
                        mul.find_pin("A").get_pin_path())
    controller.add_link(initial.find_pin("Transform.Rotation").get_pin_path(),
                        inverse.find_pin("Value").get_pin_path())
    controller.add_link(inverse.find_pin("Result").get_pin_path(),
                        mul.find_pin("B").get_pin_path())

    controller.add_link(mul.find_pin("Result").get_pin_path(),
                        rotate.find_pin("Quaternion").get_pin_path())

    controller.add_link(rotate.find_pin("Result").get_pin_path(),
                        angle.find_pin("A").get_pin_path())
    controller.add_link(rotate.find_pin("Result.Y").get_pin_path(),
                        direction.find_pin("A.Y").get_pin_path())
    controller.add_link(rotate.find_pin("Result.Z").get_pin_path(),
                        direction.find_pin("A.Z").get_pin_path())
    controller.add_link(rotate.find_pin("Result.Z").get_pin_path(),
                        greater.find_pin("A").get_pin_path())

    controller.add_link(greater.find_pin("Result").get_pin_path(),
                        condition.find_pin("Condition").get_pin_path())
    controller.add_link(direction.find_pin("Result").get_pin_path(),
                        sub.find_pin("B").get_pin_path())
    controller.add_link(sub.find_pin("Result").get_pin_path(),
                        condition.find_pin("False").get_pin_path())
    controller.add_link(direction.find_pin("Result").get_pin_path(),
                        condition.find_pin("True").get_pin_path())

    controller.add_link(angle.find_pin("Result").get_pin_path(),
                        angle_scale.find_pin("A").get_pin_path())
    controller.add_link(condition.find_pin("Result").get_pin_path(),
                        direction_scale.find_pin("A").get_pin_path())

    controller.set_pin_default_value(bone.find_pin("Item.Type").get_pin_path(), "Bone")
    controller.set_pin_default_value(bone.find_pin("Item.Name").get_pin_path(), joint)
    controller.set_pin_default_value(bone.find_pin("Space").get_pin_path(), "LocalSpace")
    controller.set_pin_default_value(initial.find_pin("Item.Type").get_pin_path(), "Bone")
    controller.set_pin_default_value(initial.find_pin("Item.Name").get_pin_path(), joint)
    controller.set_pin_default_value(initial.find_pin("Space").get_pin_path(), "LocalSpace")
    controller.set_pin_default_value(initial.find_pin("bInitial").get_pin_path(), "true")

    controller.set_pin_default_value(rotate.find_pin("Vector.X").get_pin_path(), "1.0")
    controller.set_pin_default_value(angle.find_pin("B.X").get_pin_path(), "1.0")
    controller.set_pin_default_value(direction.find_pin("B.Y").get_pin_path(), "-1.0")
    controller.set_pin_default_value(sub.find_pin("A").get_pin_path(), "%.6f" % (math.pi*2))

    controller.set_pin_default_value(angle_scale.find_pin("B").get_pin_path(), "%.6f" % (math.pi*2))
    controller.set_pin_default_value(direction_scale.find_pin("B").get_pin_path(), "%.6f" % (math.pi*2))
    return angle_scale, direction_scale


def create_sdk(controller, i, j, key_value):
    node = create_struct_node(controller, "RigUnit_AnimEvalRichCurve", i, j)
    curve_data = ",".join("(Time=%06f,Value=%.6f)" % (key, value) for key, value in key_value)
    value = "(EditorCurveData=(Keys=(%s)))" % curve_data
    controller.set_pin_default_value(node.find_pin("curve").get_pin_path(), value)
    # controller.set_pin_default_value(node.find_pin("SourceMinimum").get_pin_path(), "0")
    # controller.set_pin_default_value(node.find_pin("SourceMaximum").get_pin_path(), "%.6f"%math.pi*2)
    return node


def create_direction_sdk(controller, i, j, ds, d, direction):
    ds = sorted(set(sum([[_d, _d+360, _d-360] for _d in ds] + [[d+90, d-90]], [])))
    key_value = {ds[ds.index(d)+o1]+o2*360: v for o1, v in zip([-1, 0, 1], [0, 1, 0]) for o2 in [-1, 0, 1]}
    key_value = [[key/360.0, key_value[key]] for key in sorted(key_value.keys())]
    d_sdk = create_sdk(controller, i, j, key_value)
    controller.add_link(direction.find_pin("Result").get_pin_path(),
                        d_sdk.find_pin("Value").get_pin_path())
    return i+1, d_sdk


def create_angle_sdk(controller, i, j, _as, a, a_sdk_dict, angle):
    _as = sorted(_as+[180, 0])
    key_value = [[_as[_as.index(a)+o], v] for o, v in zip([-1, 0, 1], [0, 1, 0])]
    if key_value[2][0] == 180:
        key_value[2][1] = 1
    key_value = [[k/360.0, v] for k, v in key_value]
    keys = tuple(k for k, v in key_value)
    if keys in a_sdk_dict:
        return i, a_sdk_dict[keys]
    a_sdk = create_sdk(controller, i, j, key_value)
    controller.add_link(angle.find_pin("Result").get_pin_path(),
                        a_sdk.find_pin("Value").get_pin_path())
    a_sdk_dict[keys] = a_sdk
    return i+1, a_sdk


def create_ad_pose_bp_by_selected():
    skeletal_mesh = get_selected_skeletal_mesh()
    if skeletal_mesh is None:
        return
    rbf_bp = create_rbf_bp(skeletal_mesh)
    controller = rbf_bp.get_editor_property("controller")
    # rbf_bp = get_selected_asset()[0]
    # controller = rbf_bp.get_editor_property("controller")
    data = get_ad_pose_data(rbf_bp)
    begin = create_struct_node(controller, "RigUnit_BeginExecution", -1, 8)
    execute = begin.find_pin("ExecuteContext").get_pin_path()

    graph_info(controller)
    i = 0
    for joint, ads in data.items():
        angle, direction = create_angle_direction(controller, joint, i)
        d_a_dict = {}
        for a, d in ads:
            d_a_dict.setdefault(d, []).append(a)
        ds = d_a_dict.keys()
        a_sdk_dict = {}
        k = -0.5
        for d, _as in d_a_dict.items():
            i, d_sdk = create_direction_sdk(controller, i, 5, ds, d, direction)
            for a in _as:
                i, a_sdk = create_angle_sdk(controller, i, 5, _as, a, a_sdk_dict, angle)
                k += 0.5
                mul = create_struct_node(controller, "RigUnit_MathFloatMul", k, 7)
                curve = create_struct_node(controller, "RigUnit_SetCurveValue", k, 8)
                controller.add_link(a_sdk.find_pin("Result").get_pin_path(),
                                    mul.find_pin("A").get_pin_path())
                controller.add_link(d_sdk.find_pin("Result").get_pin_path(),
                                    mul.find_pin("B").get_pin_path())
                controller.add_link(mul.find_pin("Result").get_pin_path(),
                                    curve.find_pin("Value").get_pin_path())
                name = "{joint}_a{a}_d{d}".format(**locals())
                controller.set_pin_default_value(curve.find_pin("Curve").get_pin_path(), name)
                controller.add_link(execute, curve.find_pin("ExecuteContext").get_pin_path())
                execute = curve.find_pin("ExecuteContext").get_pin_path()
        direction_sdk_dict = {}


def create_lush_node(cls):
    ctrl_bp = get_selected_asset()[0]
    controller = ctrl_bp.get_editor_property("controller")
    i = 0
    j = 0
    size = 400
    return controller.add_struct_node(
        script_struct=getattr(unreal, cls)().static_struct(),
        method_name="Execute",
        position=[size * j, size * i],
        node_name=cls)

