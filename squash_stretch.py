"""Squash & Stretch Rigging Tool for Autodesk Maya.

Automates modular, volume-preserving squash and stretch setups across any
character rig or joint chain. Fully cycle-free, topology-agnostic, and
multi-character compatible.

Author: Alfredo M.
Course: Programming for Animators - Research Project 1
Environment: Maya 2027 / Python 3
"""

import math
from typing import List, Optional, Tuple
import maya.cmds as cmds


# -----------------------------------------------------------------------------
# Metadata & Tagging Constants
# -----------------------------------------------------------------------------
META_NODE_TYPE = "network"
META_TAG_ATTR = "isSquashStretchMeta"
META_TARGET_ATTR = "ssTargetJoints"
META_NODES_ATTR = "ssCreatedNodes"


def _ensure_plugin(plugin_name: str = "matrixNodes") -> None:
    """Ensure required Maya plugins are loaded (e.g. matrixNodes)."""
    if not cmds.pluginInfo(plugin_name, query=True, loaded=True):
        try:
            cmds.loadPlugin(plugin_name)
        except Exception as err:
            cmds.warning(f"Failed to load plugin {plugin_name}: {err}")


def _create_node(node_type: str, name: str) -> str:
    """Create a Maya node, preferring Maya 2027+ short types (addDL, multDL) with fallback."""
    aliases = {
        "addDoubleLinear": "addDL",
        "multDoubleLinear": "multDL",
    }
    target_type = aliases.get(node_type, node_type)
    try:
        return cmds.createNode(target_type, name=name)
    except Exception:
        return cmds.createNode(node_type, name=name)


def calculate_distance(node_a: str, node_b: str) -> float:
    """Calculate the Euclidean distance between two nodes in world space."""
    pos_a = cmds.xform(node_a, query=True, worldSpace=True, translation=True)
    pos_b = cmds.xform(node_b, query=True, worldSpace=True, translation=True)
    return math.sqrt(
        (pos_a[0] - pos_b[0]) ** 2
        + (pos_a[1] - pos_b[1]) ** 2
        + (pos_a[2] - pos_b[2]) ** 2
    )


def add_animator_attributes(ctrl: str) -> None:
    """Add user-facing squash & stretch control attributes to a rig controller."""
    if not cmds.attributeQuery("squashStretchDivider", node=ctrl, exists=True):
        cmds.addAttr(
            ctrl,
            longName="squashStretchDivider",
            niceName="--- S & S ---",
            attributeType="enum",
            enumName="------",
            keyable=False,
        )
        cmds.setAttr(f"{ctrl}.squashStretchDivider", channelBox=True)

    attrs = [
        ("squashStretch", "Squash & Stretch", "float", 0.0, 1.0, 1.0),
        ("volumeFactor", "Volume Factor", "float", 0.0, 5.0, 1.0),
        ("minSquash", "Min Squash Limit", "float", 0.01, 1.0, 0.2),
        ("maxStretch", "Max Stretch Limit", "float", 1.0, 10.0, 3.0),
        ("stretchOffset", "Stretch Offset", "float", -5.0, 5.0, 0.0),
    ]

    for long_n, nice_n, attr_type, min_v, max_v, def_v in attrs:
        if not cmds.attributeQuery(long_n, node=ctrl, exists=True):
            kwargs = {
                "longName": long_n,
                "niceName": nice_n,
                "attributeType": attr_type,
                "defaultValue": def_v,
                "keyable": True,
            }
            if min_v is not None:
                kwargs["minValue"] = min_v
            if max_v is not None:
                kwargs["maxValue"] = max_v
            cmds.addAttr(ctrl, **kwargs)


