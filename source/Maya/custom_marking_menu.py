import maya.cmds as cmds
import maya.mel as mel


class Menu:
    """build or rebuild marking menu.

    Example::

        import Maya.custom_marking_menu as cstm_menu

        tool_menu = cstm_menu.Menu('my_menu_name', menu_build_fct)

    See also:
        Check the cmds documentation to see how to build your |cmds_doc|

        .. |cmds_doc| raw:: html

           <a href="https://download.autodesk.com/us/maya/2009help/commandspython/menuItem.html" target="_blank">marking menu items</a>.

        And this |bind_pose| on the subject where the code come from.

        .. |bind_pose| raw:: html

           <a href="https://bindpose.com/custom-marking-menu-maya-python/" target="_blank">article</a>

    Args:
         menu_name (str): name that you will give the menu
         fct (method): function that will add the item to the menu
    """

    def __init__(self, menu_name, fct):
        """"""
        self.menu_name = menu_name
        self.fct = fct
        self.removeOld()
        self.build()

    def build(self):
        """Creates the marking menu context and calls the buildMarkingMenu()
        method to populate it with all items.
        """
        menu = cmds.popupMenu(
            self.menu_name,
            mm=1,
            b=2,
            aob=1,
            sh=0,
            p="viewPanes",
            pmo=1,
            pmc=self.buildMarkingMenu,
        )

    def removeOld(self):
        """Checks if there is a marking menu with the given name and if so
        deletes it to prepare for creating a new one
        """

        if cmds.popupMenu(self.menu_name, ex=1):
            cmds.deleteUI(self.menu_name)

    def buildMarkingMenu(self, menu, parent):
        """This is where all the elements of the marking menu our built.

        Args:
            menu (cmds.popupMenu): popupMenu to parent item to
            parent : Declared for maya
        """

        self.fct(menu)


def sculpt_anim(menu):
    """Custom marking menu for the sculpt anim tool

    Example::

        import Maya.custom_marking_menu as cstm_menu

        sculp_anim_menu = cstm_menu.Menu('sculpt_anim', sculpt_anim)

    Args:
        menu (cmds.popupMenu): popupMenu to parent item to
    """
    # Radial positioned
    cmds.menuItem(
        p=menu, l="Sculpt", rp="N", c="mel.eval('SetMeshSculptTool')", i="Sculpt.png"
    )
    cmds.menuItem(
        p=menu, l="Relax", rp="NE", c="mel.eval('SetMeshRelaxTool')", i="Relax.png"
    )
    cmds.menuItem(
        p=menu, l="Smooth", rp="W", c="mel.eval('SetMeshSmoothTool')", i="Smooth.png"
    )
    cmds.menuItem(
        p=menu, l="Pull", rp="NW", c="mel.eval('SetMeshGrabTool')", i="Grab.png"
    )
    cmds.menuItem(
        p=menu,
        l="Vertex",
        rp="E",
        c="mel.eval('dR_DoCmd('modeVert')')",
        i="UVTkVertex.png",
    )
    cmds.menuItem(
        p=menu,
        l="Edge",
        rp="SE",
        c="mel.eval('dR_DoCmd('modeEdge');')",
        i="UVTkEdge.png",
    )
    cmds.menuItem(
        p=menu,
        l="Faces",
        rp="S",
        c="mel.eval('dR_DoCmd('modeFace');')",
        i="UVTkFace.png",
    )
    cmds.menuItem(
        p=menu,
        l="Object",
        rp="SW",
        c="mel.eval('dR_DoCmd('modeObject');')",
        i="object_NEX.png",
    )
