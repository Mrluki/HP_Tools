import maya.cmds as cmds
import maya.mel as mel
import os
import maya.OpenMaya as Om
import pymel.core as pm


def export_gpu(obj, time_range, file_name, path):
    """export given objects as a gpu cache

    Warning:
        This will write most of the material. If you cache a rig
        with pupil, they will appear white when loading the cached file

    Todo:
        Create a function that will write the material of the pupil and
        allow them to be recover later on

    Example::

        import Maya.misc_tools as mtools

        objects = [pSphere1, pSphere2]

        mtools.export_gpu(objects, [12,69], pSphere_gpuCache, ../My_folder)

    Args:
        obj (list or str): object to export
        range (list): start and end time
        file_name (str): name of the file to export
        path (str): path where to export
    """

    cmds.gpuCache(
        obj,
        startTime=time_range[0],
        endTime=time_range[1],
        optimizationThreshold=40000,
        writeMaterials=True,
        dataFormat="ogawa",
        fileName=file_name,
        directory=path,
        saveMultipleFiles=False,
    )


def import_gpu(file_name, path):
    """import given file as gpu cache

    Warning:
        The file need to be a .abc

    Example::

        import Maya.misc_tools as mtools

        mtools.import_gpu(pSphere_gpuCache, ../My_folder)

    Args:
        file_name (str): name of the file
        path (str): path of the file
    """

    dir_path = path
    files = os.listdir(dir_path)
    grp_name = file_name + "_cache"

    if cmds.objExists(grp_name):
        cmds.delete(grp_name)
    groupe = cmds.group(n=grp_name, em=True)
    for f in files:
        abc_path = os.path.abspath(os.path.join(dir_path, f))
        node_name = f[:-4]
        node = cmds.createNode("gpuCache", n=node_name + "cache")
        cache_parent = cmds.listRelatives(node, p=True, pa=True)
        cache = cmds.rename(cache_parent, node_name)
        cmds.setAttr(cache + ".cacheFileName", abc_path, type="string")
        cmds.parent(cache, groupe, relative=True)


def get_namespace(objects):
    """get namespace of all selected object

    Example::

        import Maya.misc_tools as mtools

        object = 'Gerard:master'

        namespace = mtools.get_namespace(object)

    Args:
        objects (list): object to get the namespace from

    Returns:
        list: all namespaces
    """

    namespaces = []
    for obj in objects:
        if cmds.referenceQuery(obj, isNodeReferenced=True):
            name_space = obj.split(":")[0] + ":"
            if name_space not in namespaces:
                namespaces.append(name_space)
    return namespaces


def get_reference(state):
    """return all reference in the given state (loaded/unloaded)

    Example::

        import Maya.misc_tools as mtools

        loaded_ref = mtools.get_reference(True)
        unloaded_ref = mtools.get_reference(False)

    Args:
        state (bool): ``True`` for loaded reference ``False`` for unloaded

    Returns:
        list: references in given state
    """

    all_ref = cmds.ls(type="reference")
    references = []
    for ref in all_ref:
        if ref == "sharedReferenceNode":
            continue
        else:
            if (
                state
                and cmds.referenceQuery(ref, il=True)
                or not state
                and not cmds.referenceQuery(ref, il=True)
            ):
                references.append(ref)
    return references


def get_target_index(blendshape, target):
    """Get index of specified target in blendshape

    Example::

        import Maya.misc_tools as mtools

        target = 'pSphere1_deformed'
        blendshape = 'pSphere1.blendshape'

        target_index = get_target_index(blendshape, target)

    Args:
        blendshape: Blendshape containing the target
        target: target name

    Returns:
        int: index of given target
    """

    indices = cmds.getAttr("{}.w".format(blendshape), mi=True) or []
    for indice in indices:
        alias = cmds.aliasAttr("{}.w[{}]".format(blendshape, indice), q=True)
        if alias == target:
            return indice
    raise RuntimeError(
        "Target {} does not exist on blendShape {}".format(target, blendshape)
    )