def build_squash_stretch(
    start_driver: str,
    end_driver: str,
    target_joints: List[str],
    ctrl_for_attrs: Optional[str] = None,
    primary_axis: str = "Y",
    prefix: str = "ss",
    rest_length: Optional[float] = None,
) -> dict:
    """Build a cycle-free, volume-preserving squash and stretch node network.

    Parameters
    ----------
    start_driver : str
        The root transform/joint/locator defining the origin of the distance.
    end_driver : str
        The tip/handle transform/joint/locator defining the stretch distance.
    target_joints : list of str
        The joints or transforms whose scales will be modulated by the system.
    ctrl_for_attrs : str, optional
        The controller where animator attributes will be placed (defaults to end_driver).
    primary_axis : str
        The primary axis of bone stretch ('X', 'Y', or 'Z'). Default is 'Y'.
    prefix : str
        Prefix for naming created utility nodes.
    rest_length : float, optional
        Pre-calculated rest distance. If None, measured automatically.

    Returns
    -------
    dict
        Dictionary containing references to created nodes and metadata.
    """
    _ensure_plugin("matrixNodes")
    primary_axis = primary_axis.upper()
    if primary_axis not in ("X", "Y", "Z"):
        raise ValueError(f"Primary axis must be 'X', 'Y', or 'Z', got: {primary_axis}")

    if not cmds.objExists(start_driver):
        raise ValueError(f"Start driver does not exist: {start_driver}")
    if not cmds.objExists(end_driver):
        raise ValueError(f"End driver does not exist: {end_driver}")
    for jnt in target_joints:
        if not cmds.objExists(jnt):
            raise ValueError(f"Target joint does not exist: {jnt}")

    ctrl = ctrl_for_attrs or end_driver
    add_animator_attributes(ctrl)

    # Calculate rest distance
    measured_rest = calculate_distance(start_driver, end_driver)
    if rest_length is None or rest_length <= 0.0001:
        rest_length = measured_rest
    if rest_length <= 0.0001:
        rest_length = 1.0  # Guard against division by zero

    cmds.undoInfo(openChunk=True, chunkName=f"Build_SquashStretch_{prefix}")
    created_nodes = []

    try:
        # 1. World Matrix Decomposition to avoid cyclic scene graph dependencies
        start_decomp = cmds.createNode("decomposeMatrix", name=f"{prefix}_start_decompMatrix")
        end_decomp = cmds.createNode("decomposeMatrix", name=f"{prefix}_end_decompMatrix")
        created_nodes.extend([start_decomp, end_decomp])

        cmds.connectAttr(f"{start_driver}.worldMatrix[0]", f"{start_decomp}.inputMatrix", force=True)
        cmds.connectAttr(f"{end_driver}.worldMatrix[0]", f"{end_decomp}.inputMatrix", force=True)

        # 2. Distance Between Node
        dist_node = cmds.createNode("distanceBetween", name=f"{prefix}_distBetween")
        created_nodes.append(dist_node)
        cmds.connectAttr(f"{start_decomp}.outputTranslate", f"{dist_node}.point1", force=True)
        cmds.connectAttr(f"{end_decomp}.outputTranslate", f"{dist_node}.point2", force=True)

        # Optional user stretch offset addition
        add_offset_node = _create_node("addDoubleLinear", name=f"{prefix}_addOffset_ADL")
        created_nodes.append(add_offset_node)
        cmds.connectAttr(f"{dist_node}.distance", f"{add_offset_node}.input1", force=True)
        cmds.connectAttr(f"{ctrl}.stretchOffset", f"{add_offset_node}.input2", force=True)

        # 3. Ratio Calculation (Current Distance / Rest Length)
        ratio_md = cmds.createNode("multiplyDivide", name=f"{prefix}_ratio_MD")
        created_nodes.append(ratio_md)
        cmds.setAttr(f"{ratio_md}.operation", 2)  # Divide
        cmds.connectAttr(f"{add_offset_node}.output", f"{ratio_md}.input1X", force=True)
        cmds.setAttr(f"{ratio_md}.input2X", rest_length)

        # 4. Clamping (Clamp stretch ratio between minSquash and maxStretch)
        clamp_node = cmds.createNode("clamp", name=f"{prefix}_stretch_clamp")
        created_nodes.append(clamp_node)
        cmds.connectAttr(f"{ctrl}.minSquash", f"{clamp_node}.minR", force=True)
        cmds.connectAttr(f"{ctrl}.maxStretch", f"{clamp_node}.maxR", force=True)
        cmds.connectAttr(f"{ratio_md}.outputX", f"{clamp_node}.inputR", force=True)

        # 5. Volume Preservation Math: S_secondary = S ^ (-0.5 * volumeFactor)
        # 5a. Exponent multiplier: -0.5 * volumeFactor
        exp_mdl = _create_node("multDoubleLinear", name=f"{prefix}_volumeExp_MDL")
        created_nodes.append(exp_mdl)
        cmds.connectAttr(f"{ctrl}.volumeFactor", f"{exp_mdl}.input1", force=True)
        cmds.setAttr(f"{exp_mdl}.input2", -0.5)

        # 5b. Power node: clamp.outputR ^ exp_mdl.output
        volume_pow_md = cmds.createNode("multiplyDivide", name=f"{prefix}_volumePow_MD")
        created_nodes.append(volume_pow_md)
        cmds.setAttr(f"{volume_pow_md}.operation", 3)  # Power
        cmds.connectAttr(f"{clamp_node}.outputR", f"{volume_pow_md}.input1X", force=True)
        cmds.connectAttr(f"{exp_mdl}.output", f"{volume_pow_md}.input2X", force=True)

        # 6. Master Blend Colors (Blends between normal 1.0 scale and squash/stretch scale)
        scale_blend = cmds.createNode("blendColors", name=f"{prefix}_scale_blendColors")
        created_nodes.append(scale_blend)
        cmds.connectAttr(f"{ctrl}.squashStretch", f"{scale_blend}.blender", force=True)

        # Default rest scale = (1.0, 1.0, 1.0)
        cmds.setAttr(f"{scale_blend}.color2R", 1.0)
        cmds.setAttr(f"{scale_blend}.color2G", 1.0)
        cmds.setAttr(f"{scale_blend}.color2B", 1.0)

        # Map axes based on primary axis
        # Primary axis gets clamp_node.outputR
        # Secondary axes get volume_pow_md.outputX
        if primary_axis == "X":
            cmds.connectAttr(f"{clamp_node}.outputR", f"{scale_blend}.color1R", force=True)
            cmds.connectAttr(f"{volume_pow_md}.outputX", f"{scale_blend}.color1G", force=True)
            cmds.connectAttr(f"{volume_pow_md}.outputX", f"{scale_blend}.color1B", force=True)
        elif primary_axis == "Y":
            cmds.connectAttr(f"{volume_pow_md}.outputX", f"{scale_blend}.color1R", force=True)
            cmds.connectAttr(f"{clamp_node}.outputR", f"{scale_blend}.color1G", force=True)
            cmds.connectAttr(f"{volume_pow_md}.outputX", f"{scale_blend}.color1B", force=True)
        elif primary_axis == "Z":
            cmds.connectAttr(f"{volume_pow_md}.outputX", f"{scale_blend}.color1R", force=True)
            cmds.connectAttr(f"{volume_pow_md}.outputX", f"{scale_blend}.color1G", force=True)
            cmds.connectAttr(f"{clamp_node}.outputR", f"{scale_blend}.color1B", force=True)

        # 7. Connect to target joints
        for jnt in target_joints:
            cmds.connectAttr(f"{scale_blend}.outputR", f"{jnt}.scaleX", force=True)
            cmds.connectAttr(f"{scale_blend}.outputG", f"{jnt}.scaleY", force=True)
            cmds.connectAttr(f"{scale_blend}.outputB", f"{jnt}.scaleZ", force=True)

        # 8. Tagging Meta Node for clean tracking and removal
        meta_node = cmds.createNode(META_NODE_TYPE, name=f"{prefix}_SS_Meta")
        cmds.addAttr(meta_node, longName=META_TAG_ATTR, attributeType="bool", defaultValue=True)
        cmds.addAttr(meta_node, longName=META_TARGET_ATTR, dataType="string")
        cmds.addAttr(meta_node, longName=META_NODES_ATTR, dataType="string")
        cmds.addAttr(meta_node, longName="ctrlForAttrs", dataType="string")
        cmds.addAttr(meta_node, longName="restLength", attributeType="float", defaultValue=rest_length)
        cmds.addAttr(meta_node, longName="primaryAxis", dataType="string")

        cmds.setAttr(f"{meta_node}.{META_TARGET_ATTR}", ",".join(target_joints), type="string")
        cmds.setAttr(f"{meta_node}.{META_NODES_ATTR}", ",".join(created_nodes), type="string")
        cmds.setAttr(f"{meta_node}.ctrlForAttrs", ctrl, type="string")
        cmds.setAttr(f"{meta_node}.primaryAxis", primary_axis, type="string")

        # Connect meta node to controller
        if not cmds.attributeQuery("ssMetaNode", node=ctrl, exists=True):
            cmds.addAttr(ctrl, longName="ssMetaNode", attributeType="message")
        cmds.connectAttr(f"{meta_node}.message", f"{ctrl}.ssMetaNode", force=True)

        result = {
            "meta_node": meta_node,
            "controller": ctrl,
            "target_joints": target_joints,
            "rest_length": rest_length,
            "primary_axis": primary_axis,
            "created_nodes": created_nodes,
            "ratio_node": ratio_md,
            "clamp_node": clamp_node,
            "scale_blend": scale_blend,
        }
        return result

    finally:
        cmds.undoInfo(closeChunk=True)


