import numpy as np
import open3d as o3d

from octree_shape.Data.node import Node
from octree_shape.Method.node import toLeafO3DAABBMesh, toLeafPcd


def renderOctree(
    node: Node,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> bool:
    leaf_aabb_mesh = toLeafO3DAABBMesh(node, color)

    o3d.visualization.draw_geometries([leaf_aabb_mesh])
    return True


def renderOctreePcd(
    node: Node,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> bool:
    leaf_pcd = toLeafPcd(node, color)

    o3d.visualization.draw_geometries([leaf_pcd])
    return True