def get_time(mode):
    """give time range

    Example::

        import Maya.misc_tools as mtools

        time_range = mtools.get_time(1)
        time_slider = mtools.get_time(2)
        current_frame = mtools.get_time(3)[0]

    Args:
        time_range (int): accepted input are ``1``, ``2`` , ``3`` 1 = Time
            slider , 2 = Start-end, 3 = Current frame

    Returns:
        list: time range
    """

    if mode == 1:
        time = [
            int(cmds.playbackOptions(q=True, min=True)),
            int(cmds.playbackOptions(q=True, max=True)),
        ]
    elif mode == 2:
        time = [
            int(cmds.playbackOptions(q=True, ast=True)),
            int(cmds.playbackOptions(q=True, aet=True)),
        ]
    elif mode == 3:
        time = [int(cmds.currentTime(query=True))]
    return time


def import_plug(**plugin):
    """Import specified plugin in maya

    Warning:
        accepted input are ``abc``, ``gpu``
    Args:
        **plugin: plugin name
    """

    for key, value in plugin.items():
        if key == "abc":
            # Load AbcExport plugin
            if not cmds.pluginInfo("AbcExport", q=True, l=True):
                try:
                    cmds.loadPlugin("AbcExport", quiet=True)
                except Exception:
                    raise Exception("Error loading AbcExport plugin!")
        if key == "gpu":
            # Load gpuCache plugin
            if not cmds.pluginInfo("gpuCache", q=True, l=True):
                try:
                    cmds.loadPlugin("gpuCache", quiet=True)
                except Exception:
                    raise Exception("Error loading gpuCache plugin!")


def visibility_check(obj):
    """check the visibility of given objects

    Note:
        There is multiple way in maya to make an object invisible this function
        should be able to return the visibility state in most cases.

    Example::

        import Maya.misc_tools as mtools

        visible_object = []
        invisible_object = []

        objects = ['Psphere1','Psphere2','Psphere3']

        for object in objects:
            if mtools.visibility_check(object) is True:
                visible_object.append(object)
            else:
                invisible_object.append(object)

    Args:
        obj (str): object to be tested

    Returns:
        Boolean: The visibility of one object
    """
    sel_list = Om.MSelectionList()
    sel_list.add(obj)
    dag_path = Om.MDagPath()
    component = Om.MObject()
    sel_list.getDagPath(0, dag_path, component)
    return Om.MDagPath.isVisible(dag_path)


def unlock_attribute(mesh):
    """Unlock all locked attribute from mesh

        Example::

            import Maya.misc_tools as mtools

            object = 'pSphere1'

            unlocked_attribute = mtools.unlock_attribute(object)

    Args:
        mesh (str): mesh to unlock

    Returns:
        [list]: attribute that were unlocked
    """

    locked_attribute = cmds.listAttr(mesh, l=True)
    if locked_attribute is not None:
        for attribute in locked_attribute:
            cmds.setAttr("%s.%s" % (mesh, attribute), lock=0)
        return locked_attribute


def lock_attribute(mesh, attributes):
    """lock given attributes

        Example::

            import Maya.misc_tools as mtools

            object = 'pSphere1'
            attributes = ['visibility','translateX']

            mtools.lock_attribute(object,attributes)

    Args:
        mesh (str): mesh
        attributes (list): attributes to unlock
    """
    for attribute in attributes:
        cmds.setAttr("%s.%s" % (mesh, attribute), lock=1)