def remove_squash_stretch(ctrl_or_meta: str) -> bool:
    """Remove a squash and stretch setup cleanly and restore joint scales."""
    if not cmds.objExists(ctrl_or_meta):
        cmds.warning(f"Object does not exist: {ctrl_or_meta}")
        return False

    meta_node = ctrl_or_meta
    if cmds.attributeQuery("ssMetaNode", node=ctrl_or_meta, exists=True):
        conn = cmds.listConnections(f"{ctrl_or_meta}.ssMetaNode", destination=False, source=True)
        if conn:
            meta_node = conn[0]

    if not cmds.attributeQuery(META_TAG_ATTR, node=meta_node, exists=True):
        cmds.warning(f"No Squash & Stretch metadata found on {ctrl_or_meta}")
        return False

    cmds.undoInfo(openChunk=True, chunkName="Remove_SquashStretch")
    try:
        targets_str = cmds.getAttr(f"{meta_node}.{META_TARGET_ATTR}") or ""
        nodes_str = cmds.getAttr(f"{meta_node}.{META_NODES_ATTR}") or ""
        ctrl_str = cmds.getAttr(f"{meta_node}.ctrlForAttrs") or ""

        target_joints = [t.strip() for t in targets_str.split(",") if t.strip()]
        created_nodes = [n.strip() for n in nodes_str.split(",") if n.strip()]

        # Disconnect and reset scale on target joints
        for jnt in target_joints:
            if cmds.objExists(jnt):
                for axis in ("X", "Y", "Z"):
                    conns = cmds.listConnections(f"{jnt}.scale{axis}", source=True, destination=False, plugs=True)
                    if conns:
                        cmds.disconnectAttr(conns[0], f"{jnt}.scale{axis}")
                    cmds.setAttr(f"{jnt}.scale{axis}", 1.0)

        # Delete created utility nodes
        for node in created_nodes:
            if cmds.objExists(node):
                cmds.delete(node)

        # Remove attributes from controller if requested
        if ctrl_str and cmds.objExists(ctrl_str):
            for attr in ("squashStretchDivider", "squashStretch", "volumeFactor", "minSquash", "maxStretch", "stretchOffset", "ssMetaNode"):
                if cmds.attributeQuery(attr, node=ctrl_str, exists=True):
                    cmds.deleteAttr(f"{ctrl_str}.{attr}")

        # Delete meta node
        if cmds.objExists(meta_node):
            cmds.delete(meta_node)

        return True
    finally:
        cmds.undoInfo(closeChunk=True)


