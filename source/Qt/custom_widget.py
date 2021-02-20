# PySide specific imports
from PySide2 import QtCore, QtGui, QtWidgets

# Software specific import
import maya.OpenMayaUI as Omui


# shiboken specific imports
from shiboken2 import wrapInstance

# resource specific import
import Qt.icon_rc

DEFAULT_CSS = """
QSizeGrip {
    image: None; 
    width: 13;
    height: 13;
}
QToolTip {
    border: 0px;
    background-color: #4d4d4d;
    color: white;
    padding: 4px;
    opacity: 160;
}
QPushButton {
    background-color: #4d4d4d;
    border: 0px;
}
QPushButton:hover{
    background-color: #5285a6;
}
QPushButton:pressed{
    background-color: #5285a6;
}
QSlider{
    background: transparent;
}
QSlider::groove:horizontal{
    height: 4px;
    background: #4a4a4a;
}
QSlider::handle:horizontal{
    width: 6px;
    background: #b8b8b8;
    margin: -4px 1;
    border-radius: 2px;
}
QSlider::handle:horizontal:hover{
    width: 6px;
    background: #62a0c7;
    margin: -4px 1;
    border-radius: 2px;
}
QSlider::handle:horizontal:pressed{
    width: 6px;
    background: #6caed8;
    margin: -3px 1;
    border-radius: 2px;
}
QLabel{
    font-family: 'Roboto';
    font-style: normal;
    font-size: 8pt;
}
QLineEdit {
    background-color: rgba(43, 43, 43, 200);
    border: 0px;
    border-radius: 5px; 
}

QListWidget {
    background-color: rgba(43, 43, 43, 200);
    border: 0px;
    border-radius: 5px; 
}

QScrollBar:vertical {              
    border: none;
    background:white;
    width:5px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #5d5d5d;
    min-height: 0px;
}
QScrollBar::add-line:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
    height: 0px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
    height: 0 px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}

QScrollBar:horizontal {              
    border: none;
    background:white;
    height:3px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:horizontal {
    background: #5d5d5d;
    min-width: 0px;
}
QScrollBar::add-line:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
    width: 0px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
    width: 0 px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
"""


