# PySide specific imports
import Reference_manager.logic
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtWebEngineWidgets

# Software specific import
import maya.cmds as cmds
import maya.OpenMayaUI as omui

# Python specific import
from functools import wraps
import os

# Module specific imports
import Qt.custom_widget as cstm_widget
import Qt.icon_rc

logic = Reference_manager.logic.ReferenceManagerLogic()

TOOL_ICON = QtGui.QIcon(":/images/person-silhouette.png")
ICON_HELP = QtGui.QIcon(":/images/question.png")


class ReferenceManager(QtCore.QObject):
    def __init__(self):
        super(ReferenceManager, self).__init__()

        self.widget_status_dict = {}

        self.create_widgets()
        self.create_layout()
        self.create_context_menu()
        self.create_connections()
        logic.get_rigs
        self.populate(logic.rigs)

    def create_widgets(self):
        """Create all widget of QWidget"""
        self.main_ui = cstm_widget.HTransparentDialogOnViewport(
            "rig manager",
            pos=[10, 10],
            size=[200, 200],
            tool_icon=TOOL_ICON,
            visible=True,
            orientation="vertical",
        )

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("search")
        self.search_bar.dragEnabled()
        self.search_bar.setFont(QtGui.QFont("Roboto", 8))
        self.search_bar.setStyleSheet(cstm_widget.DEFAULT_CSS)

        self.completer = QtWidgets.QCompleter(["@loaded", "@cached", "@unloaded"])
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.search_bar.setCompleter(self.completer)

        self.reference_list = QtWidgets.QListWidget()
        self.reference_list.setStyleSheet(cstm_widget.DEFAULT_CSS)
        self.reference_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )

        self.help_button = cstm_widget.HButton(
            icon=ICON_HELP,
            reduce_icon=0,
            fixed=True,
            size=[17, 15],
            color="transparent",
        )

    def create_layout(self):
        """Create all layout of QWidget"""
        self.main_ui.main_layout.addWidget(self.search_bar)
        self.main_ui.main_layout.addWidget(self.reference_list)
        self.main_ui.scale_layout.removeWidget(self.main_ui.scale_window)
        self.main_ui.scale_layout.removeItem(self.main_ui.stretcher)
        self.main_ui.scale_layout.addWidget(self.help_button)
        self.main_ui.scale_layout.addItem(self.main_ui.stretcher)
        self.main_ui.scale_layout.addWidget(
            self.main_ui.scale_window, 0, QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight
        )

    def create_connections(self):
        """Create all connections of QWidget"""
        self.search_bar.textChanged.connect(self.update_display)

        self.reference_list.customContextMenuRequested.connect(
            self.option_context_menu_popup
        )
        self.help_button.clicked.connect(self.show_help)
        
        self.all_live.triggered.connect(lambda: self.all_state("green"))
        self.all_cache.triggered.connect(lambda: self.all_state("orange"))
        self.all_unload.triggered.connect(lambda: self.all_state("red"))
        self.refresh.triggered.connect(self.refresh_list)

    def option_context_menu_popup(self):
        """Make context menu appear on cursor pos"""
        self.option_context_menu.popup(QtGui.QCursor.pos())

    def create_context_menu(self):
        """Create the context menus of QWidget"""
        self.reference_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.option_context_menu = QtWidgets.QMenu()
        self.option_context_menu.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.option_context_menu.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.option_context_menu.setWindowOpacity(0.8)

        self.green_icon = QtGui.QIcon(":/images/green_icon.png")
        self.orange_icon = QtGui.QIcon(":/images/orange_icon.png")
        self.red_icon = QtGui.QIcon(":/images/red_icon.png")
        self.refresh_icon = QtGui.QIcon(":/images/reset.png")

        self.all_live = QtWidgets.QAction(self.option_context_menu)
        self.all_live.setText("All live")
        self.all_live.setIcon(self.green_icon)

        self.all_cache = QtWidgets.QAction(self.option_context_menu)
        self.all_cache.setText("All Cached")
        self.all_cache.setIcon(self.orange_icon)

        self.all_unload = QtWidgets.QAction(self.option_context_menu)
        self.all_unload.setText("All Unloaded")
        self.all_unload.setIcon(self.red_icon)

        self.refresh = QtWidgets.QAction(self.option_context_menu)
        self.refresh.setText("refresh")
        self.refresh.setIcon(self.refresh_icon)

        self.option_context_menu.addAction(self.all_live)
        self.option_context_menu.addAction(self.all_cache)
        self.option_context_menu.addAction(self.all_unload)
        self.option_context_menu.addAction(self.refresh)

    def populate(self, references):
        """populate QlistWidget with HStatus widget for each reference

        Args:
            references ([dict]):{reference name, status of the reference}
        """
        for reference, status in references.items():
            file_path = cmds.referenceQuery(reference, filename=True)
            self.reference_ns = cmds.file(file_path, q=True, namespace=True)
            widget = cstm_widget.HStatus(
                object_name=reference, item_name=self.reference_ns, status=status
            )
            widget.status.connect(self.update_reference)
            reference_item = QtWidgets.QListWidgetItem()
            reference_item.setSizeHint(widget.sizeHint())
            self.reference_list.addItem(reference_item)
            self.reference_list.setItemWidget(reference_item, widget)
            self.widget_status_dict[widget] = status
            widget.green_action.setText("load")
            widget.orange_action.setText("cache")
            widget.red_action.setText("unload")

    def update_reference(self, status_dict):
        """update reference on user click

        Args:
            status_dict ([dict]): {widget, widget_status} the icon of the widget will be set
        """
        self.main_ui.hide()
        # will try/except running the function.But will always turn on the tool window
        try:
            selected_widget = cstm_widget.selected_widget_qlist_widget(
                self.reference_list
            )
            self.reference_list.clearSelection()
            if not selected_widget:
                selected_widget = [(status_dict.keys())[0]]
            logic.update_status(selected_widget, status_dict)
        except Exception:
            raise  # will raise original error
        finally:
            self.main_ui.show()

    def all_state(self, state):
        """change state for all visible item in QlistWidget

        Args:
            state ([str]): accepted value for widget_status are ``green``, ``orange``, ``red``
        """
        self.main_ui.hide()
        # will try/except running the function.But will always turn on the tool window
        try:
            for i in range(self.reference_list.count()):
                item = self.reference_list.item(i)
                if item.isHidden() is False:
                    item.setSelected(True)
            selected_widget = cstm_widget.selected_widget_qlist_widget(
                self.reference_list
            )
            logic.update_status(selected_widget, {selected_widget[0]: state})
        except Exception:
            raise  # will raise original error
        finally:
            self.main_ui.show()

    def update_display(self, text):
        """update widget displayed in Qlist widget

        Args:
            text ([str]): input from QlineEdit search_bar
        """
        items = [
            self.reference_list.item(item)
            for item in range(self.reference_list.count())
        ]
        for item in items:
            widget = self.reference_list.itemWidget(item)
            if text.lower().startswith("@l"):
                if widget.item_status == "green":
                    item.setHidden(False)
                else:
                    item.setHidden(True)
            elif text.startswith("@c"):
                if widget.item_status == "orange":
                    item.setHidden(False)
                else:
                    item.setHidden(True)
            elif text.startswith("@u"):
                if widget.item_status == "red":
                    item.setHidden(False)
                else:
                    item.setHidden(True)
            elif widget.item_name.lower().startswith(text.lower()):
                item.setHidden(False)
            else:
                item.setHidden(True)

    def refresh_list(self):
        """
        Clear and repopulate the Qlistwidget reference_list
        """
        self.reference_list.clear()
        logic.get_rigs()
        self.populate(logic.rigs)

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
                + r"/docs/build/html/guides/Reference-manager.html"
            )
        )
        self.window.main_layout.addWidget(self.webEngineView)

