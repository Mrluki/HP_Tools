# Python specifiv imports
import os
import sys

# PySide specific imports
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

# Module specific imports
import Qt.custom_widget as cstm_widget
import Qt.icon_rc

# Software specific import
import maya.cmds as cmds
import maya.mel as mel

HP_TOOLS_ICON = QtGui.QPixmap(":/images/h_tool_logo.png")
TOOL_PATH = os.path.split(os.path.abspath(__file__))[0]
SCULPT_ANIM_ICON = TOOL_PATH + "/Sculpt_anim/Sculpt_anim_icon.png"
installer_UI = None
SCULPT_ANIM_COMMAND = """

import Sculpt_anim.ui as sculpt_anim

try:
    UI.main_ui.close()
    UI.main_ui.deleteLater()
    UI.main_ui_quit()
except (RuntimeError, TypeError, NameError):
    pass
except Exception as e:
    cmds.warning(e)


sculpt_anim_UI = sculpt_anim.SculptAnimUI()
sculpt_anim_UI.main_ui.show()
"""

TOOLS = [
    {
        "label": "sculpt anim",
        "command": SCULPT_ANIM_COMMAND,
        "annotation": "",
        "image1": SCULPT_ANIM_ICON,
        "sourceType": "python",
    }
]


class InstallUI(QtCore.QObject):
    """Sculpt anim tool UI"""

    def __init__(self):
        super(InstallUI, self).__init__()

        # init qt
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        """Create all Widget of QWidget"""
        # widget for main UI
        self.main_ui = QtWidgets.QDialog()
        self.logo = QtWidgets.QLabel()
        self.logo.setPixmap(
            HP_TOOLS_ICON.scaled(
                80,
                80,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.FastTransformation,
            )
        )
        self.logo.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.intro_label = QtWidgets.QLabel(
            "Congratulation, HP_tools was successfully installed! \n Do you wish to install the shelf?\n"
        )
        self.intro_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.yes_button = cstm_widget.HButton(
            text="YES",
            color="#cb8c06",
            hover_color="#f9b013",
            pressed_color="#f9b013",
            size=[120, 30],
            fixed=True,
        )
        self.yes_button.setFont(QtGui.QFont("Roboto", 10, weight=QtGui.QFont.Bold))

        self.no_button = cstm_widget.HButton(
            text="NO", color="#383838", size=[120, 30], fixed=True
        )
        self.no_button.setFont(QtGui.QFont("Roboto", 10, weight=QtGui.QFont.Bold))

    def create_layouts(self):
        """Create all layout of QWidget"""
        self.main_layout = QtWidgets.QVBoxLayout(self.main_ui)
        self.main_layout.setSpacing(4)
        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.logo)
        self.main_layout.addWidget(self.intro_label)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)

    def create_connections(self):
        """Create all connection of QWidget"""
        self.yes_button.clicked.connect(self.add_shelf_button)
        self.no_button.clicked.connect(self.main_ui.deleteLater)

    def add_shelf_button(self):
        """Add a new shelf in Maya for the tools"""

        shelf_name = "HPTools"
        # get top shelf
        ShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")
        shelves = cmds.tabLayout(ShelfTopLevel, query=1, ca=1)

        # delete shelf if it exists
        if "HPTools" in shelves:
            cmds.deleteUI(shelf_name)

        # create shelf and button
        shelf = cmds.shelfLayout(shelf_name, parent=ShelfTopLevel)
        mel.eval("shelfTabLayout -edit -selectTab HPTools ShelfLayout;")
        for tool in TOOLS:
            if tool.get("image1"):
                cmds.shelfButton(style="iconOnly", parent=shelf_name, **tool)
            else:
                cmds.shelfButton(style="textOnly", parent=shelf_name, **tool)

        self.main_ui.deleteLater()


def user_setup():
    """ Create an userSetup.py for hptool if userSetup already exist append the line in it """
    usd = cmds.internalVar(usd=True)
    user_setup_path = "%s/%s/%s" % (usd.rsplit("/", 3)[0], "scripts", "userSetup.py")
    text = [
        "# Hp_tools",
        "import sys",
        "hp_tools_path = '%s'" % TOOL_PATH,
        "sys.append(hp_tools_path)",
    ]

    f = open(user_setup_path, "a+")
    if check_if_string_in_file(user_setup_path, text[0]) is False:
        for line in text:
            f.write(line + "\n")
    else:
        # security in case of reinstall of the tool
        lst = []
        for line in f:
            for word in text:
                if word in line or "hp_tools_path" in line:
                    line = line.replace(word, "")
            lst.append(line)
        for i in lst:
            if i == "\n":
                lst.remove(i)
        f.close()
        with open(user_setup_path, "w") as f:
            for line in lst:
                f.write(line)
            for line in text:
                f.write(line + "\n")


def check_if_string_in_file(file_name, string_to_search):
    """ Check if any line in the file contains given string """
    with open(file_name, "r") as read_obj:
        for line in read_obj:
            if string_to_search in line:
                return True
    return False
