import maya.cmds as mc


def create_eyelid_joints_on_curve(crv, eye_joint, up_obj):
    """

    :param crv:
    :param eye_joint:
    :param up_obj:
    :return:
    """
    nam = crv[4:-4]
    grp_jnts = mc.group(n='grp_{}Jns_001'.format(nam), w=1, em=1)
    grp_nodes = mc.group(n='grp_{}RigNodes_001'.format(nam), w=1, em=1)
    grp_drive_attach = mc.group(n='grp_{}Attaches_001'.format(nam))

    mc.parent(crv, grp_nodes)

    crv_shape = mc.listRelatives(crv, s=1)[0]
    spans = mc.getAttr(crv_shape+'.spans')
    degree = mc.getAttr(crv_shape+'.degree')
    crv_cvNum = spans+degree

    for i in range(crv_cvNum):
        jnt = mc.createNode('joint', n='jnt_{}_{:03d}'.format(nam, i+1))
        mc.setAttr(jnt+'.radius', 0.2)
        pos = mc.xform('{}.cv[{}]'.format(crv, i), q=1, t=1, ws=1)
        mc.xform(jnt, t=pos, ws=1)

        npoc = mc.createNode('nearestPointOnCurve')
        mc.connectAttr(crv_shape+'.worldSpace[0]', npoc+'.inputCurve')
        mc.connectAttr(jnt+'.t', npoc+'.inPosition')
        parameter = mc.getAttr(npoc+'.parameter')
        mc.delete(npoc)

        attach = mc.group(n='grp_{}Attach_{:03d}'.format(nam, i+1), p=grp_drive_attach, em=1)
        poci = mc.createNode('pointOnCurveInfo', n=attach.replace('grp_', 'poci_'))
        mc.connectAttr(crv_shape+'.worldSpace[0]', poci+'.inputCurve')
        mc.setAttr(poci+'.parameter', parameter)
        mc.connectAttr(poci+'.position', attach+'.t')

        grp_aim = mc.group(n='grp_{}Aim_{:03d}'.format(nam, i+1), p=grp_jnts, em=1)
        mc.matchTransform(grp_aim, eye_joint, pos=1)
        mc.aimConstraint(attach, grp_aim, aim=(1, 0, 0), u=(0, 1, 0), wut='objectrotation', wuo=up_obj, wu=(0, 1, 0),
                         mo=0)

        mc.parent(jnt, grp_aim)
        mc.matchTransform(jnt, grp_aim, rot=1)
        mc.makeIdentity(jnt, a=1, t=1, r=1, s=1)


