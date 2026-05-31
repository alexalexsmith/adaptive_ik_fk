"""
IK FK utilities
"""
from maya import cmds
import maya.api.OpenMaya as om

from adaptive_ik_fk.utilities import math_utils


# NOTE: these are the names for advanced skeleton IK FK nodes
IKFK_ARM_NODES = ("FKIKArm", "Shoulder", "Elbow", "Wrist", "PoleArm", "Arm")
IKFK_LEG_NODES = ("FKIKLeg", "Hip", "PoleLeg", "Leg", "Knee", "Ankle")
ARM_FK_SNAP_NODES = ("Shoulder", "Elbow", "Wrist")
LEG_FK_SNAP_NODES = ("Hip", "Knee", "Ankle")
IK_CONTROLS = ("PoleArm", "IKArm", "PoleLeg", "IKLeg")
FK_CONTROLS = ("FKShoulder", "FKElbow", "FKWrist", "FKHip", "FKKnee", "FKAnkle")
SIDES = ("L", "R", "M")


def match_ik_fk(node):
    """
    Match the ik or fk depending on what node is given
    """
    if not get_snap_nodes(node):
        return
    for control in IK_CONTROLS:
        if control in node:
            match_fk_to_ik(node)
            break
    for control in FK_CONTROLS:
        if control in node:
            match_ik_to_fk(node)
            break


def match_to_current_interpolation_setting(node):
    """
    Match the node's ik or fk system to the active interpolation system. If the node's system is active do nothing
    """
    snap_nodes = get_snap_nodes(node)
    if not snap_nodes:
        return
    switch_plug = get_switch_plug(node)
    if not switch_plug:
        return
    if cmds.getAttr(switch_plug) == 10:
        match_fk_to_ik(node)
    if cmds.getAttr(switch_plug) == 0:
        match_ik_to_fk(node)


def match_ik_to_fk(node):
    """
    Match ik controls to fk controls position
    """
    side = get_side(node)
    if not side:
        cmds.warning("Unable to get side")
        return

    ik_matrix_offset_dict = get_ik_matrix_offset_dict(node, side)

    if not ik_matrix_offset_dict:
        cmds.warning("Unable to get ik controls for switch")
        return

    # match ik control
    offset_mmatrix = om.MMatrix(ik_matrix_offset_dict["ik_matrix"])
    parent_world_matrix = om.MMatrix(
        cmds.xform(ik_matrix_offset_dict["ik_control_snap_bone"], q=True, matrix=True, ws=True))
    paste_matrix = offset_mmatrix * parent_world_matrix
    cmds.xform(ik_matrix_offset_dict["ik_control"], matrix=list(paste_matrix), ws=True)
    cmds.setKeyframe(ik_matrix_offset_dict["ik_control"])

    # match pole vector control
    offset_mmatrix = om.MMatrix(ik_matrix_offset_dict["pole_matrix"])
    parent_world_matrix = om.MMatrix(
        cmds.xform(ik_matrix_offset_dict["pole_control_snap_bone"], q=True, matrix=True, ws=True))
    paste_matrix = offset_mmatrix * parent_world_matrix
    cmds.xform(ik_matrix_offset_dict["pole_control"], matrix=list(paste_matrix), ws=True)
    #cmds.setKeyframe(ik_matrix_offset_dict["pole_control"])


def match_fk_to_ik(node):
    """
    Match fk controls to ik controls position
    """
    fk_snap_nodes = get_snap_nodes(node)

    if not fk_snap_nodes:
        cmds.warning("select an IK or FK control")
        return

    side = get_side(node)
    if not side:
        cmds.warning("Unable to get side")
        return

    namespace = ""
    if get_namespace(node):
        namespace = f"{get_namespace(node)}:"

    for snap_node in fk_snap_nodes:
        ctrl_name = f"{namespace}FK{snap_node}_{side}"
        snap_position_node_name = f"{namespace}IKX{snap_node}_{side}"
        snap_to_matrix = cmds.xform(snap_position_node_name, query=True, matrix=True, ws=True)
        cmds.xform(ctrl_name, matrix=list(snap_to_matrix), ws=True)
        #cmds.setKeyframe(ctrl_name)


def get_switch_plug(node):
    """
    Get the IKFK switch plug path
    """
    switch_plug = None
    for snap_node in IKFK_ARM_NODES:
        if snap_node in node:
            switch_plug = IKFK_ARM_NODES[0]

    for snap_node in IKFK_LEG_NODES:
        if snap_node in node:
            switch_plug = IKFK_LEG_NODES[0]
    if switch_plug is None:
        return None
    namespace = get_namespace(node)
    side = get_side(node)
    return f"{namespace}:{switch_plug}_{side}.FKIKBlend"


def get_snap_nodes(node):
    """
    Get the list of snap nodes based on the passed node. e.g. arm snap nodes
    """
    for snap_node in IKFK_ARM_NODES:
        if snap_node in node:
            return ARM_FK_SNAP_NODES

    for snap_node in IKFK_LEG_NODES:
        if snap_node in node:
            return LEG_FK_SNAP_NODES
    return None


def get_side(node):
    """
    Get the side string assigned to the control
    """
    for side in SIDES:
        if node.endswith(side):
            return side
    return None


def get_namespace(node):
    """
    Get the namespace of the node
    """
    if ":" not in node:
        return None
    return node.rsplit(":", 1)[0]


def get_ik_matrix_offset_dict(node, side):
    """
    :param str node: name of node belonging to IK/FK system
    """
    # Figure out which controls to use

    # assuming there is always a namespace
    namespace = get_namespace(node)
    # Get what type of ik system it is and grab the controls
    ik_chain_bone = None
    ik_pole_bone = None
    ik_control = None
    pole_control = None
    ik_control_snap_bone = None
    pole_control_snap_bone = None

    for snap_node in IKFK_ARM_NODES:
        if snap_node in node:
            ik_chain_bone = "{0}:IKXWrist_{1}".format(namespace, side)
            ik_pole_bone = "{0}:IKXElbow_{1}".format(namespace, side)
            ik_control = "{0}:IKArm_{1}".format(namespace, side)
            pole_control = "{0}:PoleArm_{1}".format(namespace, side)
            ik_control_snap_bone = "{0}:FKWrist_{1}".format(namespace, side)
            pole_control_snap_bone = "{0}:FKElbow_{1}".format(namespace, side)
            break

    for snap_node in IKFK_LEG_NODES:
        if snap_node in node:
            ik_chain_bone = "{0}:IKXAnkle_{1}".format(namespace, side)
            ik_pole_bone = "{0}:IKXKnee_{1}".format(namespace, side)
            ik_control = "{0}:IKLeg_{1}".format(namespace, side)
            pole_control = "{0}:PoleLeg_{1}".format(namespace, side)
            ik_control_snap_bone = "{0}:FKAnkle_{1}".format(namespace, side)
            pole_control_snap_bone = "{0}:FKKnee_{1}".format(namespace, side)
            break

    for node_name in [ik_chain_bone, ik_pole_bone, ik_control, pole_control, ik_control_snap_bone,
                      pole_control_snap_bone]:
        if not node_name:
            return None

    # Build dict
    ik_snap_matrix_dict = {"ik_matrix": math_utils.get_matrices_offset_dict(ik_chain_bone, ik_control),
                           "pole_matrix": math_utils.get_matrices_offset_dict(ik_pole_bone, pole_control),
                           "ik_control": ik_control, "pole_control": pole_control,
                           "ik_control_snap_bone": ik_control_snap_bone,
                           "pole_control_snap_bone": pole_control_snap_bone}

    return ik_snap_matrix_dict