class HTransparentDialogOnViewport(QtWidgets.QDialog):
    """Create a Custom Qwidget that will follow the maya Viewport while allowing
    transparency/semiTransparency

    .. image:: /gif/qt/HTransparentDialogOnViewport.gif
        :align: center

    |

    Todo:
        * Allow to minimize the window to different side (top left, top right, bottom left, bottom right)
        Done:
        * hide on maya prompt / maya calculation (reparented to maya main-window 
            and changing some param allowed to remove the visibility and mask fct )
        * Improve UI positioning when rescaling maya,something like ui pos * (viewport size full screen/viewport size current)

    Args:
        object_name (str): Name of the window that'll be created
        parent (HTransparentDialogOnViewport): Parent the window to an other
            HTransparentDialogOnViewport, ``optional``
        pos (list): Position where the windows will appear base on the maya
            viewport, ``defaults [0,0]``
        size (list): Default size of the created window , ``defaults [50,50]``
        visible (bool): If the windows should be visible when created or not,
            ``defaults False``
        orientation (str): Define the layout orientation onf the window,
            ``defaults horizontal``
        opacity (float): Define the opacity of the window, ``defaults 0.5``

    Danger:
        * ``parent`` need to be a HTransparentDialogOnViewport for it to work
        * ``orientation`` only accept 'horizontal' or 'vertical'
        * ``opacity`` value should be contain between 0.0 and 1.0

    Example::

        import Qt.custom_widget as cstm_widget

        TOOL_ICON = QtGui.QIcon(":/images/my_tool_icon.png")

        class MyCustomUI(QtCore.QObject):
                def __init__(self):
                    super(MyCustomUI, self).__init__()

                    # ui creation
                    self.main_ui = cstm_widget.HTransparentDialogOnViewport('anim sculpt',
                                                                        pos=[10, 10],
                                                                        size=[400, 30],
                                                                        tool_icon=TOOL_ICON,
                                                                        visible=True)
                    self.my_button = QtWidgets.QPushButton('press me')

                    # to add widget to the main ui use ``main_layout``
                    self.main_ui.main_layout.addWidget(self.my_button)


                    # to run function when user quit ui use ``ui_leaved``
                    self.main_ui.ui_leaved.connect(my_leave_function)

        UI = MyCustomUI()
        UI.main_ui.show()

    """

    # Signals
    ui_leaved = QtCore.Signal()

    def __init__(
        self,
        object_name,
        parent=None,
        pos=[0, 0],
        size=[50, 50],
        tool_icon=None,
        visible=False,
        orientation="horizontal",
        opacity=0.5,
    ):
        super(HTransparentDialogOnViewport, self).__init__(maya_main_window())

        # class attribute
        self.window_parent = parent

        self.custom_pos = pos
        self.default_pos = self.custom_pos
        self.custom_size = size
        self.default_size = self.custom_size
        self.tool_icon = tool_icon
        self.orientation = orientation
        self.opacity = opacity

        # Function instance attribute
        self.child = []
        self.child_visibility = {}
        self.move_enabled = False
        self.initial_mouse_pos = None
        self.global_mouse_pos = None
        self.viewport_zone = {}

        # install event filter
        self.main_window = maya_main_window()
        self.main_window.installEventFilter(self)
        self.viewport = get_viewport()
        self.viewport.installEventFilter(self)

        # window appearance
        self.setWindowTitle(object_name)
        self.setStyleSheet(DEFAULT_CSS)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.SplashScreen)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setToolTip("Move        Click + drag\nReset pos  Double click")
        # overlay placement
        self.viewport_size_old = self.viewport.size()

        self.viewport_pos = self.viewport.pos()
        self.viewport_pos = self.viewport.mapToGlobal(self.viewport_pos)
        pos = QtCore.QPoint(
            self.viewport_pos.x() + self.custom_pos[0],
            self.viewport_pos.y() + self.custom_pos[1],
        )

        size = QtCore.QSize(self.custom_size[0], self.custom_size[1])
        viewport_rect = QtCore.QRect(pos, size)
        self.setGeometry(viewport_rect)
        self.set_window_zone()
        self.window_pos_from_vp = self.get_window_pos_from_viewport()

        # Widgets init
        self.create_widgets()
        self.create_layout()
        self.create_context_menu()
        self.create_connections()

    def create_widgets(self):
        """Create all Widget of QWidget"""
        icon_min = QtGui.QIcon(":/images/arrow_down.png")
        icon_close = QtGui.QIcon(":/images/cross.png")
        icon_help = QtGui.QIcon(":/images/question.png")
        self.scale_window = QtWidgets.QSizeGrip(self)
        if self.window_parent is None:
            self.minimize_button = HButton(
                icon=icon_min,
                reduce_icon=-4,
                fixed=True,
                size=[17, 15],
                color="transparent",
            )
        else:
            self.minimize_button = HButton(
                icon=icon_close,
                reduce_icon=3,
                fixed=True,
                size=[13, 13],
                color="transparent",
            )

    def create_layout(self):
        """Create all layout of QWidget"""
        if self.orientation == "horizontal":
            self.main_layout = QtWidgets.QHBoxLayout()
            self.main_layout.setSpacing(10)
            self.main_layout.setContentsMargins(5, 5, 0, 5)

            self.scale_layout = QtWidgets.QVBoxLayout()
            self.scale_layout.addWidget(
                self.minimize_button, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignRight
            )
            self.scale_layout.setContentsMargins(0, 0, 0, 0)
            self.scale_layout.addStretch(1)
            self.scale_layout.addWidget(
                self.scale_window, 0, QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight
            )

            self.global_layout = QtWidgets.QHBoxLayout(self)
            self.global_layout.setContentsMargins(0, 0, 0, 0)
            self.global_layout.setSpacing(0)
            self.global_layout.addLayout(self.main_layout, 1)
            self.global_layout.addLayout(self.scale_layout, 0)

        if self.orientation == "vertical":
            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.setSpacing(3)
            self.main_layout.setContentsMargins(5, 3, 3, 5)

            self.scale_layout = QtWidgets.QVBoxLayout()
            self.scale_layout.addWidget(
                self.minimize_button, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignRight
            )
            self.scale_layout.setContentsMargins(0, 0, 0, 0)
            self.stretcher = QtWidgets.QSpacerItem(
                0, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
            self.scale_layout.addItem(self.stretcher)
            self.scale_layout.addWidget(
                self.scale_window, 0, QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight
            )

            self.global_layout = QtWidgets.QHBoxLayout(self)
            self.global_layout.setContentsMargins(0, 0, 0, 0)
            self.global_layout.setSpacing(0)
            self.global_layout.addLayout(self.main_layout, 1)
            self.global_layout.addLayout(self.scale_layout, 0)

    def create_connections(self):
        """Create all connection of QWidget"""
        if self.window_parent is None:
            self.minimize_button.clicked.connect(self.minimize)
        else:
            self.minimize_button.clicked.connect(self.ui_quit)
        self.action_quit.triggered.connect(self.ui_quit)

    def get_window_pos_from_viewport(self):
        """Return widget position relative to the viewport

        Returns:
            QtCore.Qpoint: widget position in viewport space
        """
        pos = self.mapToGlobal(QtCore.QPoint(0, 0))
        return self.viewport.mapFromGlobal(pos)

    def move_widget_with_viewport(self, event):
        """Bind widget position to viewport

        Warning:
            This function need to be completely rewritten
            see HTransparentDialogOnViewport Todo

        Args:
            event (QtCore.QEvent): pass QEvent to function
        """
        if event == QtCore.QEvent.Resize:
            if self.viewport_size_old != self.viewport.size():
                self.viewport_pos = self.viewport.pos()
                self.viewport_pos = self.viewport.mapToGlobal(self.viewport_pos)

                if self.current_position == "top-left":
                    pos = QtCore.QPoint(
                        self.viewport_pos.x() + self.window_pos_from_vp.x(),
                        self.viewport_pos.y() + self.window_pos_from_vp.y(),
                    )
                    self.move(pos)

                elif self.current_position == "left":
                    pos = QtCore.QPoint(
                        self.viewport_pos.x() + self.window_pos_from_vp.x(),
                        self.viewport_pos.y()
                        + self.window_pos_from_vp.y()
                        - (
                            self.viewport_size_old.height()
                            - self.viewport.size().height()
                        )
                        / 2,
                    )
                    self.move(pos)

                elif self.current_position == "bottom-left":
                    pos = QtCore.QPoint(
                        self.viewport_pos.x() + self.window_pos_from_vp.x(),
                        self.viewport_pos.y()
                        + self.window_pos_from_vp.y()
                        - (
                            self.viewport_size_old.height()
                            - self.viewport.size().height()
                        )
                        / 2,
                    )
                    self.move(pos)
                elif self.current_position == "top":
                    pos = QtCore.QPoint(
                        self.viewport_pos.x()
                        + self.window_pos_from_vp.x()
                        - (
                            self.viewport_size_old.width()
                            - self.viewport.size().width()
                        )
                        / 2,
                        self.viewport_pos.y() + self.window_pos_from_vp.y(),
                    )
                    self.move(pos)
                elif self.current_position == "center":
                    pos = QtCore.QPoint(
                        self.viewport_pos.x()
                        + self.window_pos_from_vp.x()
                        - (
                            self.viewport_size_old.width()
                            - self.viewport.size().width()
                        )
                        / 2,
                        self.viewport_pos.y()
                        + self.window_pos_from_vp.y()
                        - (
                            self.viewport_size_old.height()
                            - self.viewport.size().height()
                        )
                        / 2,
                    )
                    self.move(pos)
                elif self.current_position == "bottom":
                    pos = QtCore.QPoint(
                        self.viewport_pos.x()
                        + self.window_pos_from_vp.x()
                        - (
                            self.viewport_size_old.width()
                            - self.viewport.size().width()
                        )
                        / 2,
                        self.viewport_pos.y()
                        + self.window_pos_from_vp.y()
                        - (
                            self.viewport_size_old.height()
                            - self.viewport.size().height()
                        ),
                    )
                    self.move(pos)

                elif self.current_position == "top-right":
                    pos = QtCore.QPoint(
                        self.viewport_pos.x()
                        + self.window_pos_from_vp.x()
                        - (
                            self.viewport_size_old.width()
                            - self.viewport.size().width()
                        ),
                        self.viewport_pos.y() + self.window_pos_from_vp.y(),
                    )
                    self.move(pos)

                elif self.current_position == "right":
                    pos = QtCore.QPoint(
                        self.viewport_pos.x()
                        + self.window_pos_from_vp.x()
                        - (
                            self.viewport_size_old.width()
                            - self.viewport.size().width()
                        ),
                        self.viewport_pos.y()
                        + self.window_pos_from_vp.y()
                        - (
                            self.viewport_size_old.height()
                            - self.viewport.size().height()
                        )
                        / 2,
                    )
                    self.move(pos)

                elif self.current_position == "bottom-right":
                    pos = QtCore.QPoint(
                        self.viewport_pos.x()
                        + self.window_pos_from_vp.x()
                        - (
                            self.viewport_size_old.width()
                            - self.viewport.size().width()
                        ),
                        self.viewport_pos.y()
                        + self.window_pos_from_vp.y()
                        - (
                            self.viewport_size_old.height()
                            - self.viewport.size().height()
                        ),
                    )
                    self.move(pos)

                self.viewport_size_old = self.viewport.size()
                self.window_pos_from_vp = self.get_window_pos_from_viewport()

        elif event == QtCore.QEvent.Move:
            self.viewport_pos = self.viewport.pos()
            self.viewport_pos = self.viewport.mapToGlobal(self.viewport_pos)
            pos = QtCore.QPoint(
                self.viewport_pos.x() + self.window_pos_from_vp.x(),
                self.viewport_pos.y() + self.window_pos_from_vp.y(),
            )
            self.move(pos)
            self.window_pos_from_vp = self.get_window_pos_from_viewport()

    def set_window_zone(self):
        """Assign a zone to the widget depending of it's relative position to the viewport"""
        x_pos = self.get_window_pos_from_viewport().x() + self.size().width() / 2
        y_pos = self.get_window_pos_from_viewport().y() + self.size().height() / 2
        self.get_viewport_zone()

        if (
            x_pos < 0
            or y_pos < 0
            or x_pos > self.viewport.size().width()
            or y_pos > self.viewport.size().height()
        ):
            self.current_position = "not-in-vp"
        else:
            for position, zone in self.viewport_zone.items():
                if (
                    int(y_pos) <= int(zone.get("y")[1])
                    and int(y_pos) >= int(zone.get("y")[0])
                    and int(x_pos) <= int(zone.get("x")[1])
                    and int(x_pos) >= int(zone.get("x")[0])
                ):
                    self.current_position = position
        print self.current_position

    def get_viewport_zone(self):
        """define the boundary of the viewport zones"""
        self.viewport_zone["top-left"] = {
            "y": [0, self.viewport.size().height() / 3],
            "x": [0, self.viewport.size().width() / 3],
        }
        self.viewport_zone["left"] = {
            "y": [
                self.viewport.size().height() / 3,
                self.viewport.size().height() / 3 * 2,
            ],
            "x": [0, self.viewport.size().width() / 3],
        }
        self.viewport_zone["bottom-left"] = {
            "y": [self.viewport.size().height() / 3 * 2, self.viewport.size().height()],
            "x": [0, self.viewport.size().width() / 3],
        }
        self.viewport_zone["top"] = {
            "y": [0, self.viewport.size().height() / 3],
            "x": [
                self.viewport.size().width() / 3,
                self.viewport.size().width() / 3 * 2,
            ],
        }
        self.viewport_zone["center"] = {
            "y": [
                self.viewport.size().height() / 3,
                self.viewport.size().height() / 3 * 2,
            ],
            "x": [
                self.viewport.size().width() / 3,
                self.viewport.size().width() / 3 * 2,
            ],
        }
        self.viewport_zone["bottom"] = {
            "y": [self.viewport.size().height() / 3 * 2, self.viewport.size().height()],
            "x": [
                self.viewport.size().width() / 3,
                self.viewport.size().width() / 3 * 2,
            ],
        }
        self.viewport_zone["top-right"] = {
            "y": [0, self.viewport.size().height() / 3],
            "x": [self.viewport.size().width() / 3 * 2, self.viewport.size().width()],
        }
        self.viewport_zone["right"] = {
            "y": [
                self.viewport.size().height() / 3,
                self.viewport.size().height() / 3 * 2,
            ],
            "x": [self.viewport.size().width() / 3 * 2, self.viewport.size().width()],
        }
        self.viewport_zone["bottom-right"] = {
            "y": [self.viewport.size().height() / 3 * 2, self.viewport.size().height()],
            "x": [self.viewport.size().width() / 3 * 2, self.viewport.size().width()],
        }

    def minimize(self):
        """Minimize widget or hide it if windows is child"""
        # remember the current widget size
        self.custom_size = [self.size().width(), self.size().height()]

        # hide all the widget
        item1 = (self.main_layout.itemAt(i) for i in range(self.main_layout.count()))
        for item in item1:
            if item.widget() is not None:
                item.widget().hide()
        item2 = (self.scale_layout.itemAt(i) for i in range(self.scale_layout.count()))
        for item in item2:
            if item.widget() is not None:
                item.widget().hide()
        if self.orientation == "vertical":
            self.stretcher.changeSize(0, 0)

        # create the necessaries icons for the minimized window
        icon_max = QtGui.QIcon(":/images/arrow_up.png")
        icon_tool = self.tool_icon.pixmap(
            self.tool_icon.actualSize(QtCore.QSize(15, 15))
        )
        self.maximize_button = HButton(
            icon=icon_max,
            reduce_icon=-5,
            fixed=True,
            size=[20, 20],
            color="transparent",
        )
        self.tool_logo = QtWidgets.QLabel()
        self.tool_logo.setPixmap(
            icon_tool.scaled(
                15,
                15,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.FastTransformation,
            )
        )

        # connect button
        self.maximize_button.clicked.connect(self.maximize)

        # set layout
        self.global_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0, 0, 3, 0)
        self.global_layout.addWidget(self.tool_logo)
        self.global_layout.addWidget(self.maximize_button)
        self.setFixedSize(QtCore.QSize(40, 20))
        self.custom_pos = [self.pos().x(), self.pos().y()]

        # handle children
        for child in self.child:
            if child.isVisible():
                self.child_visibility[child] = True
                child.hide()
            else:
                self.child_visibility[child] = False

    def maximize(self):
        """Maximize widget"""
        self.maximize_button.deleteLater()
        self.tool_logo.deleteLater()

        # reshow all widget
        item1 = (self.main_layout.itemAt(i) for i in range(self.main_layout.count()))
        for item in item1:
            if item.widget() is not None:
                item.widget().show()
        item2 = (self.scale_layout.itemAt(i) for i in range(self.scale_layout.count()))
        for item in item2:
            if item.widget() is not None:
                item.widget().show()
        # reset the layout param
        self.global_layout.setSpacing(0)
        if self.orientation == "vertical":
            self.stretcher.changeSize(
                0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.setMinimumSize(0, 0)
        self.setMaximumSize(maya_main_window().size())
        pos = QtCore.QPoint(self.custom_pos[0], self.custom_pos[1])
        size = QtCore.QSize(self.custom_size[0], self.custom_size[1])
        viewport_rect = QtCore.QRect(pos, size)
        self.setGeometry(viewport_rect)

        # handle children
        for child, vis_state in self.child_visibility.iteritems():
            if vis_state:
                child.show()
            else:
                continue

    def _main_ui_context_menu_popup(self):
        """Make context menu appear on cursor pos"""
        self._ui_context_menu.popup(QtGui.QCursor.pos())

    def create_context_menu(self):
        """Create the context menu"""
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._main_ui_context_menu_popup)

        self._ui_context_menu = QtWidgets.QMenu()
        self._ui_context_menu.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self._ui_context_menu.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self._ui_context_menu.setWindowOpacity(0.8)

        self.action_quit = QtWidgets.QAction(self._ui_context_menu)
        self.action_quit.setObjectName("quit")
        self.action_quit.setText("Quit")

        self._ui_context_menu.addAction(self.action_quit)

    def ui_quit(self):
        """delete the tool when quiting it and emit signal"""

        self.ui_leaved.emit()

        if self.window_parent is None:
            self.deleteLater()
            for i in self.child:
                if not i:
                    self.child.remove(i)
        else:
            self.hide()
            self.visible = False

    def paintEvent(self, event):
        """Paint the semi transparent window

        Warning:
            Qt function, shouldn't be call elsewhere

        Args:
            event (Qtcore.QEvent): Qt event
        """
        painter = QtGui.QPainter(self)
        painter.setOpacity(self.opacity)
        painter.setBrush(QtGui.QColor(77, 77, 77))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(self.rect())

    def eventFilter(self, obj, event):
        """Create eventfilter to install on maya UI to detect UI event

        Warning:
            Qt function shouldn't be call elsewhere

        Args:
            obj (QtCore.QObject): Object on witch the event happen
            event (QtCore.QEvent): Qt event
        """
        # Main window events
        if obj == self.main_window:
            if event.type() == QtCore.QEvent.Move:
                self.move_widget_with_viewport(event.type())
                self.window_pos_from_vp = self.get_window_pos_from_viewport()
            if event.type() == QtCore.QEvent.Resize:
                self.viewport_size_old = self.viewport.size()

        # Viewport events
        if obj == self.viewport and event.type() == QtCore.QEvent.Resize:
            self.move_widget_with_viewport(event.type())
            self.window_pos_from_vp = self.get_window_pos_from_viewport()

        return False

    def mousePressEvent(self, mouse_event):
        """What to do in case of mouse press event

        Warning:
            Qt function shouldn't be call elsewhere

        Args:
            mouse_event (QtCore.QEvent): Qt mouse event
        """
        if mouse_event.button() == QtCore.Qt.LeftButton:
            self.initial_mouse_pos = self.pos()
            self.global_mouse_pos = mouse_event.globalPos()
            self.move_enabled = True

    def mouseReleaseEvent(self, mouse_event):
        """What to do in case of mouse release event

        Warning:
            Qt function shouldn't be call elsewhere

        Args:
            mouse_event (QtCore.QEvent): Qt mouse event
        """
        if self.move_enabled:
            self.move_enabled = False
        self.set_window_zone()
        self.window_pos_from_vp = self.get_window_pos_from_viewport()

    def mouseMoveEvent(self, mouse_event):
        """What to do in case of mouse move event

        Warning:
            Qt function shouldn't be call elsewhere

        Args:
            mouse_event (QtCore.QEvent): Qt mouse event
        """
        if self.move_enabled:
            diff = mouse_event.globalPos() - self.global_mouse_pos
            self.move(self.initial_mouse_pos + diff)

    def mouseDoubleClickEvent(self, mouse_event):
        """What to do in case of mouse doubleclick event

        Warning:
            Qt function shouldn't be call elsewhere

        Args:
            mouse_event (QtCore.QEvent): Qt mouse event
        """
        pos = QtCore.QPoint(
            self.viewport_pos.x() + self.default_pos[0],
            self.viewport_pos.y() + self.default_pos[1],
        )
        self.move(pos)
        size = QtCore.QSize(self.default_size[0], self.default_size[1])
        self.resize(size)

        self.custom_pos = self.default_pos
        self.custom_size = self.default_size
        self.set_window_zone()
        self.window_pos_from_vp = self.get_window_pos_from_viewport()


