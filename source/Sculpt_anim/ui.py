# PySide specific imports
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtWebEngineWidgets

# Python specific imports
from traceback import print_exc
import os

# Module specific imports
import Qt.custom_widget as cstm_widget

import Maya.custom_marking_menu as cstm_menu
import Qt.icon_rc
import Sculpt_anim.logic

logic = Sculpt_anim.logic.SculptAnimLogic()

# Software specific import
import maya.cmds as cmds
import maya.OpenMaya as om
import pymel.core as pm

# icons
PREVIOUS_KEY_ICON = QtGui.QIcon(":/images/previous.png")
NEXT_KEY_ICON = QtGui.QIcon(":/images/next.png")
KEY_ICON = QtGui.QIcon(":/images/key.png")
SELECT_MESH_ICON = QtGui.QIcon(":/images/target.png")
PARAM_ICON = QtGui.QIcon(":/images/brush.png")
SCULPT_TOOL_ICON = QtGui.QIcon(":/images/anim_sculpt.png")
RESET_ICON = QtGui.QIcon(":/images/reset.png")
DELETE_ICON = QtGui.QIcon(":/images/trash.png")
HELP_ICON = QtGui.QIcon(":/images/interogation_point.png")
TOOL_ICON = QtGui.QIcon(":/images/anim_sculpt.png")


