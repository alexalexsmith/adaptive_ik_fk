"""
Math utilities
"""
from maya.api import OpenMaya
from maya import cmds


def get_matrices_offset_dict(parent, child):
    """get the matrices offset dict
    :param str parent: parent to relate offset to
    :param str child: children to compare
    :return dict: each key, named child, holding the offset matrix"""

    # Using open maya to do the matrix math to get the offset
    parent_matrix = OpenMaya.MMatrix(cmds.xform(parent, query=True, matrix=True, ws=True))
    # Removing shear and scale from the calculation to avoid distortions
    parent_transform = OpenMaya.MTransformationMatrix(parent_matrix)
    clean_parent_transform = OpenMaya.MTransformationMatrix()
    clean_parent_transform.setTranslation(parent_transform.translation(OpenMaya.MSpace.kWorld), OpenMaya.MSpace.kWorld)
    clean_parent_transform.setRotation(parent_transform.rotation(asQuaternion=True))
    clean_parent_matrix = clean_parent_transform.asMatrix()

    child_matrix = OpenMaya.MMatrix(cmds.xform(child, query=True, matrix=True, ws=True))
    # Removing shear and scale from the calculation to avoid distortions
    child_transform = OpenMaya.MTransformationMatrix(child_matrix)
    clean_child_transform = OpenMaya.MTransformationMatrix()
    clean_child_transform.setTranslation(child_transform.translation(OpenMaya.MSpace.kWorld), OpenMaya.MSpace.kWorld)
    clean_child_transform.setRotation(child_transform.rotation(asQuaternion=True))
    clean_child_matrix = clean_child_transform.asMatrix()

    # calculating the offset
    offset_mmatrix = clean_child_matrix * clean_parent_matrix.inverse()
    return list(offset_mmatrix)