class HButton(QtWidgets.QPushButton):
    """Create a Custom QPushButton with quick param setup and auto scale icon.

    .. image:: /gif/qt/Hbutton.gif
        :align: center
        :width: 50%
    |


    Todo:
        Accept text and icon at the same time and make take also scalable

    Args:
        text (str): text to add to button
        color (str): color of the button Hex format ``defaults "#4d4d4d"``
        hover_color (str): color of the button when hovered Hex format ``defaults "#5285a6"``
        pressed_color (str): color of the button when pressed Hex format ``defaults "#5285a6"``
        checked_color (str): color of the button when checked Hex format ``defaults "#5285a6"``
        icon (QtGui.QIcon): Icon to put on the button(remove text) ``optional``
        size (list): size of the button if fixed = True, format : [width,height] ``optional``
        reduce_icon (int): reduce the size of the icon whithin the button ``defaults 0``
        pos (list): postition of the button within the layout format : [x,y] ``optional``
        checkable (Boolean, default is False): set the button as checkable ``defaults False``
        fixed (Boolean, default is False): make the button scalable ``defaults Fixed``

    Example::

        # Module specific imports
        import Qt.custom_widget as cstm_widget
        # PySide specific imports
        from PySide2 import QtCore
        from PySide2 import QtWidgets
        from PySide2 import QtGui

        win = QtWidgets.QDialog()

        layout = QtWidgets.QVBoxLayout(win)

        my_icon = QtGui.QIcon(":/image/my_icon.png")
        my_button = cstm_widget.HButton(icon=my_icon, color='#383838', size=[120, 30], fixed=True)
        layout.addWidget(my_button)

        win.show()
    """

    def __init__(
        self,
        text=None,
        color="#4d4d4d",
        hover_color="#5285a6",
        pressed_color="#5285a6",
        checked_color="#5285a6",
        icon=None,
        size=None,
        reduce_icon=0,
        pos=None,
        checkable=False,
        fixed=False,
    ):
        super(HButton, self).__init__()

        # attributes
        self.btn_color = color
        self.btn_hover_color = hover_color
        self.btn_pressed_color = pressed_color
        self.btn_checked_color = checked_color
        self.reduce_icon = reduce_icon

        if text:
            self.setText(text)
        if icon is None:
            self.icon = icon
        else:
            self.icon = icon
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(self.width(), self.height()))

        if pos is not None:
            self.move(pos[0], pos[1])

        if checkable:
            self.setCheckable(True)

        if fixed:
            if size is None:
                self.resize(20, 20)
                self.setFixedSize(20, 20)
            else:
                self.resize(size[0], size[1])
                self.setFixedSize(size[0], size[1])
        else:
            if size is None:
                self.resize(20, 20)
                self.setMinimumSize(20, 20)
            else:
                self.resize(size[0], size[1])
                self.setMinimumSize(size[0], size[1])

        self.pad = 2  # padding between the icon and the button frame
        self.min_size = 8  # minimum size of the icon

        # Style button
        self.set_style_sheet()
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)

    def set_style_sheet(self):
        """set the style sheet of the button according to user input or default
        style sheet

        ``defaults``:
        .. image:: /img/Qt/Hbutton_default_color.png
            :align: left
            :width: 100%
        """
        self.setStyleSheet(
            "QPushButton"
            "{"
            "background-color: %s;"
            "border: 0px;"
            "}"
            "QPushButton:hover"
            "{"
            "background-color: %s;"
            "}"
            "QPushButton:pressed"
            "{"
            "background-color: %s;"
            "}"
            "QPushButton:checked"
            "{"
            "background-color: %s;"
            "}"
            % (
                self.btn_color,
                self.btn_hover_color,
                self.btn_pressed_color,
                self.btn_checked_color,
            )
        )

    def set_icon(self, icon):
        """Set a new icon and update witch icon ``paintEvent`` is drawing

        Example::

            import Qt.custom_widget as cstm_widget

            icon = QtGui.QIcon(":/image/my_icon.png")

            my_button = cstm_widget.HButton()

        Args:
            icon (QtGui.QIcon): button icon
        """
        self.icon = icon
        self.setIcon(self.icon)

    def paintEvent(self, event):
        """Paint the button and an upscale icon according to it's current
        size

        Warning:
            Qt function, shouldn't be call elsewhere

        Args:
            event (Qtcore.QEvent): Qt event
        """
        h = None
        w = None

        qp = QtGui.QPainter()
        qp.begin(self)

        # get default style
        opt = QtWidgets.QStyleOptionButton()
        self.initStyleOption(opt)

        # scale icon to button size
        rect = opt.rect
        if self.icon is not None:
            try:
                if self.isDown():
                    self.setIcon(self.icon)
                    h = rect.height() - self.reduce_icon - 2
                    w = rect.width() - self.reduce_icon - 2
                else:
                    self.setIcon(self.icon)
                    h = rect.height() - self.reduce_icon
                    w = rect.width() - self.reduce_icon
            except AttributeError:
                pass
            icon_size = max(min(h, w) - 2 * self.pad, self.min_size)

            opt.iconSize = QtCore.QSize(icon_size, icon_size)
        # draw button
        self.style().drawControl(QtWidgets.QStyle.CE_PushButton, opt, qp, self)

        qp.end()


