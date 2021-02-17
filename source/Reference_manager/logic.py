# Python built-in imports
import os

# PySide specific imports
from PySide2 import QtWidgets, QtCore, QtGui

# Python specific imports
from collections import OrderedDict

# Software specific import
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import pymel.core as pm
import maya.mel as mel
import Maya.misc_tools as mtools


class ReferenceManagerLogic(QtCore.QObject):
    """Rig manager tool Logic"""

    def __init__(self):
        super(ReferenceManagerLogic, self).__init__()

        self.namespace = None
        self.reference = None
        self.widget = None
        self.rigs = None
        self.get_rigs()

    def get_rigs(self):
        """get the rigs name and their current status"""
        self.rigs = OrderedDict()
        references = sorted(mtools.get_reference())
        for ref in references:
            self.reference = ref
            file_path = cmds.referenceQuery(ref, filename=True)
            self.namespace = cmds.file(file_path, q=True, namespace=True)
            self.rigs[self.reference] = self.get_current_state()

    @mtools.viewportOff
    def update_status(self, selected_widget, status_dict):
        """update status icon and run the change state function on selected widget

        Args:
            status_dict ([dict]): {widget, widget_status} the icon of the widget will be set
            to widget_status, accepted value for widget_status are ``green``, ``orange``, ``red``
        """
        for widget, status in status_dict.items():
            for sel_widget in selected_widget:
                self.widget = sel_widget
                self.reference = self.widget.objectName()
                file_path = cmds.referenceQuery(self.reference, filename=True)
                self.namespace = cmds.file(file_path, q=True, namespace=True)
                self.change_state(status)

    def change_state(self, state_dest):
        """change state of reference according to current state and state destination

        Args:
            state_dest ([str]): state destination
        """
        current_state = self.get_current_state()
        if state_dest != current_state:
            if state_dest == "orange" and current_state == "green":
                self.create_cache()
                self.widget.change_status({self.widget: "orange"})

            elif state_dest == "orange" and current_state == "red":
                try:
                    cmds.file(loadReference=self.reference)
                except RuntimeError:
                    pass
                self.create_cache()
                self.widget.change_status({self.widget: "orange"})

            elif state_dest == "red" and current_state == "orange":
                cmds.delete(self.namespace + "_cache")
                self.widget.change_status({self.widget: "red"})

            elif state_dest == "red" and current_state == "green":
                try:
                    cmds.file(unLoadReference=self.reference)
                except RuntimeError:
                    pass
                self.widget.change_status({self.widget: "red"})

            elif state_dest == "green" and current_state == "orange":
                try:
                    cmds.file(loadReference=self.reference)
                except RuntimeError:
                    pass
                cmds.delete(self.namespace + "_cache")
                self.widget.change_status({self.widget: "green"})

            elif state_dest == "green" and current_state == "red":
                try:
                    cmds.file(loadReference=self.reference)
                except RuntimeError:
                    pass
                self.widget.change_status({self.widget: "green"})

    def get_current_state(self):
        """return the current state of the reference

        Args:
            widget (cstm_widget.HStatus): HStatus widget for given reference

        Returns:
            [str]: current status on HStatus
        """
        if cmds.referenceQuery(self.reference, il=True) is False:
            if cmds.objExists(self.namespace + "_cache"):
                return "orange"
            else:
                return "red"
        elif cmds.referenceQuery(self.reference, il=True) is True:
            return "green"

    def create_cache(self):
        """export selected rig to gpu unload reference and load gpu cache

        Args:
            namespace ([str]): namespace of the reference
            reference ([str]): reference name
        """
        # get time range
        time = mtools.get_time(1)
        mesh_list = mtools.get_visible_mesh_from_namespace(self.namespace)
        file_name = self.namespace
        gpu_path = self.path_gen(file_name)
        mtools.export_gpu(mesh_list, time, file_name, gpu_path)
        mtools.import_gpu(file_name, gpu_path)
        # unload reference
        cmds.file(unloadReference=self.reference)

    def path_gen(self, file_name):
        """generate path and create gpu cache folder if needed

        Args:
            file_name ([str]): name of the gpu cache file

        Returns:
            [str]: path of gpu cache file
        """
        self.filepath = cmds.file(q=True, sn=True)
        self.filename = os.path.basename(self.filepath)
        self.folder_path = os.path.dirname(self.filepath)

        gpu_path = os.path.normpath(
            os.path.join(self.folder_path, "gpu_cache", file_name)
        )
        if not os.path.exists(gpu_path):
            os.makedirs(gpu_path)
        return gpu_path
