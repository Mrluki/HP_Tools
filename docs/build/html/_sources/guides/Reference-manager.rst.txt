.. __Reference_manager:

Reference Manager
=================

.. meta::
   :description lang=en:
       How to use reference manager tool
       It will cache unload or load your references 

This tool allow you to cache unload or load your references. Handy when you need to see what your character are doing but the rigs are too heavy

.. _Reference_manager Launch in maya:

Launch in maya
--------------

If you have created a shelf when installing the tools you just have to press this icon

.. image:: /img/guide/reference_manager_icon.png

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


.. _Reference_manager Interface:

Interface
---------

.. image:: /img/guide/reference_manager_interface.png
    :align: center



1. **Search Bar**
    Input box that allow you to search for a particular reference name or state 

2. **Reference list**
    List all the reference in the scene and their current state.
  - Green: Loaded 
  - Orange: Cached 
  - Red: Unloaded 
  
3. **Right Click Menu**
    Pop up menu with additional actions

4. **Load All**
    Change state for all displayed reference

5. **Cache All**
    Change state for all displayed reference

6. **Unload All**
    Change state for all displayed reference

7. **Refresh button**
    update the scene reference (if for example a new reference is imported)

8. **Help**
   

Workflow
--------

Initialize tool
^^^^^^^^^^^^^^^

* Load the tool in maya

.. seealso::
       :ref:`Sculpt-anim Launch in maya`

Change State
^^^^^^^^^^^^

* Select the reference you want to change the state in the ui and click the state icon to chose a new state

.. image:: /gif/guide/reference_manager/change_state.gif


Filter
^^^^^^

* You can search for a reference by name 
* You can also filter by state with the ``@loaded``, ``@cached``, ``@unloaded`` commands


.. image:: /gif/guide/reference_manager/filter.gif