
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui


class Default(QtCore.QObject):

    def __init__(self):
        super(Default, self).__init__()

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):

    def create_layout(self):

    def create_connections(self):



if __name__ == "__main__":

    try:
        Default.close() # pylint: disable=E0601
        Default.statusLater()
    except:
        pass

    Default.show()
