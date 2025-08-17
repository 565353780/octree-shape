import numpy as np
import open3d as o3d

from octree_shape.Data.node import Node
from octree_shape.Method.node import toLeafO3DAABBList


def renderOctree(
    node: Node,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> bool:
    aabb_list = toLeafO3DAABBList(node, color)

    o3d.visualization.draw_geometries(aabb_list)
    return True
