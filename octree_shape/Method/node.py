import numpy as np
import open3d as o3d

from octree_shape.Data.node import Node


def toO3DAABB(
    aabb_min: np.ndarray,
    aabb_max: np.ndarray,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> o3d.geometry.AxisAlignedBoundingBox:
    o3d_aabb = o3d.geometry.AxisAlignedBoundingBox(
        min_bound=aabb_min,
        max_bound=aabb_max,
    )
    o3d_aabb.color = color

    return o3d_aabb


def toLeafO3DAABBList(
    node: Node,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> list:
    leaf_aabb_list = []

    if node.isLeaf:
        leaf_aabb_list.append(toO3DAABB(*node.toAABB(), color))
        return leaf_aabb_list

    for child_node in node.child_dict.values():
        leaf_aabb_list += toLeafO3DAABBList(child_node, color)

    return leaf_aabb_list
