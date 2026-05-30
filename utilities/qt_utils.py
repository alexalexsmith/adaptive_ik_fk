try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui


def get_maya_main_widget():
    """
    Get Maya's main window using pure PySide (No MQtUtil required).
    """
    app = QtWidgets.QApplication.instance()
    for widget in app.topLevelWidgets():
        if widget.objectName() == "MayaWindow":
            return widget
    return None


class AbstractMayaToolWindow(QtWidgets.QWidget):
    """
    Abstract Base Class for Maya PySide UI.
    Inherits from QWidget for a clean, simple, non-tabbed UI layout.
    """
    WINDOW_NAME = "AbstractMayaQWidgetWindow"
    WINDOW_TITLE = "Abstract Maya Tool"
    STYLESHEET = ""

    def __init__(self, parent=get_maya_main_widget()):
        # 1. Close existing duplicate window before spawning a new one
        self.close_existing()

        # 2. Correctly initialize the QWidget base class
        super(AbstractMayaToolWindow, self).__init__(parent)

        # 3. Setup window properties
        self.setObjectName(self.WINDOW_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Window)  # Makes it a standalone floating window
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # Cleans up memory on close

        if self.STYLESHEET:
            self.setStyleSheet(self.STYLESHEET)

        # 4. Create a main layout for this widget to hold all child elements
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # 5. Trigger abstract workflow methods
        self.build_ui()
        self.socket_connections()

    def build_ui(self):
        """
        Placeholder for creating widgets.
        Must be overridden in the child class. Add elements to `self.main_layout`.
        """
        raise NotImplementedError("The build_ui() method must be implemented by the subclass.")

    def socket_connections(self):
        """
        Placeholder for connecting signals (buttons, sliders) to slots (functions).
        Must be overridden in the child class.
        """
        raise NotImplementedError("The socket_connections() method must be implemented by the subclass.")

    def close_existing(self):
        """
        Finds and closes any open windows sharing the same objectName.
        """
        maya_main = get_maya_main_widget()
        if not maya_main:
            return

        for child in maya_main.children():
            if child.objectName() == self.WINDOW_NAME:
                if hasattr(child, 'close'):
                    child.close()
                    child.deleteLater()

    @classmethod
    def display(cls):
        """
        A clean class method to instantiate and show the tool window properly.
        """
        instance = cls()
        instance.show()
        return instance