class HQSlider(QtWidgets.QSlider):
    """Create a Custom QSlider

    Note:
        Nothing fancy quick setup for default value and range

    Args:
        default (int): default slider value ``defaults 0``
        slider_range (list): range value of slider ``defaults [0,100]``
    """

    def __init__(self, default=0, slider_range=[0, 100]):
        super(HQSlider, self).__init__()
        self.setOrientation(QtCore.Qt.Horizontal)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        size_policy.setRetainSizeWhenHidden(False)

        self.setValue(default)

        self.range = slider_range
        self.setRange = self.setRange(self.range[0], self.range[1])
        self.setSizePolicy(size_policy)


class HIconLabel(QtWidgets.QWidget):
    """Create a widget that contain an icon and a Qlabel

    |

    .. image:: /img/Qt/HIconLabel.png
                :align: Center
    |

    Todo:
        * allow to chose the layout orientation
    Args:
        icon (pixmap): icon of the icon label ``needed``
        text (str): text of the icon label ``needed``
        size (list): size of the icon ``defaults [16,16]``
    Example::

        # Module specific imports
        import Qt.custom_widget as cstm_widget
        # PySide specific imports
        from PySide2 import QtCore
        from PySide2 import QtWidgets
        from PySide2 import QtGui

        win = QtWidgets.QDialog()

        layout = QtWidgets.QVBoxLayout(win)

        icon = QtGui.QIcon("")
        my_label = cstm_widget.HIconLabel(icon, 'my label with an icon', size=[30,30])
        layout.addWidget(my_label)

        win.show()

    """

    def __init__(self, icon, text, size=[16, 16]):
        """"""
        super(HIconLabel, self).__init__()

        self.icon = icon
        self.text = text
        self.size = size

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        """Create all widget of QWidget"""

        self.label_icon = QtWidgets.QLabel()
        if self.icon is not None:
            icon = self.icon.pixmap(
                self.icon.actualSize(QtCore.QSize(self.size[0], self.size[1]))
            )
            self.label_icon.setPixmap(
                icon.scaled(
                    self.size[0],
                    self.size[1],
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.FastTransformation,
                )
            )
        self.label_text = QtWidgets.QLabel(self.text)
        self.label_text.setFont(QtGui.QFont("Roboto", 10, weight=QtGui.QFont.Bold))

    def create_layout(self):
        """Create all Layout of QWidget"""
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        layout.addWidget(self.label_text)
        layout.addWidget(self.label_icon)
        layout.addSpacing(2)

        layout.addStretch()