class SculptAnimUI(QtCore.QObject):
    """Sculpt anim tool UI"""

    def __init__(self):
        super(SculptAnimUI, self).__init__()

        # function attribute
        self.marking_menu = cstm_menu.Menu("sculpting", cstm_menu.sculpt_anim)
        self.current_time = None

        # context manager
        self.current_mode = cmds.evaluationManager(query=True, mode=True)[0]
        if self.current_mode is not "off":
            cmds.evaluationManager(mode="off")

        # init qt
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # menus
        self.create_delete_menu()

    def create_widgets(self):
        """Create all Widget of QWidget"""
        # widget for main UI

        self.main_ui = cstm_widget.HTransparentDialogOnViewport(
            "anim sculpt",
            pos=[10, 10],
            size=[400, 30],
            tool_icon=TOOL_ICON,
            visible=True,
        )

        self.help_button = cstm_widget.HButton(icon=HELP_ICON, color="transparent")
        self.help_button.setToolTip("Help")

        self.mesh_label = QtWidgets.QLabel(text="No mesh selected")
        self.mesh_label.setStyleSheet(
            "QLabel"
            "{"
            "border: 1px solid #5d5d5d ;"
            "border-radius: 6px;"
            "padding: 0 8px;"
            "background-color: #4a4a4a;"
            "min-width: 80px;"
            "}"
        )

        self.select_mesh_button = cstm_widget.HButton(
            icon=SELECT_MESH_ICON, color="transparent"
        )
        self.select_mesh_button.setToolTip("Select mesh")

        self.previous_key_button = cstm_widget.HButton(
            icon=PREVIOUS_KEY_ICON, reduce_icon=5, color="transparent"
        )
        self.previous_key_button.setToolTip("Previous key")

        self.key_button = cstm_widget.HButton(
            icon=KEY_ICON, reduce_icon=3, color="transparent"
        )
        self.key_button.setToolTip("Set Key")

        self.next_key_button = cstm_widget.HButton(
            icon=NEXT_KEY_ICON, reduce_icon=5, color="transparent"
        )
        self.next_key_button.setToolTip("Next key")

        self.param_button = cstm_widget.HButton(
            icon=PARAM_ICON,
            reduce_icon=-3,
            color="transparent",
            pressed_color="transparent",
            checkable=True,
            checked_color="#ffb548",
        )
        self.param_button.setToolTip("Edit mode")

        self.tweener_slider = cstm_widget.HQSlider(default=0, slider_range=[0, 100])
        self.tweener_slider.setToolTip(
            "Twinning on existing target\nwill remove it this is undoable"
        )

        self.delete_button = cstm_widget.HButton(icon=DELETE_ICON, color="transparent")
        self.delete_button.setToolTip(
            "Delete               Click\nDelete all   Right click"
        )

        self.reset_button = cstm_widget.HButton(
            icon=RESET_ICON, reduce_icon=3, color="transparent"
        )
        self.reset_button.setToolTip("Reset deform")

        # disable widget
        self.previous_key_button.setEnabled(False)
        self.key_button.setEnabled(False)
        self.next_key_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.tweener_slider.setEnabled(False)
        self.param_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def create_layouts(self):
        """Create all layout of QWidget"""
        self.main_ui.main_layout.setSpacing(4)
        self.main_ui.main_layout.addWidget(self.mesh_label, 3)
        self.main_ui.main_layout.addWidget(self.select_mesh_button, 1)
        self.main_ui.main_layout.addWidget(self.key_button, 1)
        self.main_ui.main_layout.addWidget(self.reset_button, 1)
        self.main_ui.main_layout.addWidget(self.tweener_slider, 3)
        self.main_ui.main_layout.addWidget(self.param_button, 1)
        self.main_ui.main_layout.addWidget(self.delete_button, 1)
        self.main_ui.main_layout.addWidget(self.help_button, 1)

    def create_connections(self):
        """Create all connection of QWidget"""
        self.key_button.clicked.connect(self.set_key)
        self.reset_button.clicked.connect(self.reset)
        logic.cntx_click_on_mesh.connect(self.set_key)
        self.help_button.clicked.connect(self.show_help)
        self.param_button.clicked.connect(self.toggle_edit_mode)
        self.tweener_slider.sliderPressed.connect(self.init_tweener)
        self.delete_button.clicked.connect(logic.delete_current_target)
        self.main_ui.ui_leaved.connect(self.main_ui_quit)
        self.tweener_slider.sliderMoved.connect(
            lambda: logic.tweener_previs(self.tweener_slider.value())
        )
        self.tweener_slider.sliderReleased.connect(
            lambda: logic.tweener_key(self.tweener_slider.value())
        )
        self.select_mesh_button.clicked.connect(
            lambda: self.update_selected_mesh(cmds.ls(sl=1, sn=True))
        )
        self.no_mesh_error = lambda: cmds.inViewMessage(
            amg="Select a mesh to start editing", pos="botCenter", fade=True
        )

        # callback
        self.timechange_callback = om.MEventMessage.addEventCallback(
            "timeChanged", self.timeChange
        )

    def show_help(self):
        """Create help window loading the html page of the tool"""
        self.window = cstm_widget.HTransparentDialogOnViewport(
            "show_help",
            parent=self.main_ui,
            pos=[10, 10],
            size=[1000, 600],
            visible=True,
            orientation="vertical",
        )
        self.window.show()
        self.webEngineView = QtWebEngineWidgets.QWebEngineView(self.window)
        self.webEngineView.load(
            QtCore.QUrl().fromLocalFile(
                os.path.split(
                    os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
                )[0]
                + r"/docs/build/html/guides/Sculpt-anim.html"
            )
        )
        self.window.main_layout.addWidget(self.webEngineView)

    def main_delete_menu_popup(self):
        """delete ``delete_menu`` popup menu"""
        self.delete_menu.popup(QtGui.QCursor.pos())

    def create_delete_menu(self):
        """Populate delete popup menu"""
        self.delete_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.delete_button.customContextMenuRequested.connect(
            self.main_delete_menu_popup
        )

        self.delete_menu = QtWidgets.QMenu()
        self.delete_menu.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.delete_menu.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.delete_menu.setWindowOpacity(0.8)

        self.action_delete_all = QtWidgets.QAction(self.delete_menu)
        self.action_delete_all.setObjectName("delete")
        self.action_delete_all.setText("Delete all")
        self.action_delete_all.triggered.connect(self.delete_all)
        self.delete_menu.addAction(self.action_delete_all)

    def delete_all(self):
        """Delete all blendshape and reset tool"""

        logic.delete_all_target()
        self.mesh_label.setText("No mesh selected")
        self.param_button.setChecked(False)

        # disable widget
        self.previous_key_button.setEnabled(False)
        self.key_button.setEnabled(False)
        self.next_key_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.tweener_slider.setEnabled(False)
        self.param_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        cmds.setToolTo("selectSuperContext")
        self.key_button.set_style_sheet()

    def main_ui_quit(self):
        """Disconnect and reset what was change on tool quit"""
        self.marking_menu.removeOld()
        if self.param_button.isChecked():
            logic.leave_edit_mesh()
        logic.quit()
        cmds.evaluationManager(mode=self.current_mode)
        om.MMessage.removeCallback(self.timechange_callback)

    def update_selected_mesh(self, mesh):
        """Init tool for the selected mesh

        Args:
            mesh (str): new mesh
        """

        self.current_time = int(cmds.currentTime(query=True))

        # user error management
        if len(mesh) == 0:
            cmds.inViewMessage(
                amg="please select <hl>one</hl> mesh", pos="botCenter", fade=True
            )
            return
        elif len(mesh) > 1:
            cmds.inViewMessage(
                amg="you can only work on <hl>one</hl> mesh, first mesh was selected",
                pos="botCenter",
                fade=True,
            )

        objHist = cmds.listHistory(mesh[0], pdo=True)
        skinCluster = cmds.ls(objHist, type="skinCluster") or None
        if skinCluster is None:
            cmds.inViewMessage(
                amg="<hl>Mesh must be skinned</hl>", pos="botCenter", fade=True
            )
            return

        # init
        logic.mesh_init(mesh[0])
        self.mesh_label.setText(mesh[0])
        if cmds.objExists(logic.blendshape):
            cmds.select(logic.blendshape)

        # enable widget
        self.previous_key_button.setEnabled(True)
        self.key_button.setEnabled(True)
        self.next_key_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.tweener_slider.setEnabled(True)
        self.param_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def set_key(self):
        """Set a key on the blend shape"""
        if not logic.is_key():
            if cmds.objExists(logic.mesh):
                logic.create_target()
                logic.key_blendshape()
                logic.edit_mesh()
                self.param_button.setChecked(True)
                self.key_button.setStyleSheet("background-color: #cf3539")
            else:
                cmds.inViewMessage(
                    amg="Selected mesh no longer exist", pos="botCenter", fade=True
                )

    def init_tweener(self):

        if self.param_button.isChecked() is True:
            logic.leave_edit_mesh()
            self.param_button.setChecked(False)
            self.key_button.set_style_sheet()

        logic.twenner_init()

    def toggle_edit_mode(self):
        """Toggle mesh edit mode"""
        with pm.UndoChunk():
            if self.param_button.isChecked():
                if logic.is_key():
                    self.tweener_slider.setEnabled(False)
                    logic.edit_mesh()
                else:
                    self.set_key()
            else:
                self.tweener_slider.setEnabled(True)
                logic.leave_edit_mesh()

    def timeChange(self, *args):
        """update UI element and run function depending of current frame

        Args:
            *args: Allow maya to pass args
        """
        time = int(cmds.currentTime(query=True))
        if cmds.objExists(logic.blendshape):
            if time != self.current_time:
                self.current_time = time
                # If a pose was edited run the leave edit fct
                if self.param_button.isChecked():
                    logic.leave_edit_mesh()
                    self.param_button.setChecked(False)

                # UI update
                if logic.is_key():
                    self.key_button.setStyleSheet("background-color: #cf3539")
                else:
                    self.key_button.set_style_sheet()

            # set context that allow to click on the mesh to edit the mesh -> function : logic.SculptAnimLogic.cursor_on_mesh
            if cmds.draggerContext(logic.ctx, exists=True):
                cmds.deleteUI(logic.ctx)
            cmds.draggerContext(
                logic.ctx,
                pressCommand=logic.cursor_on_mesh,
                name=logic.ctx,
                cursor="crossHair",
            )
            cmds.setToolTo(logic.ctx)
            # Update tweener
            twenner_value = logic.tweener_pos_update()
            self.tweener_slider.setValue(twenner_value)
            self.tweener_slider.default_value = twenner_value

        else:
            self.key_button.set_style_sheet()
            self.param_button.setChecked(False)

    def reset(self):
        """update UI element and run reset function"""
        self.param_button.setChecked(True)
        self.key_button.setStyleSheet("background-color: #cf3539")
        logic.reset_shape()
