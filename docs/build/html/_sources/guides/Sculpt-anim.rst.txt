.. __Sculpt-anim:

Sculpt Anim
===========

.. meta::
   :description lang=en:
       How to use anim sculpt tool
       It will create  and handle multiple blend shape on the same mesh

This tool allow you to sculpt any skinned mesh on one or multiple frame.

.. _Sculpt-anim Launch in maya:

Launch in maya
--------------

If you have created a shelf when installing the tools you just have to press this icon

.. image:: /img/guide/anim_sculpt.png

If not you can run this code in Maya script editor

.. code-block:: python

    import Sculpt_anim.ui as sculpt_anim

    try:
        UI.main_ui.deleteLater()
        UI.main_ui_quit()
    except (RuntimeError, TypeError, NameError):
        pass
    except Exception as e:
        cmds.warning(e)


    sculpt_anim_UI = sculpt_anim.SculptAnimUI()
    sculpt_anim_UI.main_ui.show()


.. _Sculpt-anim Interface:

Interface
---------

.. image:: /img/guide/interface.png

.. note::

   If no mesh were selected most of the interface will be disable
   please use the select mesh button (cf 2.) to enable them

1. **Current mesh**
    This box will display the current mesh selected. It's on this mesh that the
    edit will be performed.

2. **Select mesh**
    This button will be use to change the current mesh based on what you have selected
    when pressing it.

3. **Key**
    | If you press this button it will create a new target on the current frame.
    | It'll also light in ``red`` if there's already a key on the current frame.

4. **Reset mesh**
    This button will reset the mesh to it's default state.

5. **Tweener**
    | The handle will move accordingly to your positioning between two targets
    | You can move the handle to be more close from the previous or next target
    | Releasing the handle will set a new key

5. **Edit mode**
    | This will enable the edit mode, you have to activate it in order to edit the mesh
    | It will light in ``yellow`` when you are in edit mode
    | If there is no key when you toggle the edit mode a key will be set

7. **Delete Target**
    This will delete the current target
    you can right click the button to delete all target

8. **Help**
    Open the documentation inside maya and press the select mesh button

Workflow
--------

Initialize tool
^^^^^^^^^^^^^^^

* Load the tool in maya

.. seealso::
       :ref:`Sculpt-anim Launch in maya`

* Select the mesh you want to edit and press the :ref:`select mesh<Sculpt-anim Interface>` button,
      this will enable all the tools

.. image:: /gif/guide/sculpt-anim/select_mesh.gif

.. warning::
    | It is not currently possible to edit multiple meshes at the same time.
    | If you have multiple meshes selected when pressing the button the first one will be set as Current mesh. (:ref:`cf 1.<Sculpt-anim Interface>`)

Edit Mesh
^^^^^^^^^

* Go to a frame where you want to edit your mesh and press the :ref:`edit mode<Sculpt-anim Interface>` button 
  This will allow you to start sculpting your mesh

.. image:: /gif/guide/sculpt-anim/edit_mesh.gif

|

* Once your done editing this frame moving in the timeline will automatically bake the target

.. image:: /gif/guide/sculpt-anim/leave_edit_mesh.gif

.. note::
       If you want to leave the edit mode without changing the current frame you can also press the :ref:`edit mode<Sculpt-anim Interface>` button again

* You can edit the mesh with all the classic mesh edit maya tool. This tool also come with his own marking menu 
  that you can summon |:ghost:| by pressing the mouse middle click button

.. image:: /gif/guide/sculpt-anim/brush_wheel.gif

|

* At any moment you can reset the mesh to it's default deformation by using the :ref:`reset<Sculpt-anim Interface>` button

.. image:: /gif/guide/sculpt-anim/reset.gif

.. note:: This will only reset the deformation performed by the sculpt anim tool

Tweener
^^^^^^^

* | You can use the tweener between two frames it will favor on or the other.
  | Releasing the handle will set a key

.. image:: /gif/guide/sculpt-anim/tweener.gif

.. warning::
    | Using the tweener on a frame with an existing target on it will delete the target. ``this action in undoable``