class HStatus(QtWidgets.QWidget):
    """Allow to display a name and a status that can be change by pressing
        the status icon button

        |

        .. image:: /img/Qt/HStatus.gif
                    :align: Center
        |

        Example::

    # Module specific imports
    import Qt.custom_widget as cstm_widget
    # PySide specific imports
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from PySide2 import QtGui

    win = QtWidgets.QDialog()

    layout = QtWidgets.QVBoxLayout(win)

    reference = 'rig1RN'
    item_name = 'rig1'
    status = 'green'

    widget = cstm_widget.HStatus(
        object_name=reference, item_name=item_name, status=status
        )

    # if you want to change the status name in the pop up menu
    widget.green_action.setText('load')
    widget.orange_action.setText('cache')
    widget.red_action.setText('unload')

    layout.addWidget(my_label)

    win.show()

        Args:
            object_name (str): name of the widget
            item_name (str): name of the item that will be displayed
            item_status (str): current status of the item

    """

    # Signals
    status = QtCore.Signal(dict)

    def __init__(self, object_name=None, item_name=None, status="green"):
        super(HStatus, self).__init__()

        self.item_name = item_name
        self.item_status = status
        self.green_icon = QtGui.QIcon(":/images/green_icon.png")
        self.orange_icon = QtGui.QIcon(":/images/orange_icon.png")
        self.red_icon = QtGui.QIcon(":/images/red_icon.png")

        self.setObjectName(object_name)
        self.create_widgets()
        self.create_layout()
        self.create_status_menu()

        self.setStyleSheet(DEFAULT_CSS)

    def create_widgets(self):
        """Create all widget of QWidget"""
        self.iten_name_label = QtWidgets.QLabel(self.item_name)
        self.iten_name_label.setStyleSheet("background-color: transparent")
        self.iten_name_label.setFont(QtGui.QFont("Roboto", 8))
        self.status_icon = HButton(
            icon=self.green_icon,
            size=[15, 15],
            fixed=True,
            color="transparent",
        )
        self.change_status({self: self.item_status})
        self.status.connect(self.change_status)

    def create_layout(self):
        """Create all layout of QWidget"""
        self.item_layout = QtWidgets.QHBoxLayout(self)
        self.item_layout.setContentsMargins(2, 5, 2, 5)
        self.item_layout.addWidget(self.iten_name_label, 1)
        self.item_layout.addWidget(self.status_icon)

    def status_menu_popup(self):
        """Make context menu appear on cursor pos"""
        self.status_menu.popup(QtGui.QCursor.pos())

    def create_status_menu(self):
        """Populate status popup menu"""
        self.status_icon.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.status_icon.clicked.connect(self.status_menu_popup)

        self.status_menu = QtWidgets.QMenu()
        self.status_menu.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.status_menu.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.status_menu.setWindowOpacity(0.9)

        self.green_action = QtWidgets.QAction(self.status_menu)
        self.green_action.setObjectName("green")
        self.green_action.setText("green")
        self.green_action.setIcon(self.green_icon)
        self.green_action.triggered.connect(lambda: self.status.emit({self: "green"}))

        self.orange_action = QtWidgets.QAction(self.status_menu)
        self.orange_action.setObjectName("orange")
        self.orange_action.setText("orange")
        self.orange_action.setIcon(self.orange_icon)
        self.orange_action.triggered.connect(lambda: self.status.emit({self: "orange"}))

        self.red_action = QtWidgets.QAction(self.status_menu)
        self.red_action.setObjectName("red")
        self.red_action.setText("red")
        self.red_action.setIcon(self.red_icon)
        self.red_action.triggered.connect(lambda: self.status.emit({self: "red"}))

        self.status_menu.addAction(self.green_action)
        self.status_menu.addAction(self.orange_action)
        self.status_menu.addAction(self.red_action)

    def change_status(self, status_dict):
        """Change the status icon of the item

        Args:
            status_dict (dict): {widget, widget_status} the icon of the widget will be set
            to widget_status, accepted value for widget_status are ``green``, ``orange``, ``red``
        """
        for item, status in status_dict.items():
            if status == "green":
                self.status_icon.set_icon(self.green_icon)
                self.item_status = "green"
            if status == "orange":
                self.status_icon.set_icon(self.orange_icon)
                self.item_status = "orange"
            if status == "red":
                self.status_icon.set_icon(self.red_icon)
                self.item_status = "red"


# Qt_utils need to be put in own module when there will be a bit more


def maya_main_window():
    """Return the Maya main window widget as a Python object"""
    main_window_ptr = Omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def get_viewport():
    """Return Maya Viewport as a python object"""
    viewport_ptr = Omui.M3dView.active3dView().widget()
    return wrapInstance(long(viewport_ptr), QtWidgets.QWidget)


def selected_widget_qlist_widget(qlist_widget):
    """return all selected widget in QListWidget

    Args:
        qlist_widget (QtWidget.QlistWidget): list to get selected item from

    Returns:
        [list]: Selected widgets
    """
    selected_row = [x.row() for x in qlist_widget.selectedIndexes()]
    selected_widget = []
    for row in selected_row:
        item = qlist_widget.item(row)
        widget = qlist_widget.itemWidget(item)
        if widget is not None:
            selected_widget.append(widget)
    return selected_widget