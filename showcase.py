"""Multi-Character Showcase and Dynamic Test Animation Generator.

Demonstrates the Squash & Stretch Rigging Tool across multiple character
components simultaneously (Bouncing Ball with BlendShapes, 3-Joint IK Limb,
and 4-Joint Cartoon Spine) with fully keyframed animation across 120 frames.

Author: Alfredo M.
Course: Programming for Animators - Research Project 1
Environment: Maya 2027 / Python 3
"""

import math
import pathlib
import maya.cmds as cmds
import squash_stretch as ss


def build_multi_character_showcase() -> dict:
    """Build a complete 3-character side-by-side showcase scene with keyframed animation."""
    cmds.file(new=True, force=True)
    cmds.undoInfo(openChunk=True, chunkName="Build_Showcase_Animation")

    try:
        # Configure viewport and playback timeline
        cmds.playbackOptions(minTime=1, maxTime=120, animationStartTime=1, animationEndTime=120)
        cmds.playbackOptions(playbackSpeed=1.0)  # Realtime 24 fps
        cmds.currentTime(1)

        # ---------------------------------------------------------------------
        # Ground Grid & Lighting Setup
        # ---------------------------------------------------------------------
        ground = cmds.polyPlane(width=30, height=20, subdivisionsX=15, subdivisionsY=10, name="showcase_ground")[0]
        cmds.move(0, 0, 0, ground)
        cmds.setAttr(f"{ground}.receiveShadows", 1)

        # ---------------------------------------------------------------------
        # Character 1: Cartoon Ball with Live BlendShapes (Left, X = -7)
        # ---------------------------------------------------------------------
        c1_group = cmds.group(empty=True, name="char1_ball_grp")
        cmds.move(-7, 0, 0, c1_group)

        # Base sphere
        c1_sphere = cmds.polySphere(radius=1.8, subdivisionsX=24, subdivisionsY=24, name="c1_ball_geo")[0]
        cmds.move(-7, 2.0, 0, c1_sphere)
        cmds.parent(c1_sphere, c1_group)

        # BlendShape targets
        c1_squash_tgt = cmds.duplicate(c1_sphere, name="c1_squash_target")[0]
        cmds.setAttr(f"{c1_squash_tgt}.scaleX", 1.55)
        cmds.setAttr(f"{c1_squash_tgt}.scaleY", 0.35)
        cmds.setAttr(f"{c1_squash_tgt}.scaleZ", 1.55)
        cmds.makeIdentity(c1_squash_tgt, apply=True, scale=True)
        cmds.setAttr(f"{c1_squash_tgt}.visibility", 0)

        c1_stretch_tgt = cmds.duplicate(c1_sphere, name="c1_stretch_target")[0]
        cmds.setAttr(f"{c1_stretch_tgt}.scaleX", 0.55)
        cmds.setAttr(f"{c1_stretch_tgt}.scaleY", 2.3)
        cmds.setAttr(f"{c1_stretch_tgt}.scaleZ", 0.55)
        cmds.makeIdentity(c1_stretch_tgt, apply=True, scale=True)
        cmds.setAttr(f"{c1_stretch_tgt}.visibility", 0)

        c1_bs = cmds.blendShape(c1_squash_tgt, c1_stretch_tgt, c1_sphere, name="c1_blendShape")[0]

        # Joints
        cmds.select(clear=True)
        c1_root_jnt = cmds.joint(name="c1_root_jnt", position=(-7, 0, 0))
        c1_center_jnt = cmds.joint(name="c1_center_jnt", position=(-7, 2.0, 0))
        c1_top_jnt = cmds.joint(name="c1_top_jnt", position=(-7, 4.0, 0))
        cmds.parent(c1_root_jnt, c1_group)

        cmds.skinCluster(c1_center_jnt, c1_sphere, name="c1_skinCluster", toSelectedBones=True)

        # Controls
        c1_root_ctrl = cmds.circle(normal=(0, 1, 0), radius=2.6, name="c1_root_ctrl")[0]
        cmds.move(-7, 0, 0, c1_root_ctrl)
        cmds.parent(c1_root_ctrl, c1_group)

        c1_top_ctrl = cmds.circle(normal=(0, 1, 0), radius=1.4, name="c1_stretch_ctrl")[0]
        cmds.move(-7, 4.0, 0, c1_top_ctrl)
        cmds.parent(c1_top_ctrl, c1_group)

        cmds.parentConstraint(c1_root_ctrl, c1_root_jnt, maintainOffset=True)
        cmds.pointConstraint(c1_top_ctrl, c1_top_jnt, maintainOffset=True)

        ss.build_squash_stretch(
            start_driver=c1_root_ctrl,
            end_driver=c1_top_ctrl,
            target_joints=[c1_center_jnt],
            ctrl_for_attrs=c1_top_ctrl,
            primary_axis="Y",
            prefix="c1_ss",
            rest_length=4.0,
        )

        ss.connect_blendshape_driver(
            meta_or_ctrl=c1_top_ctrl,
            blendshape_node=c1_bs,
            squash_target_name="c1_squash_target",
            stretch_target_name="c1_stretch_target",
            multiplier=1.2,
            prefix="c1_bs_drv",
        )

        # Keyframe Character 1 (Ball Bounce with Impact Squash & Apex Stretch)
        ball_keys = [
            (1, 4.0),    # Rest
            (15, 1.3),   # Anticipation Squash
            (28, 8.5),   # Explosive Upward Stretch
            (48, 6.5),   # Float at Apex
            (62, 1.1),   # Heavy Ground Impact
            (76, 5.2),   # Rebound Stretch
            (90, 1.8),   # Second Impact
            (105, 4.3),  # Settle Wobble
            (120, 4.0),  # Clean Rest Loop
        ]
        for f, val in ball_keys:
            cmds.setKeyframe(f"{c1_top_ctrl}.translateY", time=f, value=val)

        # ---------------------------------------------------------------------
        # Character 2: Cartoon 3-Joint IK Leg/Arm (Center, X = 0)
        # ---------------------------------------------------------------------
        c2_group = cmds.group(empty=True, name="char2_limb_grp")
        cmds.move(0, 0, 0, c2_group)

        cmds.select(clear=True)
        c2_hip_jnt = cmds.joint(name="c2_hip_jnt", position=(0, 6.0, 0))
        c2_knee_jnt = cmds.joint(name="c2_knee_jnt", position=(0, 3.0, 0.3))
        c2_ankle_jnt = cmds.joint(name="c2_ankle_jnt", position=(0, 0.0, 0))
        cmds.joint(c2_hip_jnt, edit=True, orientJoint="xyz", secondaryAxisOrient="yup", children=True)
        cmds.parent(c2_hip_jnt, c2_group)

        c2_cyl = cmds.polyCylinder(radius=0.75, height=6.0, subdivisionsY=14, name="c2_limb_geo")[0]
        cmds.move(0, 3.0, 0, c2_cyl)
        cmds.parent(c2_cyl, c2_group)
        cmds.skinCluster([c2_hip_jnt, c2_knee_jnt, c2_ankle_jnt], c2_cyl, name="c2_skinCluster")

        c2_ik = cmds.ikHandle(startJoint=c2_hip_jnt, endEffector=c2_ankle_jnt, solver="ikRPsolver", name="c2_ikHandle")[0]
        c2_foot_ctrl = cmds.circle(normal=(0, 1, 0), radius=1.6, name="c2_foot_ctrl")[0]
        cmds.move(0, 0, 0, c2_foot_ctrl)
        cmds.parent(c2_foot_ctrl, c2_group)
        cmds.parent(c2_ik, c2_foot_ctrl)

        c2_hip_ctrl = cmds.circle(normal=(0, 1, 0), radius=1.8, name="c2_hip_ctrl")[0]
        cmds.move(0, 6.0, 0, c2_hip_ctrl)
        cmds.parent(c2_hip_ctrl, c2_group)
        cmds.parentConstraint(c2_hip_ctrl, c2_hip_jnt, maintainOffset=True)

        ss.build_squash_stretch(
            start_driver=c2_hip_ctrl,
            end_driver=c2_foot_ctrl,
            target_joints=[c2_hip_jnt, c2_knee_jnt],
            ctrl_for_attrs=c2_foot_ctrl,
            primary_axis="X",
            prefix="c2_ss",
            rest_length=6.0,
        )

        # Keyframe Character 2 (Crouch -> High Cartoon Extension Kick -> Settle)
        foot_keys = [
            (1, 0.0, 0.0, 0.0),
            (18, 0.0, 1.8, 0.8),     # High bend crouch
            (38, 0.5, -2.8, -1.5),   # Extreme extension kick (stretches past rest)
            (60, 0.2, 0.5, 0.0),     # Recoil
            (85, -0.4, -2.2, 1.0),   # Forward reach
            (105, 0.0, 0.4, 0.0),    # Settling step
            (120, 0.0, 0.0, 0.0),    # Rest loop
        ]
        for f, tx, ty, tz in foot_keys:
            cmds.setKeyframe(f"{c2_foot_ctrl}.translateX", time=f, value=tx)
            cmds.setKeyframe(f"{c2_foot_ctrl}.translateY", time=f, value=ty)
            cmds.setKeyframe(f"{c2_foot_ctrl}.translateZ", time=f, value=tz)

        # ---------------------------------------------------------------------
        # Character 3: Flexible Cartoon Spine / Torso (Right, X = 7)
        # ---------------------------------------------------------------------
        c3_group = cmds.group(empty=True, name="char3_spine_grp")
        cmds.move(7, 0, 0, c3_group)

        cmds.select(clear=True)
        c3_j0 = cmds.joint(name="c3_spine_00_jnt", position=(7, 0.0, 0))
        c3_j1 = cmds.joint(name="c3_spine_01_jnt", position=(7, 1.8, 0))
        c3_j2 = cmds.joint(name="c3_spine_02_jnt", position=(7, 3.6, 0))
        c3_j3 = cmds.joint(name="c3_spine_03_jnt", position=(7, 5.4, 0))
        cmds.parent(c3_j0, c3_group)

        c3_geo = cmds.polyCone(radius=1.3, height=5.5, subdivisionsY=12, name="c3_spine_geo")[0]
        cmds.move(7, 2.75, 0, c3_geo)
        cmds.parent(c3_geo, c3_group)
        cmds.skinCluster([c3_j0, c3_j1, c3_j2, c3_j3], c3_geo, name="c3_skinCluster")

        c3_pelvis_ctrl = cmds.circle(normal=(0, 1, 0), radius=2.2, name="c3_pelvis_ctrl")[0]
        cmds.move(7, 0, 0, c3_pelvis_ctrl)
        cmds.parent(c3_pelvis_ctrl, c3_group)
        cmds.parentConstraint(c3_pelvis_ctrl, c3_j0, maintainOffset=True)

        c3_chest_ctrl = cmds.circle(normal=(0, 1, 0), radius=1.7, name="c3_chest_ctrl")[0]
        cmds.move(7, 5.4, 0, c3_chest_ctrl)
        cmds.parent(c3_chest_ctrl, c3_group)
        cmds.pointConstraint(c3_chest_ctrl, c3_j3, maintainOffset=True)

        ss.build_squash_stretch(
            start_driver=c3_pelvis_ctrl,
            end_driver=c3_chest_ctrl,
            target_joints=[c3_j1, c3_j2],
            ctrl_for_attrs=c3_chest_ctrl,
            primary_axis="Y",
            prefix="c3_ss",
            rest_length=5.4,
        )

        # Keyframe Character 3 (Breathing / Torso Compression & Elongation)
        spine_keys = [
            (1, 5.4),
            (22, 2.8),   # Heavy torso compression (expands wide)
            (48, 8.2),   # High vertical reach / arch (compresses narrow)
            (72, 3.4),   # Secondary compress
            (95, 6.2),   # Elastic recoil
            (120, 5.4),  # Clean rest loop
        ]
        for f, val in spine_keys:
            cmds.setKeyframe(f"{c3_chest_ctrl}.translateY", time=f, value=val)

        # ---------------------------------------------------------------------
        # Viewport Framing
        # ---------------------------------------------------------------------
        cmds.select(clear=True)
        # Position persp camera nicely
        cmds.setAttr("persp.translateX", 0.0)
        cmds.setAttr("persp.translateY", 5.5)
        cmds.setAttr("persp.translateZ", 22.0)
        cmds.setAttr("persp.rotateX", -8.0)
        cmds.setAttr("persp.rotateY", 0.0)
        cmds.setAttr("persp.rotateZ", 0.0)

        cmds.viewFit(all=True)

        result = {
            "ball_ctrl": c1_top_ctrl,
            "limb_ctrl": c2_foot_ctrl,
            "spine_ctrl": c3_chest_ctrl,
            "duration_frames": 120,
        }
        return result

    finally:
        cmds.undoInfo(closeChunk=True)


def export_playblast(
    filename: str = "squash_stretch_showcase",
    width: int = 1280,
    height: int = 720,
) -> str:
    """Export an animation playblast preview from the active Maya viewport."""
    out_dir = pathlib.Path(__file__).parent / "movies"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = str(out_dir / filename)

    cmds.currentTime(1)
    # Ensure viewport has smooth shading and textures enabled
    cmds.modelEditor("modelPanel4", edit=True, displayAppearance="smoothShaded", displayTextures=True)

    playblast_path = cmds.playblast(
        filename=out_file,
        format="image",
        compression="jpg",
        clearCache=True,
        viewer=False,
        showOrnaments=True,
        fp=4,
        percent=100,
        widthHeight=(width, height),
        startTime=1,
        endTime=120,
        forceOverwrite=True,
    )
    return str(playblast_path)
