import numpy as np
import open3d as o3d

from octree_shape.Data.node import Node
from octree_shape.Method.node import toLeafO3DAABBMesh, toLeafPcd, toO3DAABBMesh


def renderNodes(
    node_list: list,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> bool:
    nodes_mesh = o3d.geometry.TriangleMesh()

    for node in node_list:
        aabb = node.toAABB(1.0)
        curr_leaf_aabb_mesh = toO3DAABBMesh(aabb[:3], aabb[3:], color)
        nodes_mesh += curr_leaf_aabb_mesh

    o3d.visualization.draw_geometries([nodes_mesh])
    return True


def renderNodesPcd(
    node_list: list,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> bool:
    node_centers = []

    for node in node_list:
        center = node.toCenter()
        node_centers.append(center)

    node_centers = np.vstack(node_centers)

    node_colors = np.broadcast_to(color, (node_centers.shape[0], 3))

    nodes_pcd = o3d.geometry.PointCloud()
    nodes_pcd.points = o3d.utility.Vector3dVector(node_centers)
    nodes_pcd.colors = o3d.utility.Vector3dVector(node_colors)

    o3d.visualization.draw_geometries([nodes_pcd])
    return True


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
