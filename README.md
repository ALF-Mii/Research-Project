# Maya Squash & Stretch Rigging Tool

[![Maya 2027](https://img.shields.io/badge/Maya-2027-blue.svg)](https://www.autodesk.com/products/maya/)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-brightgreen.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Milestone%201-Verified%20(Nov%2010)-success.svg)]()

A modular, volume-preserving Squash and Stretch rigging tool for Autodesk Maya. Built for stylized character animation, cartoon props, and dynamic rigging pipelines.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Instructor Feedback & Multi-Character Design](#instructor-feedback--multi-character-design)
3. [Mathematical Model](#mathematical-model)
4. [Live Test Verification](#live-test-verification)
5. [Installation & Quick Start](#installation--quick-start)
6. [Tool UI & Features](#tool-ui--features)
7. [API Reference](#api-reference)
8. [Milestones & Roadmap](#milestones--roadmap)

---

## Project Overview

In 3D animation, creating stylized squash and stretch traditionally requires manually wiring utility node networks (`distanceBetween`, `multiplyDivide`, `clamp`, `blendColors`, scale constraints) for each joint or limb. This process is time-consuming, prone to DAG cycle errors, and difficult to standardize across different characters.

This tool provides:
- **1-Click Procedural Setup:** Builds cycle-free node networks via matrix decomposition (`decomposeMatrix`).
- **Exact Volume Preservation:** Enforces constant 3D volume ($S_x \cdot S_y \cdot S_z = 1.0$) with user-controlled exaggeration exponents.
- **Topology & Rig Agnostic:** Works on any 2-point driver setup or multi-joint chain (bipeds, quadrupeds, tails, spines, balls, props).
- **Safe Reversibility:** Tags setups with a meta network node (`SS_Meta`), enabling 100% clean removal without leaving junk nodes or breaking joint hierarchies.
- **Blendshape Integration:** Automatically drives squash and stretch blendshapes based on deformation deltas.

---

## Instructor Feedback & Multi-Character Design

> **Instructor Feedback:**  
> *"Thanks for getting it in. Squash and stretch sounds good. I'd like to see it on a couple characters if possible. I know you mentioned yours, so definitely at least one quality model, but you want to also make sure it works for other characters too. Ask fellow students if they have one you can use, if needed."*

To satisfy this requirement, the tool is built with **zero hardcoded joint names**:
- Operates on user selection or explicit transform arguments.
- Supports selectable primary bone axes (**X**, **Y**, or **Z**) to accommodate different auto-riggers (e.g., HumanIK, AdvancedSkeleton, mGear, custom student rigs).
- Includes two built-in test rig generators (`bouncing_ball` and `cartoon_limb`) to immediately verify deformation behavior on different topologies before importing classmate characters.

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

Verified live in Autodesk Maya 2027 on November 10, 2026:

| Test Case | Driver Y | Stretch Ratio ($S$) | Primary Scale ($S_y$) | Secondary Scale ($S_x, S_z$) | Total Volume ($S_x \cdot S_y \cdot S_z$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rest Position** | 4.0 | 1.000 | 1.0000 | 1.0000 | **1.0000** |
| **2x Stretch** | 8.0 | 2.000 | 2.0000 | 0.7071 ($2^{-0.5}$) | **1.0000** |
| **0.5x Squash** | 2.0 | 0.500 | 0.5000 | 1.4142 ($0.5^{-0.5}$) | **1.0000** |

---

## Installation & Quick Start

### 1. In Maya Script Editor
Open Maya's **Script Editor** (`Windows > General Editors > Script Editor`), select the **Python** tab, and run:

```python
import sys
repo_path = r"C:\Users\alfre\Documents\Research-Project"
if repo_path not in sys.path:
    sys.path.append(repo_path)

import squash_stretch as ss
ss.show_ui()
```

### 2. Fast 1-Click Test Scene
To immediately generate a test rig and test the tool:
```python
import squash_stretch as ss

# Generates cartoon bouncing ball with volume S&S:
ss.create_test_rig("bouncing_ball")

# OR generates a 3-joint IK cartoon limb with stretch:
# ss.create_test_rig("cartoon_limb")
```

---

## Tool UI & Features

The tool features a lightweight UI (`ss.show_ui()`):
- **Step 1: Driver Selection:** Select your root transform and tip controller.
- **Step 2: Target Joints & Axis:** Pick the joints to deform, choose primary stretch axis (X, Y, or Z), and customize the naming prefix.
- **Build / Remove:** One-click generation and clean deconstruction.
- **Testing & Demos:** Procedural 1-click test rig generation.

### Animator Controller Attributes Added:
- `squashStretch`: Master blend slider (0.0 = off / normal scale, 1.0 = full S&S).
- `volumeFactor`: Multiplier for cross-axis volume expansion (default 1.0).
- `minSquashLimit`: Lowest squash threshold (prevents negative scaling / inversion).
- `maxStretchLimit`: Upper stretch threshold.
- `stretchOffset`: Manual offset adjustment.

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
Builds the cycle-free node network. Connects `decomposeMatrix`, `distanceBetween`, `multiplyDivide`, `clamp`, and `blendColors`.

### `remove_squash_stretch(ctrl_or_meta: str) -> bool`
Deletes all utility nodes associated with the setup, disconnects scale attributes, restores default scale `(1, 1, 1)`, and removes animator channel attributes.

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
Wires deformation deltas into blendshape target weights:
- Squash weight: $\text{clamp}(0, 1, (1.0 - S) \cdot \text{multiplier})$
- Stretch weight: $\text{clamp}(0, 1, (S - 1.0) \cdot \text{multiplier})$

---

## Milestones & Roadmap

- [x] **Week 1 (Nov 10): Core Rigging Engine**
  - Volume-preserving node network logic.
  - Cycle-free matrix decomposition.
  - Multi-axis support (X, Y, Z).
  - 1-click test rigs (`bouncing_ball`, `cartoon_limb`).
  - Safe removal system.
- [ ] **Week 2 (Nov 17): Presets & Blendshapes**
  - Bidirectional blendshape driver automation.
  - JSON preset serializer (e.g., "Rubber/Squishy", "Subtle/Flesh", "Hard-Surface").
- [ ] **Week 3 (Nov 23): Polished PySide UI & Multi-Character Demo**
  - Full PySide6 UI with preset browsing.
  - Integration on primary character and peer student rigs.
  - Final animation presentation clip.
- [ ] **Class Presentation (Nov 24)**
