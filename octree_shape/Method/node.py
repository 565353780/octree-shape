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


def toO3DAABBMesh(
    aabb_min: np.ndarray,
    aabb_max: np.ndarray,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> o3d.geometry.TriangleMesh:
    vertices = np.array(
        [
            [aabb_min[0], aabb_min[1], aabb_min[2]],  # 0
            [aabb_max[0], aabb_min[1], aabb_min[2]],  # 1
            [aabb_max[0], aabb_max[1], aabb_min[2]],  # 2
            [aabb_min[0], aabb_max[1], aabb_min[2]],  # 3
            [aabb_min[0], aabb_min[1], aabb_max[2]],  # 4
            [aabb_max[0], aabb_min[1], aabb_max[2]],  # 5
            [aabb_max[0], aabb_max[1], aabb_max[2]],  # 6
            [aabb_min[0], aabb_max[1], aabb_max[2]],  # 7
        ]
    )

    triangles = np.array(
        [
            # 底面 z=min
            [0, 2, 1],
            [0, 3, 2],
            # 顶面 z=max
            [4, 5, 6],
            [4, 6, 7],
            # 前面 y=min
            [0, 1, 5],
            [0, 5, 4],
            # 后面 y=max
            [2, 3, 7],
            [2, 7, 6],
            # 左面 x=min
            [0, 4, 7],
            [0, 7, 3],
            # 右面 x=max
            [1, 2, 6],
            [1, 6, 5],
        ],
        dtype=np.int32,
    )

    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    mesh.paint_uniform_color(color)
    mesh.compute_vertex_normals()
    return mesh


def toLeafO3DAABBMesh(
    node: Node,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> o3d.geometry.TriangleMesh:
    leaf_aabb_mesh = o3d.geometry.TriangleMesh()

    if node.isLeaf():
        aabb = node.toAABB(1.0)
        curr_leaf_aabb_mesh = toO3DAABBMesh(aabb[:3], aabb[3:], color)
        leaf_aabb_mesh += curr_leaf_aabb_mesh
        return leaf_aabb_mesh

    for child_node in node.child_dict.values():
        leaf_aabb_mesh += toLeafO3DAABBMesh(child_node, color)

    return leaf_aabb_mesh