def connect_blendshape_driver(
    meta_or_ctrl: str,
    blendshape_node: str,
    squash_target_name: Optional[str] = None,
    stretch_target_name: Optional[str] = None,
    multiplier: float = 1.0,
    prefix: str = "ss_bs",
) -> dict:
    """Connect squash and stretch delta drivers into Maya blendshape target weights.

    Parameters
    ----------
    meta_or_ctrl : str
        The controller or meta node containing the setup.
    blendshape_node : str
        The Maya blendshape node name.
    squash_target_name : str, optional
        Name of the squash target shape attribute (e.g. 'squash_wide').
    stretch_target_name : str, optional
        Name of the stretch target shape attribute (e.g. 'stretch_long').
    multiplier : float
        Sensitivity multiplier for blendshape weight activation.
    prefix : str
        Prefix for created driver nodes.

    Returns
    -------
    dict
        Created driver nodes.
    """
    if not cmds.objExists(blendshape_node):
        raise ValueError(f"Blendshape node does not exist: {blendshape_node}")

    meta_node = meta_or_ctrl
    if cmds.attributeQuery("ssMetaNode", node=meta_or_ctrl, exists=True):
        conn = cmds.listConnections(f"{meta_or_ctrl}.ssMetaNode", destination=False, source=True)
        if conn:
            meta_node = conn[0]

    nodes_str = cmds.getAttr(f"{meta_node}.{META_NODES_ATTR}") or ""
    created_nodes = [n.strip() for n in nodes_str.split(",") if n.strip()]

    # Find the ratio node
    clamp_node = None
    for n in created_nodes:
        if cmds.nodeType(n) == "clamp":
            clamp_node = n
            break

    if not clamp_node:
        raise RuntimeError("Could not find clamp node from Squash & Stretch setup.")

    drivers = {}

    # Squash driver: activates when S < 1.0 -> weight = clamp(0, 1, (1.0 - S) * multiplier)
    if squash_target_name and cmds.attributeQuery(squash_target_name, node=blendshape_node, exists=True):
        squash_sub = cmds.createNode("plusMinusAverage", name=f"{prefix}_squashDelta_PMA")
        cmds.setAttr(f"{squash_sub}.operation", 2)  # Subtract: input3D[0] - input3D[1]
        cmds.setAttr(f"{squash_sub}.input1D[0]", 1.0)
        cmds.connectAttr(f"{clamp_node}.outputR", f"{squash_sub}.input1D[1]", force=True)

        squash_mult = _create_node("multDoubleLinear", name=f"{prefix}_squashMult_MDL")
        cmds.connectAttr(f"{squash_sub}.output1D", f"{squash_mult}.input1", force=True)
        cmds.setAttr(f"{squash_mult}.input2", multiplier)

        squash_clamp = cmds.createNode("clamp", name=f"{prefix}_squashBS_clamp")
        cmds.setAttr(f"{squash_clamp}.minR", 0.0)
        cmds.setAttr(f"{squash_clamp}.maxR", 1.0)
        cmds.connectAttr(f"{squash_mult}.output", f"{squash_clamp}.inputR", force=True)

        cmds.connectAttr(f"{squash_clamp}.outputR", f"{blendshape_node}.{squash_target_name}", force=True)
        drivers["squash"] = [squash_sub, squash_mult, squash_clamp]

    # Stretch driver: activates when S > 1.0 -> weight = clamp(0, 1, (S - 1.0) * multiplier)
    if stretch_target_name and cmds.attributeQuery(stretch_target_name, node=blendshape_node, exists=True):
        stretch_sub = cmds.createNode("plusMinusAverage", name=f"{prefix}_stretchDelta_PMA")
        cmds.setAttr(f"{stretch_sub}.operation", 2)  # Subtract
        cmds.connectAttr(f"{clamp_node}.outputR", f"{stretch_sub}.input1D[0]", force=True)
        cmds.setAttr(f"{stretch_sub}.input1D[1]", 1.0)

        stretch_mult = _create_node("multDoubleLinear", name=f"{prefix}_stretchMult_MDL")
        cmds.connectAttr(f"{stretch_sub}.output1D", f"{stretch_mult}.input1", force=True)
        cmds.setAttr(f"{stretch_mult}.input2", multiplier)

        stretch_clamp = cmds.createNode("clamp", name=f"{prefix}_stretchBS_clamp")
        cmds.setAttr(f"{stretch_clamp}.minR", 0.0)
        cmds.setAttr(f"{stretch_clamp}.maxR", 1.0)
        cmds.connectAttr(f"{stretch_mult}.output", f"{stretch_clamp}.inputR", force=True)

        cmds.connectAttr(f"{stretch_clamp}.outputR", f"{blendshape_node}.{stretch_target_name}", force=True)
        drivers["stretch"] = [stretch_sub, stretch_mult, stretch_clamp]

    return drivers


