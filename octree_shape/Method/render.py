import numpy as np
import open3d as o3d
from tqdm import tqdm

from octree_shape.Method.node import toNodeAABBs, toNodeCenters


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


def toO3DBoxCentersMesh(
    box_centers: np.ndarray,
    box_length: float,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> o3d.geometry.TriangleMesh:
    aabbs_mesh = o3d.geometry.TriangleMesh()

    half_length = 0.5 * box_length

    print("[INFO][render::toO3DBoxCentersMesh]")
    print("\t start collect box center mesh...")
    for box_center in tqdm(box_centers):
        aabb_min = box_center - half_length
        aabb_max = box_center + half_length

        aabb_mesh = toO3DAABBMesh(aabb_min, aabb_max, color)

        aabbs_mesh += aabb_mesh

    return aabbs_mesh


def toO3DAABBsMesh(
    nodes: list,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> o3d.geometry.TriangleMesh:
    aabb_mesh = o3d.geometry.TriangleMesh()

    aabbs = toNodeAABBs(nodes)

    print("[INFO][render::toO3DAABBsMesh]")
    print("\t start collect node mesh...")
    for aabb in tqdm(aabbs):
        curr_aabb_mesh = toO3DAABBMesh(aabb[:3], aabb[3:], color)
        aabb_mesh += curr_aabb_mesh

    return aabb_mesh


def renderNodes(
    nodes: list,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> bool:
    aabbs_mesh = toO3DAABBsMesh(nodes, color)
    o3d.visualization.draw_geometries([aabbs_mesh])
    return True


def renderPoints(
    points: np.ndarray,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
):
    colors = np.broadcast_to(color, (points.shape[0], 3))

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    o3d.visualization.draw_geometries([pcd])
    return True


def renderNodesPcd(
    nodes: list,
    color: np.ndarray = np.array([0.0, 0.0, 1.0]),
) -> bool:
    centers = toNodeCenters(nodes)

    return renderPoints(centers, color)