def get_display_setting():
    """get maya viewport display settings

        Example::

            import Maya.misc_tools as mtools

            viewport_settings = mtools.get_display_setting()

    Returns:
        list: all maya viewport display settings
    """
    panel = "modelPanel4"
    cv = pm.modelEditor(panel, q=1, cv=1)
    hud = pm.modelEditor(panel, q=1, hud=1)
    hos = pm.modelEditor(panel, q=1, hos=1)
    sel = pm.modelEditor(panel, q=1, sel=1)
    grid = pm.modelEditor(panel, q=1, grid=1)
    hulls = pm.modelEditor(panel, q=1, hulls=1)
    planes = pm.modelEditor(panel, q=1, planes=1)
    lights = pm.modelEditor(panel, q=1, lights=1)
    joints = pm.modelEditor(panel, q=1, joints=1)
    fluids = pm.modelEditor(panel, q=1, fluids=1)
    pivots = pm.modelEditor(panel, q=1, pivots=1)
    cameras = pm.modelEditor(panel, q=1, cameras=1)
    handles = pm.modelEditor(panel, q=1, handles=1)
    strokes = pm.modelEditor(panel, q=1, strokes=1)
    n_cloths = pm.modelEditor(panel, q=1, nCloths=1)
    n_rigids = pm.modelEditor(panel, q=1, nRigids=1)
    dynamics = pm.modelEditor(panel, q=1, dynamics=1)
    locators = pm.modelEditor(panel, q=1, locators=1)
    textures = pm.modelEditor(panel, q=1, textures=1)
    deformers = pm.modelEditor(panel, q=1, deformers=1)
    follicles = pm.modelEditor(panel, q=1, follicles=1)
    ik_handles = pm.modelEditor(panel, q=1, ikHandles=1)
    polymeshes = pm.modelEditor(panel, q=1, polymeshes=1)
    dimensions = pm.modelEditor(panel, q=1, dimensions=1)
    image_plane = pm.modelEditor(panel, q=1, imagePlane=1)
    n_particles = pm.modelEditor(panel, q=1, nParticles=1)
    clip_ghosts = pm.modelEditor(panel, q=1, clipGhosts=1)
    controllers = pm.modelEditor(panel, q=1, controllers=1)
    nurbs_curves = pm.modelEditor(panel, q=1, nurbsCurves=1)
    hair_systems = pm.modelEditor(panel, q=1, hairSystems=1)
    manipulators = pm.modelEditor(panel, q=1, manipulators=1)
    motion_trails = pm.modelEditor(panel, q=1, motionTrails=1)
    plugin_shapes = pm.modelEditor(panel, q=1, pluginShapes=1)
    nurbs_surfaces = pm.modelEditor(panel, q=1, nurbsSurfaces=1)
    grease_pencils = pm.modelEditor(panel, q=1, greasePencils=1)
    subdiv_surfaces = pm.modelEditor(panel, q=1, subdivSurfaces=1)
    particle_instancers = pm.modelEditor(panel, q=1, particleInstancers=1)
    dynamic_constraints = pm.modelEditor(panel, q=1, dynamicConstraints=1)

    return [
        cv,
        hud,
        hos,
        sel,
        grid,
        hulls,
        planes,
        lights,
        joints,
        fluids,
        pivots,
        cameras,
        handles,
        strokes,
        dynamics,
        n_cloths,
        n_rigids,
        locators,
        textures,
        controllers,
        deformers,
        follicles,
        polymeshes,
        ik_handles,
        dimensions,
        image_plane,
        n_particles,
        clip_ghosts,
        nurbs_curves,
        hair_systems,
        manipulators,
        motion_trails,
        plugin_shapes,
        nurbs_surfaces,
        grease_pencils,
        subdiv_surfaces,
        particle_instancers,
        dynamic_constraints,
    ]


