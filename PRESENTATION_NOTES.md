# Research Project 1: Presentation Notes & Live Demo Script

**Course:** Programming for Animators  
**Date:** Tuesday, November 24, 2026 (In-Class Presentation)  
**Presenter:** Alfredo M.  
**Project:** Maya Squash & Stretch Rigging Tool  
**Repository:** [https://github.com/ALF-Mii/Research-Project](https://github.com/ALF-Mii/Research-Project)  

---

## 1. Quick Presentation Outline (5 Minutes)

### Slide / Opening: The Project in One Sentence (30 seconds)
> *"For my research project, I built an automated, modular Squash & Stretch rigging tool with a PySide UI in Autodesk Maya that delivers exact volume preservation, JSON preset profiles, and bidirectional blendshape drivers across multiple character rigs."*

### Why This Tool (1 minute)
- **The Problem:** Manually wiring squash and stretch in Maya is tedious, error-prone, and fragile. Riggers have to build complex utility node networks (`distanceBetween`, `multiplyDivide`, `clamp`, `blendColors`), calculate volume cross-scaling formulas, and often run into DAG cycle errors and double-transform bugs.
- **The Solution:** Automate the entire process programmatically with zero hardcoded joint names, full cycle-free matrix decomposition, and dynamic shape driver integration.

### Instructor Feedback Addressed: Multi-Character Compatibility (1 minute)
- **Instructor's Note:** *"I'd like to see it on a couple characters if possible... make sure it works for other characters too."*
- **How I Solved It:**
  1. **Zero Hardcoded Names:** The tool accepts user selection or arbitrary joint chains.
  2. **Selectable Primary Axis (X, Y, or Z):** Accommodates different auto-riggers (e.g., HumanIK vs AdvancedSkeleton vs custom rigs).
  3. **3-Character Animated Showcase:** Built directly into the tool (`showcase.py`) demonstrating:
     - **Character A (Cartoon Bouncing Ball):** Full volume preservation + squash/stretch blendshapes.
     - **Character B (3-Joint IK Cartoon Limb):** Multi-joint bone chain stretching past rest with volume compression.
     - **Character C (4-Joint Cartoon Spine):** Flexible spine compression and arching elongation.

### The Mathematics: Volume Preservation (1 minute)
- Constant volume in 3D: $V = S_x \cdot S_y \cdot S_z = 1.0$
- If stretching along primary axis $Y$ by factor $S$:
  $$S_y = S \implies S_x = S_z = S^{-0.5 \cdot \text{volumeFactor}}$$
- **Live Numbers from Maya:**
  - At **2x Stretch ($S = 2.0$)**: Scale = $(0.7071, 2.0, 0.7071) \implies \text{Volume} = \mathbf{1.0000}$
  - At **0.5x Squash ($S = 0.5$)**: Scale = $(1.4142, 0.5, 1.4142) \implies \text{Volume} = \mathbf{1.0000}$

---

## 2. Live Demo Script (Step-by-Step in Maya)

### Step 1: Open the Tool in Maya (15 seconds)
Run in Script Editor:
```python
import squash_stretch_pyside as ss_ui
ss_ui.show_pyside_ui()
```
Show the class the modern dark-themed Qt window with its 4 tabs: **Rigging**, **Presets**, **BlendShapes**, and **Showcase**.

### Step 2: Play the Multi-Character Animated Showcase (45 seconds)
1. In the **Showcase** tab, click **"🎬 BUILD 3-CHARACTER ANIMATED SHOWCASE"** (or run `import showcase; showcase.build_multi_character_showcase()`).
2. Press **Play** on the Maya timeline (120 frames):
   - Point out the **Bouncing Ball** on the left: watch the cheek puff / squash blendshape fire on the ground impact (frame 62), and the elongated stretch shape fire during the explosive jump (frame 28).
   - Point out the **IK Limb** in the center: watch the thigh and shin joints dynamically compress cross-axially when kicking high past its rest length.
   - Point out the **Spine** on the right: watch the torso widen on compression and slim down during the vertical reach.

### Step 3: Demonstrate Live Preset Switching (30 seconds)
1. Select the ball controller `c1_stretch_ctrl`.
2. Go to the **Presets** tab:
   - Select **"Cartoony Rubber"** $\to$ click **Apply** (volume factor jumps to 1.4, exaggerated bouncy feel).
   - Select **"Mechanical Hard-Surface"** $\to$ click **Apply** (volume factor drops to 0.0, strict limits, robotic feel).
3. Move the controller up and down to show how the character's physical deformation profile instantly transforms.

### Step 4: Clean Reversal / Safe Deconstruction (15 seconds)
1. Click **"REMOVE SELECTED SETUP"**.
2. Show that Maya's joints cleanly revert to $(1, 1, 1)$ without breaking the rig or leaving junk nodes behind.

---

## 3. Anticipated Questions & Answers

**Q: Did you encounter any cycle errors when connecting distances and scales?**  
*A: Yes, that was the riskiest part identified in the proposal. If you connect scale back into an IK chain or use point constraints that depend on child transforms, Maya throws DAG cycle warnings. I solved this by using `decomposeMatrix` from the world matrices of the driver transforms, completely isolating the distance calculation from the hierarchy.*

**Q: How do the blendshapes know when to trigger?**  
*A: I wired two math branches using `plusMinusAverage`, `multDL`, and `clamp` nodes: one calculates $(1.0 - S)$ for squash, and the other calculates $(S - 1.0)$ for stretch. The animators can tune sensitivity on the controller via `squashBS_mult` and `stretchBS_mult`.*

**Q: Can this be run on another student's rig?**  
*A: Yes. It takes 3 inputs in the UI: Start Driver, End Driver, and Target Joints, with a choice of X, Y, or Z stretch axis. It does not rely on any preset naming conventions.*
