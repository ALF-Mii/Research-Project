# Maya Squash & Stretch Rigging Tool

[![Maya 2027](https://img.shields.io/badge/Maya-2027-blue.svg)](https://www.autodesk.com/products/maya/)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-brightgreen.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6-orange.svg)](https://wiki.qt.io/Qt_for_Python)
[![Milestone 1](https://img.shields.io/badge/Milestone%201-Verified%20(Nov%2010)-success.svg)]()
[![Milestone 2](https://img.shields.io/badge/Milestone%202-Verified%20(Nov%2017)-success.svg)]()
[![Milestone 3](https://img.shields.io/badge/Milestone%203-Complete%20(Nov%2023)-success.svg)]()

A modular, volume-preserving Squash and Stretch rigging tool for Autodesk Maya. Built for stylized character animation, cartoon props, and dynamic rigging pipelines.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Instructor Feedback & Multi-Character Design](#instructor-feedback--multi-character-design)
3. [Mathematical Model](#mathematical-model)
4. [Live Test Verification](#live-test-verification)
5. [Blendshape Integration](#blendshape-integration)
6. [JSON Preset System](#json-preset-system)
7. [Multi-Character Showcase Animation](#multi-character-showcase-animation)
8. [Installation & Quick Start](#installation--quick-start)
9. [Modern PySide6 UI](#modern-pyside6-ui)
10. [API Reference](#api-reference)
11. [Presentation & In-Class Demo Guide](#presentation--in-class-demo-guide)
12. [Milestones & Progress](#milestones--progress)

---

## Project Overview

In 3D animation, creating stylized squash and stretch traditionally requires manually wiring utility node networks (`distanceBetween`, `multiplyDivide`, `clamp`, `blendColors`, scale constraints) for each joint or limb. This process is time-consuming, prone to DAG cycle errors, and difficult to standardize across different characters.

This tool provides:
- **1-Click Procedural Setup:** Builds cycle-free node networks via matrix decomposition (`decomposeMatrix`).
- **Exact Volume Preservation:** Enforces constant 3D volume ($S_x \cdot S_y \cdot S_z = 1.0$) with user-controlled exaggeration exponents.
- **Topology & Rig Agnostic:** Works on any 2-point driver setup or multi-joint chain (bipeds, quadrupeds, tails, spines, balls, props).
- **Bidirectional Blendshape Drivers:** Automatically fires squash blendshapes (e.g. cheek puffs, belly squashes) on compression, and stretch blendshapes on elongation.
- **JSON Preset Engine:** One-click saving and loading of character deformation profiles (Cartoony, Realistic, Mechanical, Impact).
- **Multi-Character Animated Showcase:** 3-character side-by-side animated demonstration scene with automatic 120-frame keyframing and playblast exporter.
- **Modern PySide6 UI:** Dark-themed Qt window with live parameter readouts, preset browsing, and one-click rigging actions.
- **Safe Reversibility:** Tags setups with a meta network node (`SS_Meta`), enabling 100% clean removal without leaving junk nodes or breaking joint hierarchies.

---

## Instructor Feedback & Multi-Character Design

> **Instructor Feedback:**  
> *"Thanks for getting it in. Squash and stretch sounds good. I'd like to see it on a couple characters if possible. I know you mentioned yours, so definitely at least one quality model, but you want to also make sure it works for other characters too. Ask fellow students if they have one you can use, if needed."*

To satisfy this requirement, the tool is built with **zero hardcoded joint names**:
- Operates on user selection or explicit transform arguments.
- Supports selectable primary bone axes (**X**, **Y**, or **Z**) to accommodate different auto-riggers (e.g., HumanIK, AdvancedSkeleton, mGear, custom student rigs).
- Includes the **3-Character Animated Showcase** (`showcase.py`) demonstrating simultaneous volume preservation across:
  1. **Character A (Cartoon Bouncing Ball):** Full volume preservation + squash/stretch blendshapes.
  2. **Character B (3-Joint IK Cartoon Limb):** Multi-joint bone chain stretching past rest with lateral compression.
  3. **Character C (4-Joint Cartoon Spine):** Flexible spine compression and arching elongation.

---

## Mathematical Model

### 1. Stretch Ratio ($S$)
Given start driver position $P_{\text{start}}$ and end driver position $P_{\text{end}}$:
$$\text{Current Distance } L = \| P_{\text{end}} - P_{\text{start}} \|$$
$$S = \frac{L + \text{offset}}{L_0}$$
Where $L_0$ is the rest length measured at setup time. $S$ is clamped between `minSquash` (default 0.2) and `maxStretch` (default 3.0).

### 2. Volume Preservation Math
In 3D space, constant volume requires:
$$V = S_x \cdot S_y \cdot S_z = 1.0$$

If stretching along primary axis $Y$ by factor $S$ ($S_y = S$), and assuming uniform circular cross-section ($S_x = S_z$):
$$S_x \cdot S_z = \frac{1}{S} \implies S_x = S_z = \frac{1}{\sqrt{S}} = S^{-0.5}$$

To give animators creative control over exaggeration, a `volumeFactor` attribute ($k \ge 0$, default $1.0$) is introduced:
$$S_{\text{secondary}} = S^{-0.5 \cdot k}$$

- **$k = 0.0$:** Mechanical stretch (no cross-axis change).
- **$k = 1.0$:** Exact mathematical volume preservation.
- **$k > 1.0$:** Exaggerated cartoon volume.

---

## Live Test Verification

Verified live in Autodesk Maya 2027:

### Volume Preservation Data
| Test Case | Driver Y | Stretch Ratio ($S$) | Primary Scale ($S_y$) | Secondary Scale ($S_x, S_z$) | Total Volume ($S_x \cdot S_y \cdot S_z$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rest Position** | 4.0 | 1.000 | 1.0000 | 1.0000 | **1.0000** |
| **2x Stretch** | 8.0 | 2.000 | 2.0000 | 0.7071 ($2^{-0.5}$) | **1.0000** |
| **0.5x Squash** | 2.0 | 0.500 | 0.5000 | 1.4142 ($0.5^{-0.5}$) | **1.0000** |

### BlendShape Activation Data
| Driver State | Stretch Ratio ($S$) | Squash Shape Weight | Stretch Shape Weight |
| :--- | :--- | :--- | :--- |
| **Rest** (Y=4) | 1.0 | 0.00 | 0.00 |
| **Stretched** (Y=8) | 2.0 | 0.00 | **1.00** |
| **Squashed** (Y=2) | 0.5 | **0.50** (with 1.0 mult) | 0.00 |

---

## Blendshape Integration

The tool connects deformation deltas directly into Maya `blendShape` target weights without script expressions:
- **Squash Delta Driver ($S < 1.0$):**
  $$\text{Weight}_{\text{squash}} = \text{clamp}\Big(0.0,\, 1.0,\, (1.0 - S) \cdot \text{multiplier}\Big)$$
- **Stretch Delta Driver ($S > 1.0$):**
  $$\text{Weight}_{\text{stretch}} = \text{clamp}\Big(0.0,\, 1.0,\, (S - 1.0) \cdot \text{multiplier}\Big)$$

Animators can keyframe or dial `squashBS_mult` and `stretchBS_mult` directly in the Channel Box to fine-tune how aggressively the character's facial/body shapes react.

---

## JSON Preset System

Presets are stored as standard JSON files inside the [`presets/`](presets/) directory.

### Built-in Profiles:
1. **Cartoony Rubber (`cartoony_rubber.json`):**
   - High volume expansion (`volumeFactor = 1.4`), wide bounds (`minSquash = 0.1`, `maxStretch = 4.0`), heightened blendshape reaction (`mult = 1.5`).
2. **Realistic Flesh (`realistic_flesh.json`):**
   - Subtle anatomy preservation (`volumeFactor = 0.85`), conservative bounds (`minSquash = 0.65`, `maxStretch = 1.35`).
3. **Mechanical Hard-Surface (`mechanical_hardsurface.json`):**
   - Zero lateral distortion (`volumeFactor = 0.0`), strict bounds (`minSquash = 0.85`, `maxStretch = 1.25`), no blendshapes.
4. **Impact Squash (`impact_squash.json`):**
   - Extreme ground contact flattening (`minSquash = 0.05`, `volumeFactor = 1.8`, `squashBS_mult = 2.0`).

---

## Multi-Character Showcase Animation

Run one command in Maya to construct an animated side-by-side comparison across 3 distinct characters:

```python
import showcase
showcase.build_multi_character_showcase()
```

- **Frame 1–30:** Anticipation & crouching squash.
- **Frame 31–60:** Explosive jump & high extension kicks (volume compression).
- **Frame 61–90:** Ground impact squash (blendshape triggers) & elastic torso recoil.
- **Frame 91–120:** Settling loop back to rest.

To export playblast animation frames:
```python
showcase.export_playblast("my_showcase")
```
Exported frames are saved in [`movies/`](movies/).

---

## Installation & Quick Start

### 1. Launch the Modern PySide6 UI in Maya
Open Maya's **Script Editor** (`Windows > General Editors > Script Editor`), select the **Python** tab, and run:

```python
import sys
repo_path = r"C:\Users\alfre\Documents\Research-Project"
if repo_path not in sys.path:
    sys.path.append(repo_path)

import squash_stretch_pyside as ss_ui
ss_ui.show_pyside_ui()
```

### 2. Fast 1-Click Verification Demos
```python
import showcase
showcase.build_multi_character_showcase()
```

---

## Modern PySide6 UI

The tool features a 4-tab interface ([`squash_stretch_pyside.py`](squash_stretch_pyside.py)):
- **Tab 1: Rigging:** Start & End driver selection, target joints, primary axis selection (X, Y, Z), and one-click build/remove.
- **Tab 2: Presets:** Preset dropdown selector with description preview, "Apply to Selected Ctrl", and "Save Current as Preset...".
- **Tab 3: BlendShapes:** Auto-detect blendShape nodes, map squash & stretch target channels, and adjust sensitivity.
- **Tab 4: Showcase:** 1-click 3-character animated showcase builder and playblast exporter.

*(A native Maya `cmds` fallback interface is also available via `squash_stretch.show_ui()` for systems without PySide).*

---

## Presentation & In-Class Demo Guide

See [`PRESENTATION_NOTES.md`](PRESENTATION_NOTES.md) for the complete 5-minute presentation script, live demo walkthrough, and anticipated Q&A for the **Tuesday, November 24** presentation.

---

## API Reference

### `build_squash_stretch(...)`
```python
build_squash_stretch(
    start_driver: str,
    end_driver: str,
    target_joints: list[str],
    ctrl_for_attrs: str = None,
    primary_axis: str = "Y",
    prefix: str = "ss",
    rest_length: float = None
) -> dict
```

### `connect_blendshape_driver(...)`
```python
connect_blendshape_driver(
    meta_or_ctrl: str,
    blendshape_node: str,
    squash_target_name: str = None,
    stretch_target_name: str = None,
    multiplier: float = 1.0,
    prefix: str = "ss_bs"
) -> dict
```

### `load_preset(preset_name_or_file: str, ctrl: str) -> bool`
Loads JSON configuration and applies settings to the target controller attributes.

### `save_preset(name: str, ctrl: str, description: str = "") -> str`
Serializes active controller settings to a new JSON file in `presets/`.

### `remove_squash_stretch(ctrl_or_meta: str) -> bool`
Cleanly reverts joint scales and deletes all helper nodes.

---

## Milestones & Progress

- [x] **Week 1 (Nov 10): Core Rigging Engine**
  - Volume-preserving node network logic.
  - Cycle-free matrix decomposition.
  - Multi-axis support (X, Y, Z).
  - 1-click test rigs (`bouncing_ball`, `cartoon_limb`).
  - Safe removal system.
- [x] **Week 2 (Nov 17): Presets & Blendshapes**
  - Bidirectional blendshape driver automation.
  - Interactive sensitivity multipliers on controller.
  - JSON preset serializer & loader with 4 built-in profiles.
  - Live test rig with active blendshape targets (`ball_with_blendshapes`).
- [x] **Week 3 (Nov 23): Polished PySide UI & Multi-Character Showcase**
  - Modern PySide6 dark-themed UI window (`squash_stretch_pyside.py`).
  - 3-Character animated showcase scene with 120-frame animation (`showcase.py`).
  - Automatic playblast exporter.
  - Presentation notes and live demo script (`PRESENTATION_NOTES.md`).
- [ ] **Class Presentation (Nov 24)**
