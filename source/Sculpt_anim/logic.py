# Python built-in imports
import os

# PySide specific imports
from PySide2 import QtWidgets, QtCore, QtGui

# Software specific import
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import pymel.core as pm
import maya.mel as mel
import Maya.misc_tools as mtools


class SculptAnimLogic(QtCore.QObject):
    """Sculpt anim tool Logic"""

    # Signals
    cntx_click_on_mesh = QtCore.Signal()

    def __init__(self):
        super(SculptAnimLogic, self).__init__()

        # function attributes
        self.mesh = None
        self.mesh_shape = None
        self.mesh_short_name = None
        self.temp = None
        self.temp_skin = None
        self.grp = None
        self.base_mesh = None
        self.blendshape = None
        self.number_of_blend_shapes = 0
        self.target = None
        self.current = None
        self.next_key = None
        self.prev_key = None
        self.ctx = "clickMesh"
        self.current_tool = None
        self.enable_override_node = None
        self.display_type_node = None
        self.visibility_override_node = None

    def mesh_init(self, mesh):
        """AI is creating summary for mesh_init

        Args:
            mesh ([type]): [description]
        """
        # remove namespace from mesh name
        self.mesh_short_name = mesh.split(":")[-1] if ":" in mesh else mesh
        # naming variable
        self.mesh = mesh
        self.temp = "%s_temp" % self.mesh_short_name
        self.temp_skin = "%s_temp_zero" % self.mesh_short_name
        self.grp = "%s_BS_group" % self.mesh_short_name
        self.base_mesh = "%s_base_mesh" % self.mesh_short_name
        self.blendshape = self.mesh_short_name + "_anim_sculpt"
        self.target = "%s_BS_%s" % (
            self.mesh_short_name,
            mtools.get_time(3)[0],
        )
        self.enable_override_node = "%s_enable_override_node" % self.mesh_short_name
        self.display_type_node = "%s_display_type_node" % self.mesh_short_name
        self.visibility_override_node = "%s_visibility_override_node" % self.mesh_short_name
        
        # set up override attributes
        # enable override on mesh
        try:
            pm.PyNode(self.enable_override_node)
        except pm.MayaNodeError:
            self.enable_override_node = cmds.createNode(
                "floatConstant", n=self.enable_override_node
            )
            cmds.connectAttr(
                "%s.inFloat" % self.enable_override_node,
                "%s.overrideEnabled" % self.mesh,
            )
        cmds.setAttr("%s.inFloat" % self.enable_override_node, 1)

        # set mesh to reference
        try:
            pm.PyNode(self.display_type_node)
        except pm.MayaNodeError:
            self.display_type_node = cmds.createNode(
                "floatConstant", n=self.display_type_node
            )
            cmds.connectAttr(
                "%s.inFloat" % self.display_type_node,
                "%s.overrideDisplayType" % self.mesh,
            )
        cmds.setAttr("%s.inFloat" % self.display_type_node, 2)

        # set visibility  override
        try:
            self.visibility_override_node = pm.PyNode("visibility_override_node")
        except pm.MayaNodeError:
            self.visibility_override_node = cmds.createNode(
                "floatConstant", n=self.visibility_override_node
            )
            cmds.connectAttr(
                "%s.inFloat" % self.visibility_override_node,
                "%s.overrideVisibility" % self.mesh,
            )
        cmds.setAttr("%s.inFloat" % self.visibility_override_node, 1)

    def create_target(self):
        """create blendshape/target"""

        time = mtools.get_time(3)[0]
        # Create the needed meshes
        self.target = "%s_BS_%s" % (self.mesh_short_name, time)
        # Create Group
        if not cmds.objExists(self.grp):
            self.grp = cmds.group(em=True, n=self.grp)

        if not cmds.objExists(self.base_mesh):
            # Create base mesh
            base_mesh = cmds.duplicate(self.mesh, n=self.base_mesh)
            # get mesh origin shape
            relative = cmds.listRelatives(self.mesh, shapes=True)
            
            orig_shape = relative[1]
            self.mesh_shape = relative[0]

            pm.setAttr("%s.intermediateObject" % orig_shape, 0)

            # set base mesh
            orig_bs = "%s_orig_bs" % self.mesh_short_name
            cmds.blendShape(orig_shape, base_mesh, n=orig_bs)
            cmds.setAttr(orig_bs+".%s" % orig_shape.split(":")[-1], 1)
            cmds.DeleteHistory(self.base_mesh)

            # Parent base mesh to grp
            cmds.parent(base_mesh, self.grp)
            mtools.unlock_attribute(self.base_mesh)
            cmds.setAttr("%s.visibility" % self.base_mesh, 0)

            # set orig mesh as intermediate object
            pm.setAttr("%s.intermediateObject" % orig_shape, 1)

        # Create Target mesh
        if not cmds.objExists(self.target):
            bs = cmds.duplicate(self.base_mesh, smartTransform=True)
            cmds.rename(bs, self.target)
            cmds.setAttr("%s.visibility" % self.target, 0)

        # Create Blendshape node
        if not cmds.objExists(self.blendshape):
            cmds.blendShape(self.mesh, n=self.blendshape, par=True)
            if cmds.objExists("parallelBlender"):
                cmds.rename("parallelBlender", self.mesh_short_name + "_par")

        # get last target index
        self.number_of_blend_shapes = 0
        query_weights = cmds.blendShape(self.blendshape, q=True, w=1)
        if query_weights != None:
            self.number_of_blend_shapes = len(query_weights)

        # add target to blendshape
        cmds.blendShape(
            self.blendshape,
            edit=True,
            t=(self.mesh, self.number_of_blend_shapes + 1, self.target, 1.0),
        )

    def key_blendshape(self):
        """Key Blendshapes"""
        self.toggle_target()

        # Set all bs to 0 and key envelope(to keep a key in the timeline while the target are locked)

        cmds.setKeyframe(
            "%s.%s" % (self.blendshape, "envelope"), v=1, itt="linear", ott="linear"
        )
        for i in cmds.listRelatives(self.grp, c=True):
            if "BS" in i:
                cmds.setKeyframe(
                    "%s.%s" % (self.blendshape, i), v=0, itt="linear", ott="linear"
                )

            # Set current Bs to 1
            cmds.setKeyframe(
                self.blendshape,
                attribute=self.target,
                t=mtools.get_time(3)[0],
                v=1,
                itt="linear",
                ott="linear",
            )

        # set current Bs to 0 on previous and next frame
        if self.number_of_blend_shapes != 0:
            if self.get_previous_key() is not None:
                cmds.setKeyframe(
                    self.blendshape,
                    attribute=self.target,
                    t=self.get_previous_key(),
                    v=0,
                    itt="linear",
                    ott="linear",
                )
                if cmds.objExists(
                    "%s_BS_%s_reset" % (self.mesh_short_name, self.get_previous_key())
                ):
                    cmds.setKeyframe(
                        self.blendshape,
                        attribute="%s_BS_%s_reset"
                        % (self.mesh, self.get_previous_key()),
                        t=self.get_previous_key(),
                        v=0,
                        itt="linear",
                        ott="linear",
                    )
            if self.get_next_key() is not None:
                cmds.setKeyframe(
                    self.blendshape,
                    attribute=self.target,
                    t=self.get_next_key(),
                    v=0,
                    itt="linear",
                    ott="linear",
                )
                if cmds.objExists(
                    "%s_BS_%s_reset" % (self.mesh_short_name, self.get_next_key())
                ):
                    cmds.setKeyframe(
                        self.blendshape,
                        attribute="%s_BS_%s_reset"
                        % (self.mesh, self.get_previous_key()),
                        t=self.get_next_key(),
                        v=0,
                        itt="linear",
                        ott="linear",
                    )

    def edit_mesh(self):
        """Enable sculpt mode"""

        # set previously used tool
        if self.current_tool:
            cmds.setToolTo(self.current_tool)
        else:
            mel.eval("SetMeshGrabTool")

        # create meshes
        self.target = "%s_BS_%s" % (
            self.mesh_short_name,
            mtools.get_time(3)[0],
        )
        self.create_temp()
        self.create_skin_temp()
        res_name = self.target + "_reset"
        if cmds.objExists(res_name):
            self.target = res_name
        self.current = self.target
        cmds.select(self.temp)

    def leave_edit_mesh(self):
        """Disable sculpt mode and update BS vertex position"""

        # get lastly used tool
        self.current_tool = cmds.currentCtx()

        self.target = self.current
        # Get position of all vertex
        temp_pos = self.get_vertex_pos(self.temp)
        base_mesh_pos = self.get_vertex_pos(self.base_mesh)
        mesh_pos = self.get_vertex_pos(self.temp_skin)

        # Compare vertex pos
        delta_pos = self.delta_vertex_pos(base_mesh_pos, mesh_pos, temp_pos)

        # Move vertex to their new pos
        self.move_vertex(self.target, delta_pos)

        # Clean up
        cmds.setAttr("%s.inFloat" % self.visibility_override_node, 1)
        cmds.setAttr("%s.visibility" % self.temp, 0)
        cmds.delete(self.temp)
        cmds.delete(self.temp_skin)
        cmds.select(self.blendshape)
        self.toggle_target(lock_=True)

        
        # set context that allow to click on the mesh to edit the mesh -> function : logic.SculptAnimLogic.cursor_on_mesh
        if cmds.draggerContext(self.ctx, exists=True):
            cmds.deleteUI(self.ctx)
            
        cmds.draggerContext(
            self.ctx,
            pressCommand=self.cursor_on_mesh,
            name=self.ctx,
            cursor="crossHair",
        )
        cmds.setToolTo(self.ctx)

    def create_temp(self):
        """Create a duplicate of the mesh with all his deformer"""
        # Create Temp mesh
        temp = cmds.duplicate(self.mesh, smartTransform=True)
        cmds.rename(temp, self.temp)
        mtools.unlock_attribute(self.temp)
        cmds.parent(self.temp, self.grp)
        cmds.setAttr("%s.envelope" % self.blendshape, 0)

        # not usefull but it look nicer to know where are your other key when you sculpt
        mykeys = self.get_target_keys()
        for key in mykeys:
            cmds.setKeyframe(self.temp, t=key, v=0, at="translateX")

    def create_skin_temp(self):
        """Create a duplicate of the mesh without PSD deformer"""
        # Create a mesh copy with skin only
        cmds.setAttr("%s.envelope" % self.blendshape, 0)

        cmds.duplicate(self.mesh, n=self.temp_skin, smartTransform=True)
        mtools.unlock_attribute(self.temp_skin)
        cmds.parent(self.temp_skin, self.grp)

        cmds.setAttr("%s.envelope" % self.blendshape, 1)
        cmds.setAttr("%s.visibility" % (self.temp_skin), 0)
        cmds.setAttr("%s.inFloat" % (self.visibility_override_node), 0)

    def reset_shape(self):
        """reset pose to default by moving vertex to orig pos"""
        self.toggle_target()
        # variable init
        self.target = "%s_BS_%s" % (
            self.mesh_short_name,
            mtools.get_time(3)[0],
        )
        res_name = self.target + "_reset"

        # if no existing target set one
        if not cmds.objExists(self.target):
            self.create_target()
            self.key_blendshape()

            for i in cmds.listRelatives(self.grp, c=True):
                if "BS" in i:
                    cmds.setAttr("%s.%s" % (self.blendshape, i), 0)
            cmds.setAttr("%s.%s" % (self.blendshape, self.target), 1)
            self.edit_mesh()

        # Create a sub BS to be able to reset pose and keep deformation on other frame the same
        else:
            if not cmds.objExists(self.temp):
                self.create_temp()
                self.create_skin_temp()
            if not cmds.objExists(res_name):
                # Create reset pose mesh
                reset = cmds.duplicate(self.base_mesh, smartTransform=True)
                reset = cmds.rename(reset, res_name)
                cmds.parent(reset, self.target)
                cmds.setAttr("%s.visibility" % (reset), 0)

                # Create reset blendshape node and add target
                query_weights = cmds.blendShape(self.blendshape, q=True, w=1)
                number_of_blend_shapes = len(query_weights)
                cmds.blendShape(
                    self.blendshape,
                    edit=True,
                    t=(self.mesh, number_of_blend_shapes + 1, reset, 1.0),
                    tangentSpace=True,
                )
                cmds.setKeyframe(
                    "%s.%s" % (self.blendshape, reset), v=1, itt="linear", ott="linear"
                )

                # Key reset blendshape value
                if self.get_previous_key() != None:
                    cmds.setKeyframe(
                        self.blendshape,
                        attribute=reset,
                        t=self.get_previous_key(),
                        v=0,
                        itt="linear",
                        ott="linear",
                    )
                if self.get_next_key() != None:
                    cmds.setKeyframe(
                        self.blendshape,
                        attribute=reset,
                        t=self.get_next_key(),
                        v=0,
                        itt="linear",
                        ott="linear",
                    )

            for i in cmds.listRelatives(self.grp, c=True):
                if "BS" in i:
                    cmds.setAttr("%s.%s" % (self.blendshape, i), 0)
            # Reset vertex Value
            reset_point = self.get_vertex_pos(self.temp_skin)
            self.move_vertex(self.temp, reset_point)
            cmds.select(self.temp)

            self.toggle_target(lock_=True)

    def get_next_key(self):
        """
            give closest next keyframe

        Returns:
            int: next keyframe
        """
        # Get current time and all frame with a key on it

        time = mtools.get_time(3)[0]
        mykeys = self.get_target_keys()

        if cmds.objExists(self.blendshape):
            mykeys = sorted(mykeys)
            # Compare current to frame and set the new time
            for j in mykeys:
                if time < j:
                    return j

    def get_previous_key(self):
        """
            give closest preceding keyframe

        Returns:
            int: preceding keyframe
        """
        # Get current time and all frame with a key on it
        time = mtools.get_time(3)[0]
        mykeys = self.get_target_keys()

        if cmds.objExists(self.blendshape):
            mykeys = sorted(mykeys, reverse=True)
            # Compare current to frame and return preceding frame
            for j in mykeys:
                if time > j:
                    return j

    def is_key(self):
        """Check if there's a target on the current frame"""
        time = mtools.get_time(3)[0]
        keyframe = self.get_target_keys()
        return keyframe is not None and time in keyframe

    def toggle_target(self, lock_=False):
        """Lock or unlock target attributes

        Args:
            lock_ (bool): if the target
                attribute should be locked or unlocked
        """
        attribute = cmds.listConnections(self.blendshape, type="animCurve")
        if attribute:
            for attr in attribute:
                attr = attr.replace(self.blendshape + "_", "")
                if attr != "envelope":
                    cmds.setAttr("%s.%s" % (self.blendshape, attr), lock=lock_)

    def get_target_keys(self):
        """return all key on which there's a key"""
        if cmds.objExists(self.blendshape):
            anim_curve = cmds.listConnections(self.blendshape, type="animCurve")
            keyframe = []
            for i in anim_curve:
                keys = cmds.keyframe(i, q=True)
                for k in keys:
                    if k not in keyframe:
                        keyframe.append(int(k))
            return keyframe

    def get_vertex_pos(self, object):
        """
            return position of all vertex of given mesh

        Args:
            object:

        Returns:
            list: position of all vertex
        """
        # Get mesh
        mesh = om.MSelectionList()
        mesh.add(object)
        # Get dagPath
        defaultPath = om.MDagPath()
        mesh.getDagPath(0, defaultPath)
        # Create point array
        point_array = om.MPointArray()
        # Get point position
        mesh_surface = om.MFnMesh(defaultPath)
        mesh_surface.getPoints(point_array, om.MSpace.kObject)
        # Add point to  pointList
        pointList = []
        for i in range(point_array.length()):
            pointList.append([point_array[i][0], point_array[i][1], point_array[i][2]])
        return pointList

    def delta_vertex_pos(self, zero_out, deform, deform_plus):
        """
            return the delta position of the deformed object and the base pos

        Args:
            zero_out (list): default pose mesh
            deform (list): deformed mesh pose without PSD
            deform_plus (list): deformed mesh pose with PSD

        Returns:
            list: delta position of vertex
        """
        # Compare point and add the result to new list
        pointlist = []
        for point in range(len(zero_out)):
            k = [
                (zero_out[point][0] + (deform_plus[point][0] - deform[point][0])),
                (zero_out[point][1] + (deform_plus[point][1] - deform[point][1])),
                (zero_out[point][2] + (deform_plus[point][2] - deform[point][2])),
            ]

            pointlist.append(k)
        return pointlist

    def move_vertex(self, mesh, pointList):
        """move vertex of given mesh to new position

        Todo:
            convert function to plugin and implement undo

        Args:
            mesh (str): mesh that vertex need to be updated
            pointList (list): deformed mesh pose without PSD
        """
        nodelist = mesh
        # create point array for target
        target_point = om.MPointArray()
        # add pointlist into the point array
        for pos in pointList:
            target_point.append(*pos)
        # Get target
        target = om.MSelectionList()
        target.add(nodelist)

        # Get dagPath
        targetpath = om.MDagPath()
        target.getDagPath(0, targetpath)

        # Set new vertex pos
        MFnMesh = om.MFnMesh(targetpath)
        MFnMesh.setPoints(target_point)

    def twenner_init(self):
        """initialize the tweener"""
        with pm.UndoChunk():
            self.prev_key = self.get_previous_key()
            self.next_key = self.get_next_key()

            # enable it only if there's at least 2 target
            if self.prev_key is not None and self.next_key is not None:
                self.toggle_target()

                # create target if needed
                if not self.is_key():
                    self.create_target()
                    self.key_blendshape()

                # variable init
                self.target = "%s_BS_%s" % (
                    self.mesh_short_name,
                    mtools.get_time(3)[0],
                )
                self.prev_tgt = "%s_BS_%s" % (self.mesh_short_name, self.prev_key)
                self.next_tgt = "%s_BS_%s" % (self.mesh_short_name, self.next_key)
                if cmds.objExists(
                    "%s_BS_%s_reset" % (self.mesh_short_name, self.prev_key)
                ):
                    self.prev_tgt = "%s_BS_%s_reset" % (
                        self.mesh_short_name,
                        self.prev_key,
                    )
                if cmds.objExists(
                    "%s_BS_%s_reset" % (self.mesh_short_name, self.next_key)
                ):
                    self.next_tgt = "%s_BS_%s_reset" % (
                        self.mesh_short_name,
                        self.next_key,
                    )

                # disable current target and key next and previous target
                cmds.setAttr("%s.%s" % (self.blendshape, self.target), 0)
                cmds.setKeyframe(
                    "%s.%s" % (self.blendshape, self.prev_tgt),
                    itt="linear",
                    ott="linear",
                )
                cmds.setKeyframe(
                    "%s.%s" % (self.blendshape, self.next_tgt),
                    itt="linear",
                    ott="linear",
                )
            else:
                cmds.inViewMessage(
                    amg="you need at least <hl>2</hl> blendshapes to use the tweener",
                    pos="botCenter",
                    fade=True,
                )

    def tweener_previs(self, tween_slider_value):
        """Change target value according to tweener value

        Args:
            tween_slider_value (int): slider value
        """
        cmds.undoInfo(swf=False)
        if self.prev_key is not None and self.next_key is not None:
            self.pre_value = (100 - float(tween_slider_value)) / 100
            self.post_value = (float(tween_slider_value)) / 100

            # disable autokeyframe to avoid the 'autoKeyframe;' in maya if you have the script editor opened
            cmds.autoKeyframe(state=False)

            cmds.setAttr("%s.%s" % (self.blendshape, self.prev_tgt), self.pre_value)
            cmds.setAttr("%s.%s" % (self.blendshape, self.next_tgt), self.post_value)
        cmds.undoInfo(swf=True)

    def tweener_key(self, tween_slider_value):
        """key the previsualized tween in target

        Args:
            tween_slider_value (int): tween value chose by user
        """

        with pm.UndoChunk():
            if self.prev_key is not None and self.next_key is not None:
                self.pre_value = (100 - float(tween_slider_value)) / 100
                self.post_value = (float(tween_slider_value)) / 100

                # Get position of all vertex
                cmds.autoKeyframe(state=True)
                cmds.setAttr("%s.%s" % (self.blendshape, self.prev_tgt), self.pre_value)
                cmds.setAttr(
                    "%s.%s" % (self.blendshape, self.next_tgt), self.post_value
                )
                if not cmds.objExists(self.temp):
                    self.create_temp()
                if not cmds.objExists(self.temp_skin):
                    self.create_skin_temp()

                temp_pos = self.get_vertex_pos(self.temp)
                base_mesh_pos = self.get_vertex_pos(self.base_mesh)
                mesh_pos = self.get_vertex_pos(self.temp_skin)

                # Compare vertex pos
                delta_pos = self.delta_vertex_pos(base_mesh_pos, mesh_pos, temp_pos)

                # Move vertex to their new pos
                self.move_vertex(self.target, delta_pos)

                # Clean up
                cmds.setAttr("%s.inFloat" % self.visibility_override_node, 1)
                cmds.setAttr("%s.visibility" % self.temp, 0)
                cmds.delete(self.temp_skin)
                cmds.delete(self.temp)
                cmds.select(self.blendshape)

                cmds.setAttr("%s.%s" % (self.blendshape, self.prev_tgt), 0)
                cmds.setAttr("%s.%s" % (self.blendshape, self.next_tgt), 0)
                cmds.setAttr("%s.%s" % (self.blendshape, self.target), 1)

                self.toggle_target(lock_=True)

    def tweener_pos_update(self):
        """Return value according to how close we are from the next target

        Returns:
            int: percentage between two frame
        """
        if cmds.objExists(self.grp):
            next_ = self.get_next_key()
            if next_ is None:
                return 0

            if cmds.objExists("%s_BS_%s_reset" % (self.mesh_short_name, next_)):
                self.next_tgt = "%s_BS_%s_reset" % (self.mesh_short_name, next_)
            else:
                self.next_tgt = "%s_BS_%s" % (self.mesh_short_name, next_)
            self.post_value = cmds.getAttr("%s.%s" % (self.blendshape, self.next_tgt))
            return self.post_value * 100

    def delete_all_target(self):
        """Delete all node created for given mesh"""
        cmds.delete("%s_par" % self.mesh_short_name)
        cmds.delete(self.grp)
        cmds.setAttr("%s.inFloat" % self.display_type_node, 0)
        cmds.setAttr("%s.inFloat" % self.enable_override_node, 0)
        cmds.setAttr("%s.inFloat" % self.visibility_override_node, 0)
        cmds.setToolTo("selectSuperContext")

    def quit(self):
        """set overide to default"""

        try:
            cmds.setAttr("%s.inFloat" % self.display_type_node, 0)
            cmds.setAttr("%s.inFloat" % self.enable_override_node, 0)
            cmds.setAttr("%s.inFloat" % self.visibility_override_node, 0)
            pm.delete(self.visibility_override_node)
            pm.delete(self.enable_override_node)
            pm.delete(self.display_type_node)
        except:
            cmds.warning("sculpt anim mesh locking node doesn't exist")
        cmds.setToolTo("selectSuperContext")

    def delete_current_target(self):
        """Delete target on current frame"""

        self.toggle_target()
        time = mtools.get_time(3)[0]

        if self.is_key():
            # variable init
            self.prev_key = self.get_previous_key()
            self.next_key = self.get_next_key()
            blendshape_name = self.blendshape
            self.target = "%s_BS_%s" % (self.mesh_short_name, time)
            target_index = mtools.get_target_index(blendshape_name, self.target)
            mel.eval(
                "blendShapeDeleteTargetGroup %s %s" % (blendshape_name, target_index)
            )

            # remove key from all remaining target
            anim_curve = cmds.listConnections(self.blendshape, type="animCurve")
            keyframe = []
            for i in anim_curve:
                keys = cmds.keyframe(i, q=True)
                for k in keys:
                    if k not in keyframe:
                        keyframe.append(int(k))
                if time in keyframe:
                    cmds.cutKey(i, t=(time + 0.01, time - 0.01), clear=1)

            # update next key value on previous target
            if self.next_key is not None:
                cmds.setKeyframe(
                    self.blendshape,
                    attribute="%s_BS_%s" % (self.mesh_short_name, self.next_key),
                    t=self.prev_key,
                    v=0,
                    itt="linear",
                    ott="linear",
                )

            # delete target mesh
            cmds.delete(self.target)

        else:
            cmds.inViewMessage(
                amg="there is no target on this frame", pos="botCenter", fade=True
            )

        cmds.select(self.blendshape)
        self.toggle_target(lock_=True)

    def cursor_on_mesh(self):
        """Emit a signal if a click happen on a mesh
        Todo:
            Need to be converted to a real context file
        """

        # get cursor pos
        vp_x, vp_y, _ = cmds.draggerContext(self.ctx, query=True, anchorPoint=True)

        # init point and vector
        pos = om.MPoint()
        dir = om.MVector()
        hitpoint = om.MFloatPoint()

        # port to world coordinates
        omui.M3dView().active3dView().viewToWorld(int(vp_x), int(vp_y), pos, dir)
        pos_world = om.MFloatPoint(pos.x, pos.y, pos.z)

        # init dag for given mesh
        selectionList = om.MSelectionList()
        selectionList.add(self.mesh_shape)
        dagPath = om.MDagPath()
        selectionList.getDagPath(0, dagPath)

        # check for intersection
        fnMesh = om.MFnMesh(dagPath)
        intersection = fnMesh.closestIntersection(
            om.MFloatPoint(pos_world),
            om.MFloatVector(dir),
            None,
            None,
            False,
            om.MSpace.kWorld,
            99999,
            False,
            None,
            hitpoint,
            None,
            None,
            None,
            None,
            None,
        )
        if intersection is True:
            self.cntx_click_on_mesh.emit()