# -----------------------------------------------------------------------------
# 1-Click Interactive Test Rig Generator
# -----------------------------------------------------------------------------
def create_test_rig(rig_type: str = "bouncing_ball") -> dict:
    """Generate a clean, self-contained test rig in Maya with geometry and controllers.

    Types supported:
        - 'bouncing_ball': Stylized cartoon bouncing ball with root + stretch handle.
        - 'cartoon_limb': 3-joint cartoon leg/arm with IK handle and stretch.
    """
    cmds.file(new=True, force=True)

    if rig_type == "bouncing_ball":
        # 1. Base sphere
        sphere = cmds.polySphere(radius=2.0, subdivisionsX=24, subdivisionsY=24, name="test_ball_geo")[0]
        cmds.move(0, 2.0, 0, sphere)

        # 2. Skeleton
        cmds.select(clear=True)
        root_jnt = cmds.joint(name="ball_root_jnt", position=(0, 0, 0))
        center_jnt = cmds.joint(name="ball_center_jnt", position=(0, 2.0, 0))
        top_jnt = cmds.joint(name="ball_top_jnt", position=(0, 4.0, 0))

        # Skin sphere to center_jnt
        skin = cmds.skinCluster(center_jnt, sphere, name="ball_skinCluster", toSelectedBones=True)[0]

        # 3. Controls
        root_ctrl = cmds.circle(normal=(0, 1, 0), radius=3.0, name="ball_root_ctrl")[0]
        cmds.move(0, 0, 0, root_ctrl)

        top_ctrl = cmds.circle(normal=(0, 1, 0), radius=1.5, name="ball_stretch_ctrl")[0]
        cmds.move(0, 4.0, 0, top_ctrl)

        # Parent constraint root_jnt to root_ctrl
        cmds.parentConstraint(root_ctrl, root_jnt, maintainOffset=True)

        # Point constraint top_jnt to top_ctrl
        cmds.pointConstraint(top_ctrl, top_jnt, maintainOffset=True)

        # 4. Apply Squash & Stretch
        ss_result = build_squash_stretch(
            start_driver=root_ctrl,
            end_driver=top_ctrl,
            target_joints=[center_jnt],
            ctrl_for_attrs=top_ctrl,
            primary_axis="Y",
            prefix="ball_ss",
            rest_length=4.0,
        )

        cmds.select(top_ctrl)
        return {
            "type": "bouncing_ball",
            "geo": sphere,
            "root_ctrl": root_ctrl,
            "top_ctrl": top_ctrl,
            "center_jnt": center_jnt,
            "setup": ss_result,
        }

    elif rig_type == "cartoon_limb":
        # 3-joint leg / arm
        cmds.select(clear=True)
        hip_jnt = cmds.joint(name="limb_hip_jnt", position=(0, 6.0, 0))
        knee_jnt = cmds.joint(name="limb_knee_jnt", position=(0, 3.0, 0.3))
        ankle_jnt = cmds.joint(name="limb_ankle_jnt", position=(0, 0.0, 0))
        cmds.joint(hip_jnt, edit=True, orientJoint="xyz", secondaryAxisOrient="yup", children=True)

        # Cylinder mesh
        cyl = cmds.polyCylinder(radius=0.8, height=6.0, subdivisionsY=12, name="limb_geo")[0]
        cmds.move(0, 3.0, 0, cyl)
        cmds.skinCluster([hip_jnt, knee_jnt, ankle_jnt], cyl, name="limb_skinCluster")

        # IK RP solver
        ik_handle = cmds.ikHandle(startJoint=hip_jnt, endEffector=ankle_jnt, solver="ikRPsolver", name="limb_ikHandle")[0]

        # Ankle controller
        foot_ctrl = cmds.circle(normal=(0, 1, 0), radius=1.8, name="limb_foot_ctrl")[0]
        cmds.move(0, 0, 0, foot_ctrl)
        cmds.parent(ik_handle, foot_ctrl)

        # Hip controller
        hip_ctrl = cmds.circle(normal=(0, 1, 0), radius=2.0, name="limb_hip_ctrl")[0]
        cmds.move(0, 6.0, 0, hip_ctrl)
        cmds.parentConstraint(hip_ctrl, hip_jnt, maintainOffset=True)

        # Apply Squash & Stretch across hip and knee joints
        ss_result = build_squash_stretch(
            start_driver=hip_ctrl,
            end_driver=foot_ctrl,
            target_joints=[hip_jnt, knee_jnt],
            ctrl_for_attrs=foot_ctrl,
            primary_axis="X",
            prefix="limb_ss",
            rest_length=6.0,
        )

        cmds.select(foot_ctrl)
        return {
            "type": "cartoon_limb",
            "geo": cyl,
            "hip_ctrl": hip_ctrl,
            "foot_ctrl": foot_ctrl,
            "setup": ss_result,
        }

    else:
        raise ValueError(f"Unknown rig type: {rig_type}")


