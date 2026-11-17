"""PySide6 Modern UI for Maya Squash & Stretch Rigging Tool.

Author: Alfredo M.
Course: Programming for Animators - Research Project 1
Environment: Maya 2027 / Python 3 / PySide6
"""

import pathlib
from typing import Optional
from PySide6 import QtCore, QtGui, QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import shiboken6

import squash_stretch as ss
import showcase


def get_maya_main_window() -> Optional[QtWidgets.QWidget]:
    """Retrieve the Maya main window pointer wrapped as a QWidget."""
    ptr = omui.MQtUtil.mainWindow()
    if ptr:
        return shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)
    return None


class SquashStretchWindow(QtWidgets.QDialog):
    """Modern dark-themed PySide6 interface for the Squash & Stretch tool."""

    WINDOW_TITLE = "Squash & Stretch Rigging Tool"
    WINDOW_OBJECT = "MayaSquashStretchPySideWindow"

    def __init__(self, parent=None):
        super().__init__(parent or get_maya_main_window())
        self.setObjectName(self.WINDOW_OBJECT)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(440, 580)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        """Apply sleek stylesheet matching Maya's dark palette."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background: #2b2b2b;
                top: -1px;
            }
            QTabBar::tab {
                background: #333333;
                color: #b0b0b0;
                padding: 7px 14px;
                border: 1px solid #3c3c3c;
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                min-width: 75px;
            }
            QTabBar::tab:selected {
                background: #444444;
                color: #ffffff;
                font-weight: bold;
                border-bottom: 2px solid #5285a6;
            }
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 14px;
                font-weight: bold;
                color: #8faec4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 4px 6px;
                color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #5285a6;
            }
            QPushButton {
                background-color: #3e3e3e;
                color: #ffffff;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 6px 12px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #2e2e2e;
            }
            QPushButton#buildBtn {
                background-color: #2e5939;
                border-color: #3b7349;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#buildBtn:hover {
                background-color: #376b44;
            }
            QPushButton#removeBtn {
                background-color: #5c3232;
                border-color: #784141;
            }
            QPushButton#removeBtn:hover {
                background-color: #6e3b3b;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #5285a6;
                color: #ffffff;
            }
            QLabel#headerLabel {
                font-size: 15px;
                font-weight: bold;
                color: #5285a6;
            }
            QStatusBar {
                color: #aaaaaa;
            }
        """)

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 8)
        main_layout.setSpacing(10)

        # Header Title
        header = QtWidgets.QLabel("SQUASH & STRETCH RIGGER v3.0")
        header.setObjectName("headerLabel")
        header.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(header)

        # Tabs
        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        self._build_rigging_tab()
        self._build_presets_tab()
        self._build_blendshapes_tab()
        self._build_showcase_tab()

        # Status Bar / Message
        self.status_lbl = QtWidgets.QLabel("Ready. Select drivers in viewport.")
        self.status_lbl.setStyleSheet("color: #888888; font-style: italic; padding-top: 4px;")
        main_layout.addWidget(self.status_lbl)

    # ---------------- TAB 1: RIGGING ----------------
    def _build_rigging_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Drivers Box
        drv_box = QtWidgets.QGroupBox("Step 1: Drivers & Controller")
        drv_layout = QtWidgets.QGridLayout(drv_box)
        drv_layout.setSpacing(6)

        drv_layout.addWidget(QtWidgets.QLabel("Start Driver:"), 0, 0)
        self.start_edit = QtWidgets.QLineEdit()
        drv_layout.addWidget(self.start_edit, 0, 1)
        btn_start = QtWidgets.QPushButton("< Set")
        btn_start.clicked.connect(lambda: self._set_from_sel(self.start_edit))
        drv_layout.addWidget(btn_start, 0, 2)

        drv_layout.addWidget(QtWidgets.QLabel("End Driver:"), 1, 0)
        self.end_edit = QtWidgets.QLineEdit()
        drv_layout.addWidget(self.end_edit, 1, 1)
        btn_end = QtWidgets.QPushButton("< Set")
        btn_end.clicked.connect(lambda: self._set_from_sel(self.end_edit))
        drv_layout.addWidget(btn_end, 1, 2)

        drv_layout.addWidget(QtWidgets.QLabel("Attr Control:"), 2, 0)
        self.ctrl_edit = QtWidgets.QLineEdit()
        self.ctrl_edit.setPlaceholderText("(Defaults to End Driver)")
        drv_layout.addWidget(self.ctrl_edit, 2, 1)
        btn_ctrl = QtWidgets.QPushButton("< Set")
        btn_ctrl.clicked.connect(lambda: self._set_from_sel(self.ctrl_edit))
        drv_layout.addWidget(btn_ctrl, 2, 2)

        layout.addWidget(drv_box)

        # Target Joints Box
        jnt_box = QtWidgets.QGroupBox("Step 2: Target Joints & Axis")
        jnt_layout = QtWidgets.QGridLayout(jnt_box)
        jnt_layout.setSpacing(6)

        jnt_layout.addWidget(QtWidgets.QLabel("Target Joints:"), 0, 0)
        self.target_edit = QtWidgets.QLineEdit()
        jnt_layout.addWidget(self.target_edit, 0, 1)
        btn_targets = QtWidgets.QPushButton("< Set Sel")
        btn_targets.clicked.connect(lambda: self._set_from_sel(self.target_edit, multi=True))
        jnt_layout.addWidget(btn_targets, 0, 2)

        jnt_layout.addWidget(QtWidgets.QLabel("Primary Axis:"), 1, 0)
        self.axis_combo = QtWidgets.QComboBox()
        self.axis_combo.addItems(["X", "Y", "Z"])
        self.axis_combo.setCurrentText("Y")
        jnt_layout.addWidget(self.axis_combo, 1, 1, 1, 2)

        jnt_layout.addWidget(QtWidgets.QLabel("Prefix:"), 2, 0)
        self.prefix_edit = QtWidgets.QLineEdit("ss")
        jnt_layout.addWidget(self.prefix_edit, 2, 1, 1, 2)

        layout.addWidget(jnt_box)

        # Action Buttons
        self.btn_build = QtWidgets.QPushButton("BUILD SQUASH & STRETCH")
        self.btn_build.setObjectName("buildBtn")
        self.btn_build.setFixedHeight(36)
        self.btn_build.clicked.connect(self._on_build)
        layout.addWidget(self.btn_build)

        self.btn_remove = QtWidgets.QPushButton("REMOVE SELECTED SETUP")
        self.btn_remove.setObjectName("removeBtn")
        self.btn_remove.setFixedHeight(28)
        self.btn_remove.clicked.connect(self._on_remove)
        layout.addWidget(self.btn_remove)

        layout.addStretch()
        self.tabs.addTab(tab, "Rigging")

    # ---------------- TAB 2: PRESETS ----------------
    def _build_presets_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        layout.addWidget(QtWidgets.QLabel("Select a Controller in Maya to apply presets:"))

        self.preset_list = QtWidgets.QListWidget()
        layout.addWidget(self.preset_list)

        self.preset_desc = QtWidgets.QLabel("")
        self.preset_desc.setWordWrap(True)
        self.preset_desc.setStyleSheet("color: #b0c2ce; font-style: italic; padding: 4px;")
        layout.addWidget(self.preset_desc)

        self.preset_list.currentItemChanged.connect(self._on_preset_selected)

        btn_row = QtWidgets.QHBoxLayout()
        btn_apply = QtWidgets.QPushButton("Apply Preset to Selected Ctrl")
        btn_apply.setFixedHeight(32)
        btn_apply.clicked.connect(self._on_apply_preset)
        btn_row.addWidget(btn_apply)

        btn_save = QtWidgets.QPushButton("Save Current as Preset...")
        btn_save.setFixedHeight(32)
        btn_save.clicked.connect(self._on_save_preset)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

        self._refresh_presets()
        self.tabs.addTab(tab, "Presets")

    # ---------------- TAB 3: BLENDSHAPES ----------------
    def _build_blendshapes_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        bs_box = QtWidgets.QGroupBox("BlendShape Driver Setup")
        bs_layout = QtWidgets.QGridLayout(bs_box)
        bs_layout.setSpacing(6)

        bs_layout.addWidget(QtWidgets.QLabel("Controller:"), 0, 0)
        self.bs_ctrl_edit = QtWidgets.QLineEdit()
        bs_layout.addWidget(self.bs_ctrl_edit, 0, 1)
        btn_bs_ctrl = QtWidgets.QPushButton("< Set")
        btn_bs_ctrl.clicked.connect(lambda: self._set_from_sel(self.bs_ctrl_edit))
        bs_layout.addWidget(btn_bs_ctrl, 0, 2)

        bs_layout.addWidget(QtWidgets.QLabel("BlendShape Node:"), 1, 0)
        self.bs_node_edit = QtWidgets.QLineEdit()
        bs_layout.addWidget(self.bs_node_edit, 1, 1)
        btn_detect = QtWidgets.QPushButton("< Detect")
        btn_detect.clicked.connect(self._on_detect_bs)
        bs_layout.addWidget(btn_detect, 1, 2)

        bs_layout.addWidget(QtWidgets.QLabel("Squash Target:"), 2, 0)
        self.sq_tgt_edit = QtWidgets.QLineEdit()
        bs_layout.addWidget(self.sq_tgt_edit, 2, 1, 1, 2)

        bs_layout.addWidget(QtWidgets.QLabel("Stretch Target:"), 3, 0)
        self.st_tgt_edit = QtWidgets.QLineEdit()
        bs_layout.addWidget(self.st_tgt_edit, 3, 1, 1, 2)

        bs_layout.addWidget(QtWidgets.QLabel("Sensitivity:"), 4, 0)
        self.bs_sens_spin = QtWidgets.QDoubleSpinBox()
        self.bs_sens_spin.setRange(0.1, 10.0)
        self.bs_sens_spin.setValue(1.0)
        self.bs_sens_spin.setSingleStep(0.1)
        bs_layout.addWidget(self.bs_sens_spin, 4, 1, 1, 2)

        layout.addWidget(bs_box)

        btn_conn = QtWidgets.QPushButton("CONNECT BLENDSHAPE DRIVERS")
        btn_conn.setFixedHeight(34)
        btn_conn.clicked.connect(self._on_connect_bs)
        layout.addWidget(btn_conn)

        layout.addStretch()
        self.tabs.addTab(tab, "BlendShapes")

    # ---------------- TAB 4: SHOWCASE & DEMOS ----------------
    def _build_showcase_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        demo_box = QtWidgets.QGroupBox("Multi-Character Verification & Demos")
        demo_layout = QtWidgets.QVBoxLayout(demo_box)
        demo_layout.setSpacing(8)

        btn_showcase = QtWidgets.QPushButton("🎬 BUILD 3-CHARACTER ANIMATED SHOWCASE")
        btn_showcase.setFixedHeight(38)
        btn_showcase.setStyleSheet("background-color: #2b4d59; font-weight: bold; border-color: #3b6b7d;")
        btn_showcase.clicked.connect(self._on_build_showcase)
        demo_layout.addWidget(btn_showcase)

        btn_playblast = QtWidgets.QPushButton("🎥 Export Playblast Animation")
        btn_playblast.setFixedHeight(30)
        btn_playblast.clicked.connect(self._on_export_playblast)
        demo_layout.addWidget(btn_playblast)

        layout.addWidget(demo_box)

        single_box = QtWidgets.QGroupBox("Single Component Test Rigs")
        single_layout = QtWidgets.QVBoxLayout(single_box)

        btn_ball = QtWidgets.QPushButton("1. Cartoon Bouncing Ball (Volume S&S)")
        btn_ball.clicked.connect(lambda: ss.create_test_rig("bouncing_ball"))
        single_layout.addWidget(btn_ball)

        btn_ball_bs = QtWidgets.QPushButton("2. Ball with Live BlendShapes (Squash/Stretch)")
        btn_ball_bs.clicked.connect(lambda: ss.create_test_rig("ball_with_blendshapes"))
        single_layout.addWidget(btn_ball_bs)

        btn_limb = QtWidgets.QPushButton("3. 3-Joint Cartoon IK Limb (Chain S&S)")
        btn_limb.clicked.connect(lambda: ss.create_test_rig("cartoon_limb"))
        single_layout.addWidget(btn_limb)

        layout.addWidget(single_box)
        layout.addStretch()
        self.tabs.addTab(tab, "Showcase")

    # ---------------- HELPERS & SLOTS ----------------
    def _set_from_sel(self, edit_widget: QtWidgets.QLineEdit, multi: bool = False):
        sel = cmds.ls(selection=True)
        if not sel:
            self._set_status("Nothing selected in Maya viewport.", error=True)
            return
        edit_widget.setText(", ".join(sel) if multi else sel[0])
        self._set_status(f"Loaded: {edit_widget.text()}")

    def _set_status(self, text: str, error: bool = False):
        color = "#e06c75" if error else "#98c379"
        self.status_lbl.setStyleSheet(f"color: {color}; font-style: italic;")
        self.status_lbl.setText(text)

    def _on_build(self):
        start = self.start_edit.text().strip()
        end = self.end_edit.text().strip()
        ctrl = self.ctrl_edit.text().strip() or end
        targets = [t.strip() for t in self.target_edit.text().split(",") if t.strip()]
        axis = self.axis_combo.currentText()
        pfx = self.prefix_edit.text().strip() or "ss"

        if not start or not end or not targets:
            self._set_status("Start, End Driver, and at least 1 Target Joint required!", error=True)
            return

        try:
            ss.build_squash_stretch(
                start_driver=start,
                end_driver=end,
                target_joints=targets,
                ctrl_for_attrs=ctrl,
                primary_axis=axis,
                prefix=pfx,
            )
            self._set_status(f"Built Squash & Stretch on {', '.join(targets)}!")
        except Exception as e:
            self._set_status(f"Error: {e}", error=True)

    def _on_remove(self):
        sel = cmds.ls(selection=True)
        if not sel:
            self._set_status("Select controller or meta node to remove.", error=True)
            return
        if ss.remove_squash_stretch(sel[0]):
            self._set_status(f"Removed Squash & Stretch on {sel[0]}.")
        else:
            self._set_status("Could not remove setup.", error=True)

    def _refresh_presets(self):
        self.preset_list.clear()
        pdict = ss.list_presets()
        for name in pdict.keys():
            self.preset_list.addItem(name)
        if self.preset_list.count() > 0:
            self.preset_list.setCurrentRow(0)

    def _on_preset_selected(self, current, _):
        if not current:
            return
        pdict = ss.list_presets()
        name = current.text()
        if name in pdict:
            import json
            try:
                with open(pdict[name], "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    self.preset_desc.setText(data.get("description", "No description."))
            except Exception:
                self.preset_desc.setText("")

    def _on_apply_preset(self):
        sel = cmds.ls(selection=True)
        if not sel:
            self._set_status("Select a rig controller in Maya first.", error=True)
            return
        curr = self.preset_list.currentItem()
        if not curr:
            return
        pname = curr.text()
        if ss.load_preset(pname, sel[0]):
            self._set_status(f"Applied preset '{pname}' to {sel[0]}!")
        else:
            self._set_status("Failed to apply preset.", error=True)

    def _on_save_preset(self):
        sel = cmds.ls(selection=True)
        if not sel:
            self._set_status("Select a rig controller with S&S attributes.", error=True)
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "Save Preset", "Preset Name:")
        if ok and name.strip():
            filepath = ss.save_preset(name.strip(), sel[0])
            self._refresh_presets()
            self._set_status(f"Saved custom preset: {name.strip()}")

    def _on_detect_bs(self):
        sel = cmds.ls(selection=True)
        if not sel:
            self._set_status("Select a mesh or blendShape node.", error=True)
            return
        target = sel[0]
        if cmds.nodeType(target) == "blendShape":
            self.bs_node_edit.setText(target)
            self._populate_bs_targets(target)
        else:
            bss = ss.find_blendshapes(target)
            if bss:
                self.bs_node_edit.setText(bss[0])
                self._populate_bs_targets(bss[0])
                self._set_status(f"Found blendShape: {bss[0]}")
            else:
                self._set_status(f"No blendShape found on {target}", error=True)

    def _populate_bs_targets(self, bs_node: str):
        targets = ss.get_blendshape_targets(bs_node)
        for t in targets:
            tl = t.lower()
            if "squash" in tl and not self.sq_tgt_edit.text():
                self.sq_tgt_edit.setText(t)
            elif "stretch" in tl and not self.st_tgt_edit.text():
                self.st_tgt_edit.setText(t)

    def _on_connect_bs(self):
        ctrl = self.bs_ctrl_edit.text().strip()
        bs = self.bs_node_edit.text().strip()
        sq = self.sq_tgt_edit.text().strip() or None
        st = self.st_tgt_edit.text().strip() or None
        m = self.bs_sens_spin.value()

        if not ctrl or not bs:
            self._set_status("Controller and BlendShape node required!", error=True)
            return
        try:
            ss.connect_blendshape_driver(
                meta_or_ctrl=ctrl,
                blendshape_node=bs,
                squash_target_name=sq,
                stretch_target_name=st,
                multiplier=m,
            )
            self._set_status("BlendShape drivers connected successfully!")
        except Exception as e:
            self._set_status(f"Error: {e}", error=True)

    def _on_build_showcase(self):
        try:
            res = showcase.build_multi_character_showcase()
            self._set_status("3-Character Showcase Scene Built with Animation!")
        except Exception as e:
            self._set_status(f"Showcase Error: {e}", error=True)

    def _on_export_playblast(self):
        try:
            path = showcase.export_playblast()
            self._set_status(f"Playblast exported to movies/")
        except Exception as e:
            self._set_status(f"Playblast Error: {e}", error=True)


# Global window handle to prevent garbage collection
_ui_instance: Optional[SquashStretchWindow] = None


def show_pyside_ui() -> SquashStretchWindow:
    """Launch or focus the PySide6 Squash & Stretch Window."""
    global _ui_instance
    if _ui_instance is not None:
        try:
            _ui_instance.close()
            _ui_instance.deleteLater()
        except Exception:
            pass

    _ui_instance = SquashStretchWindow()
    _ui_instance.show()
    return _ui_instance
