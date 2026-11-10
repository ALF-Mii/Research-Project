# Research Project 1 Proposal: Maya Squash & Stretch Rigging Tool

**Student:** Alfredo M.  
**Course:** Programming for Animators  
**Software:** Autodesk Maya 2027 (Python 3 / `maya.cmds` / OpenMaya / PySide)  
**Milestone Date:** Tuesday, November 10, 2026 (Week 1 Verified)  
**Final Submission Date:** Monday, November 23, 2026  
**Presentation Date:** Tuesday, November 24, 2026  

---

## 1. The Project in One Sentence
I will build a custom Python tool with a UI in Autodesk Maya that automates modular squash-and-stretch setup on specific character rig components, complete with volume-preservation presets and blendshape integration.

---

## 2. Why This One
Right now, setting up squash-and-stretch requires manually building complex utility node networks (`distanceBetween` nodes, `multiplyDivide` nodes, `blendColors`, scale constraints), which is repetitive, prone to hierarchy breaks, and difficult to standardize across a character. Afterward, I will know how to programmatically construct rigging mechanics in Maya via Python, handle volume preservation math, and build a reusable pipeline tool that drastically speeds up stylized character animation.

---

## 3. What You'll Show
- **The Tool:** A custom UI (built with Python / PySide) inside Maya that allows the animator to select joints/controls, apply squash-and-stretch behaviors, and load/save preset deformation and blendshape values.
- **The Piece of Work:** An original 3D character rigged and fully responding to the tool, demonstrated through a short clip showcasing dynamic poses, stylized impacts, and facial/body blendshapes.

---

## 4. The Three Weeks

- **By Nov 10 (Week 1 - Completed & Verified):**  
  Core rigging logic in Python works. The underlying node network for volume-preserving squash & stretch can be generated automatically on selected joints/controls of any character model via script. Verified cycle-free via matrix decomposition and tested with live 1-click test rigs (Bouncing Ball & Cartoon Limb).
- **By Nov 17 (Week 2):**  
  Preset and blendshape functionality implemented. The tool can read/write squash-and-stretch configurations and trigger corresponding blendshapes (e.g., impact squash + puffed cheeks, elongated stretch) using JSON data or direct Maya attributes.
- **By Nov 23 (Week 3 - Final):**  
  Polished UI and full integration. The interface allows seamless toggling and blending of presets, and the completed character is posed in a dynamic test animation demonstrating the tool's capabilities.

---

## 5. The Smallest Version That Still Counts
If the advanced UI or preset serialization system runs into issues, the fallback is a functional shelf script that builds the squash-and-stretch node network on targeted joints with hardcoded blendshape connections, demonstrated live on the character rig.

---

## 6. The Riskiest Part
Preventing double transformations and cycling errors where the squash-and-stretch scaling interacts with blendshapes and existing rig constraints, as well as making sure volume preservation math behaves cleanly across multiple axes without mesh flipping.

---

## 7. Instructor Feedback & Action Plan
> **Instructor:** *"Thanks for getting it in. Squash and stretch sounds good. I'd like to see it on a couple characters if possible. I know you mentioned yours, so definitely at least one quality model, but you want to also make sure it works for other characters too. Ask fellow students if they have one you can use, if needed."*

### How the Tool Addresses This:
1. **Zero Hardcoded Names:** The tool does not look for specific joint names (e.g. `hip_JNT` or `spine_01`). It operates on user-selected transforms, arbitrary joint chains, and customizable naming prefixes.
2. **Selectable Primary Axis (X, Y, or Z):** Different auto-riggers and student characters orient joints differently (e.g. Maya HumanIK vs AdvancedSkeleton vs custom rigs). The tool supports stretching along X, Y, or Z while dynamically preserving volume on the other two axes.
3. **Multi-Character Testing Suite:** Built-in procedural test generators (Bouncing Ball, 3-joint Cartoon Limb) allow immediate verification across different topologies and kinematics before applying to external student rigs.