# -----------------------------------------------------------------------------
# Quick Maya UI
# -----------------------------------------------------------------------------
def show_ui() -> None:
    """Display the Squash & Stretch Rigging Tool UI inside Maya."""
    win_id = "MayaSquashStretchToolUI"
    if cmds.window(win_id, exists=True):
        cmds.deleteUI(win_id)

    win = cmds.window(win_id, title="Maya Squash & Stretch Tool", widthHeight=(360, 420), resizeToFitChildren=True)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6, columnOffset=("both", 10))

    cmds.text(label="SQUASH & STRETCH RIGGER", font="boldLabelFont", height=30)
    cmds.separator(height=10, style="in")

    cmds.text(label="Step 1: Driver Selection", align="left", font="boldLabelFont")
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(90, 160, 70), adjustableColumn=2)
    cmds.text(label="Start Driver:")
    start_field = cmds.textField("ss_start_field")
    cmds.button(label="< Set", command=lambda *_: _load_selected_into_field(start_field))
    cmds.setParent("..")

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(90, 160, 70), adjustableColumn=2)
    cmds.text(label="End Driver:")
    end_field = cmds.textField("ss_end_field")
    cmds.button(label="< Set", command=lambda *_: _load_selected_into_field(end_field))
    cmds.setParent("..")

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(90, 160, 70), adjustableColumn=2)
    cmds.text(label="Attr Ctrl:")
    ctrl_field = cmds.textField("ss_ctrl_field")
    cmds.button(label="< Set", command=lambda *_: _load_selected_into_field(ctrl_field))
    cmds.setParent("..")

    cmds.separator(height=10, style="in")
    cmds.text(label="Step 2: Target Joints & Axis", align="left", font="boldLabelFont")
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(90, 160, 70), adjustableColumn=2)
    cmds.text(label="Target Joints:")
    target_field = cmds.textField("ss_target_field")
    cmds.button(label="< Set", command=lambda *_: _load_selected_into_field(target_field, multi=True))
    cmds.setParent("..")

    axis_menu = cmds.optionMenuGrp(label="Primary Axis:", columnWidth=(1, 90))
    cmds.menuItem(label="X")
    cmds.menuItem(label="Y")
    cmds.menuItem(label="Z")
    cmds.optionMenuGrp(axis_menu, edit=True, value="Y")

    prefix_field = cmds.textFieldGrp(label="Prefix:", text="ss", columnWidth=(1, 90))

    cmds.separator(height=10, style="in")

    def _on_build(*_):
        start = cmds.textField(start_field, query=True, text=True).strip()
        end = cmds.textField(end_field, query=True, text=True).strip()
        ctrl = cmds.textField(ctrl_field, query=True, text=True).strip() or end
        targets = [t.strip() for t in cmds.textField(target_field, query=True, text=True).split(",") if t.strip()]
        axis = cmds.optionMenuGrp(axis_menu, query=True, value=True)
        pfx = cmds.textFieldGrp(prefix_field, query=True, text=True).strip() or "ss"

        if not start or not end or not targets:
            cmds.warning("Please specify Start Driver, End Driver, and at least one Target Joint!")
            return

        build_squash_stretch(
            start_driver=start,
            end_driver=end,
            target_joints=targets,
            ctrl_for_attrs=ctrl,
            primary_axis=axis,
            prefix=pfx,
        )
        cmds.inViewMessage(amg=f"Squash & Stretch setup built on <hl>{', '.join(targets)}</hl>!", pos="topCenter", fade=True)

    def _on_remove(*_):
        sel = cmds.ls(selection=True)
        if not sel:
            cmds.warning("Select the controller or meta node to remove.")
            return
        if remove_squash_stretch(sel[0]):
            cmds.inViewMessage(amg="Squash & Stretch setup removed cleanly.", pos="topCenter", fade=True)

    cmds.button(label="BUILD SQUASH & STRETCH", backgroundColor=(0.2, 0.5, 0.3), height=35, command=_on_build)
    cmds.button(label="REMOVE SELECTED SETUP", backgroundColor=(0.5, 0.2, 0.2), height=28, command=_on_remove)

    cmds.separator(height=12, style="in")
    cmds.text(label="Testing & Demos", align="left", font="boldLabelFont")
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(170, 170))
    cmds.button(label="Create Bouncing Ball Test", command=lambda *_: create_test_rig("bouncing_ball"))
    cmds.button(label="Create Cartoon Limb Test", command=lambda *_: create_test_rig("cartoon_limb"))
    cmds.setParent("..")

    cmds.showWindow(win)


def _load_selected_into_field(field_name: str, multi: bool = False) -> None:
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Nothing selected in viewport.")
        return
    text = ", ".join(sel) if multi else sel[0]
    cmds.textField(field_name, edit=True, text=text)
