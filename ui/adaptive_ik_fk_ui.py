"""
adaptive ik fk ui
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui

from maya.api import OpenMaya
from maya import cmds

from adaptive_ik_fk.utilities import qt_utils, ik_fk_utils
from adaptive_ik_fk import RESOURCES


class AdaptiveIKFKUI(qt_utils.AbstractMayaToolWindow):
    """
    UI
    """
    WINDOW_NAME = "AdaptiveIKFK"
    WINDOW_TITLE = "Adaptive IKFK"
    STYLESHEET = f"{RESOURCES}/neon_sunset.qss"

    def __init__(self):
        super(AdaptiveIKFKUI, self).__init__()
        self.selection_changed_callback = None
        self.attribute_changed_callback = None
        self.register_selection_changed_callback()
        self.info_label.setText(f"Adaptive IKFK ready")

    def build_ui(self):
        """
        Placeholder for creating widgets and tabs.
        Must be overridden in the child class.
        """
        self.info_label = QtWidgets.QLabel("")
        self.main_layout.addWidget(self.info_label)

    def socket_connections(self):
        """
        Placeholder for connecting signals (buttons, sliders) to slots (functions).
        Must be overridden in the child class.
        """
        return

    def register_selection_changed_callback(self):
        """
        register selection changed callback
        """
        self.remove_selection_callback()

        self.selection_changed_callback = OpenMaya.MEventMessage.addEventCallback(
            "SelectionChanged",
            self.on_selection_changed
        )

    def register_transform_callback(self, node_name):

        # Convert string name to MObject
        selection_list = OpenMaya.MSelectionList()
        selection_list.add(node_name)
        m_object = selection_list.getDependNode(0)

        # Remove existing callback if it exists to prevent duplicates
        self.remove_attribute_changed_callback()

        # Register the callback
        self.attribute_changed_callback = OpenMaya.MNodeMessage.addAttributeChangedCallback(m_object, self.on_attribute_changed)
        self.info_label.setText(f"active IKFK control: {node_name}")

    def on_selection_changed(self, *args):
        """
        Callback function that triggers every time the selection changes.
        """
        # Get the current selection
        selection = cmds.ls(sl=True)
        if len(selection) == 0:
            self.remove_attribute_changed_callback()
            self.info_label.setText(f"Adaptive IKFK ready")
            return

        if ik_fk_utils.get_snap_nodes(selection[0]):
            # make sure to match the position if it is not the active interpolation system
            # We just want to adjust the current pose with the opposing system
            ik_fk_utils.match_to_current_interpolation_setting(selection[0])
            self.register_transform_callback(selection[0])
        else:
            self.remove_attribute_changed_callback()
            self.info_label.setText(f"Adaptive IKFK ready")

    def on_attribute_changed(self, msg, plug, *args):
        """
        Callback function that triggers when an attribute changes.
        """
        # Check if the attribute change is a 'set' action (value actually changed)
        if msg & OpenMaya.MNodeMessage.kAttributeSet:
            # Get the name of the attribute that changed (e.g., 'translateX')
            attr_name = plug.partialName(useLongNames=True)

            # Filter for translate, rotate, and scale
            if any(transform_type in attr_name for transform_type in ['translate', 'rotate', 'scale']):
                m_object = plug.node()
                dep_node_fn = OpenMaya.MFnDependencyNode(m_object)
                node_name = dep_node_fn.name()
                ik_fk_utils.match_ik_fk(node_name)

    def remove_selection_callback(self):
        if self.selection_changed_callback is not None:
            try:
                OpenMaya.MMessage.removeCallback(self.selection_changed_callback)
                print("Selection Changed callback successfully removed.")
                self.selection_changed_callback = None
            except RuntimeError:
                pass

    def remove_attribute_changed_callback(self):
        if self.attribute_changed_callback is not None:
            try:
                OpenMaya.MMessage.removeCallback(self.attribute_changed_callback)
                print("Attribute Changed callback successfully removed.")
                self.attribute_changed_callback = None
            except RuntimeError:
                pass

    def closeEvent(self, event):
        """Remove all callback messages and remove ui from memory"""
        super(AdaptiveIKFKUI, self).closeEvent(event)
        self.remove_selection_callback()
        self.remove_attribute_changed_callback()
        self.deleteLater()