def set_display_setting(display_settings):
    """set maya viewport display settings

    Example::

            import Maya.misc_tools as mtools

            mtools.set_display_setting(viewport_settings)

    Args:
        display_settings (list): maya viewport display settings
    """
    panel = "modelPanel4"
    pm.modelEditor(panel, e=1, cv=display_settings[3])
    pm.modelEditor(panel, e=1, hud=display_settings[35])
    pm.modelEditor(panel, e=1, hos=display_settings[36])
    pm.modelEditor(panel, e=1, sel=display_settings[37])
    pm.modelEditor(panel, e=1, hulls=display_settings[4])
    pm.modelEditor(panel, e=1, grid=display_settings[34])
    pm.modelEditor(panel, e=1, planes=display_settings[7])
    pm.modelEditor(panel, e=1, lights=display_settings[8])
    pm.modelEditor(panel, e=1, cameras=display_settings[9])
    pm.modelEditor(panel, e=1, joints=display_settings[11])
    pm.modelEditor(panel, e=1, fluids=display_settings[16])
    pm.modelEditor(panel, e=1, pivots=display_settings[25])
    pm.modelEditor(panel, e=1, nCloths=display_settings[19])
    pm.modelEditor(panel, e=1, nRigids=display_settings[21])
    pm.modelEditor(panel, e=1, handles=display_settings[26])
    pm.modelEditor(panel, e=1, strokes=display_settings[28])
    pm.modelEditor(panel, e=1, dynamics=display_settings[14])
    pm.modelEditor(panel, e=1, locators=display_settings[23])
    pm.modelEditor(panel, e=1, textures=display_settings[27])
    pm.modelEditor(panel, e=1, locators=display_settings[38])
    pm.modelEditor(panel, e=1, polymeshes=display_settings[5])
    pm.modelEditor(panel, e=1, ikHandles=display_settings[12])
    pm.modelEditor(panel, e=1, deformers=display_settings[13])
    pm.modelEditor(panel, e=1, follicles=display_settings[18])
    pm.modelEditor(panel, e=1, controllers=display_settings[0])
    pm.modelEditor(panel, e=1, nurbsCurves=display_settings[1])
    pm.modelEditor(panel, e=1, imagePlane=display_settings[10])
    pm.modelEditor(panel, e=1, nParticles=display_settings[20])
    pm.modelEditor(panel, e=1, dimensions=display_settings[24])
    pm.modelEditor(panel, e=1, clipGhosts=display_settings[31])
    pm.modelEditor(panel, e=1, hairSystems=display_settings[17])
    pm.modelEditor(panel, e=1, nurbsSurfaces=display_settings[2])
    pm.modelEditor(panel, e=1, motionTrails=display_settings[29])
    pm.modelEditor(panel, e=1, pluginShapes=display_settings[30])
    pm.modelEditor(panel, e=1, manipulators=display_settings[33])
    pm.modelEditor(panel, e=1, subdivSurfaces=display_settings[6])
    pm.modelEditor(panel, e=1, greasePencils=display_settings[32])
    pm.modelEditor(panel, e=1, particleInstancers=display_settings[15])
    pm.modelEditor(panel, e=1, dynamicConstraints=display_settings[22])


def show_geo_only():
    """Hide everything except geometry"""
    panel = "modelPanel4"
    pm.modelEditor(panel, e=1, cv=0)
    pm.modelEditor(panel, e=1, hud=1)
    pm.modelEditor(panel, e=1, hos=0)
    pm.modelEditor(panel, e=1, sel=0)
    pm.modelEditor(panel, e=1, grid=0)
    pm.modelEditor(panel, e=1, hulls=0)
    pm.modelEditor(panel, e=1, planes=0)
    pm.modelEditor(panel, e=1, lights=0)
    pm.modelEditor(panel, e=1, joints=0)
    pm.modelEditor(panel, e=1, fluids=0)
    pm.modelEditor(panel, e=1, pivots=0)
    pm.modelEditor(panel, e=1, cameras=0)
    pm.modelEditor(panel, e=1, nCloths=0)
    pm.modelEditor(panel, e=1, nRigids=0)
    pm.modelEditor(panel, e=1, handles=0)
    pm.modelEditor(panel, e=1, strokes=0)
    pm.modelEditor(panel, e=1, locators=0)
    pm.modelEditor(panel, e=1, dynamics=0)
    pm.modelEditor(panel, e=1, textures=0)
    pm.modelEditor(panel, e=1, ikHandles=0)
    pm.modelEditor(panel, e=1, deformers=0)
    pm.modelEditor(panel, e=1, follicles=0)
    pm.modelEditor(panel, e=1, polymeshes=1)
    pm.modelEditor(panel, e=1, imagePlane=0)
    pm.modelEditor(panel, e=1, nParticles=0)
    pm.modelEditor(panel, e=1, dimensions=0)
    pm.modelEditor(panel, e=1, clipGhosts=0)
    pm.modelEditor(panel, e=1, controllers=0)
    pm.modelEditor(panel, e=1, nurbsCurves=0)
    pm.modelEditor(panel, e=1, hairSystems=0)
    pm.modelEditor(panel, e=1, motionTrails=0)
    pm.modelEditor(panel, e=1, pluginShapes=1)
    pm.modelEditor(panel, e=1, manipulators=0)
    pm.modelEditor(panel, e=1, nurbsSurfaces=0)
    pm.modelEditor(panel, e=1, greasePencils=0)
    pm.modelEditor(panel, e=1, subdivSurfaces=0)
    pm.modelEditor(panel, e=1, particleInstancers=0)
    pm.modelEditor(panel, e=1, dynamicConstraints=0)
