"""
Maya attribute change callback utils
"""

import maya.api.OpenMaya as om

from adaptive_ik_fk.utilities import ik_fk_utils

# Global variable to hold the callback ID so we can remove it later
try:
    match_ik_fk_callback_id
except NameError:
    match_ik_fk_callback_id = None


def on_attribute_changed(msg, plug, other_plug, client_data):
    """
    Callback function that triggers when an attribute changes.
    """
    # Check if the attribute change is a 'set' action (value actually changed)
    if msg & om.MNodeMessage.kAttributeSet:
        # Get the name of the attribute that changed (e.g., 'translateX')
        attr_name = plug.partialName(useLongNames=True)

        # Filter for translate, rotate, and scale
        if any(transform_type in attr_name for transform_type in ['translate', 'rotate', 'scale']):
            m_object = plug.node()
            dep_node_fn = om.MFnDependencyNode(m_object)
            node_name = dep_node_fn.name()
            ik_fk_utils.match_ik_fk(node_name)


def register_transform_callback(node_name):
    global match_ik_fk_callback_id

    # Convert string name to MObject
    selection_list = om.MSelectionList()
    selection_list.add(node_name)
    m_object = selection_list.getDependNode(0)

    # Remove existing callback if it exists to prevent duplicates
    remove_callback()

    # Register the callback
    my_callback_id = om.MNodeMessage.addAttributeChangedCallback(m_object, on_attribute_changed)
    print(f"Successfully registered transform callback on: {node_name}")


def remove_callback():
    global match_ik_fk_callback_id
    if match_ik_fk_callback_id is not None:
        try:
            om.MMessage.removeCallback(match_ik_fk_callback_id)
            print("Transform callback successfully removed.")
            my_callback_id = None
        except RuntimeError:
            pass