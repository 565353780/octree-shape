import trimesh
import numpy as np


def isAABBIntersect(
    aabb1_min: np.ndarray,
    aabb1_max: np.ndarray,
    aabb2_min: np.ndarray,
    aabb2_max: np.ndarray,
) -> bool:
    return np.all(aabb1_max >= aabb2_min) and np.all(aabb2_max >= aabb1_min)


def isTriangleIntersectAABB(
    tri: np.ndarray,
    aabb_min: np.ndarray,
    aabb_max: np.ndarray,
) -> bool:
    # AABB中心与半边长
    box_center = (aabb_min + aabb_max) / 2
    box_half_size = (aabb_max - aabb_min) / 2

    # 将三角形顶点移到AABB局部坐标系
    v0 = tri[0] - box_center
    v1 = tri[1] - box_center
    v2 = tri[2] - box_center

    verts = np.array([v0, v1, v2])
    edges = [v1 - v0, v2 - v1, v0 - v2]

    # AABB的三个坐标轴
    aabb_axes = np.eye(3)

    # 测试AABB的3个面法向
    for i in range(3):
        min_proj = np.min(verts @ aabb_axes[i])
        max_proj = np.max(verts @ aabb_axes[i])
        if min_proj > box_half_size[i] or max_proj < -box_half_size[i]:
            return False

    # 三角形的法向量
    tri_normal = np.cross(edges[0], edges[1])
    if not tri_normal.any():  # degenerate triangle
        return False
    tri_normal = tri_normal / np.linalg.norm(tri_normal)
    # 将三角形投影到其法线方向
    r = box_half_size.dot(np.abs(tri_normal))
    p = np.dot(v0, tri_normal)
    if abs(p) > r:
        return False

    # 交叉轴测试：9条轴（边对 aabb轴）
    for i in range(3):  # triangle edges
        for j in range(3):  # AABB axes
            axis = np.cross(edges[i], aabb_axes[j])
            if np.linalg.norm(axis) < 1e-6:
                continue  # 平行或零向量
            axis = axis / np.linalg.norm(axis)
            # 投影
            tri_proj = verts @ axis
            tri_min = tri_proj.min()
            tri_max = tri_proj.max()
            # AABB 投影
            r = box_half_size.dot(np.abs(axis))
            if tri_min > r or tri_max < -r:
                return False

    return True


def isTriangleIntersectAABBFast(
    triangle: np.ndarray,
    aabb_min: np.ndarray,
    aabb_max: np.ndarray,
) -> bool:
    tri_min = triangle.min(axis=0)
    tri_max = triangle.max(axis=0)

    if not isAABBIntersect(tri_min, tri_max, aabb_min, aabb_max):
        return False

    inside = np.all((triangle >= aabb_min) & (triangle <= aabb_max), axis=1)
    if np.any(inside):
        return True

    # 精确三角形-AABB 相交检测（使用 trimesh）
    return isTriangleIntersectAABB(triangle, aabb_min, aabb_max)


def isMeshIntersectAABB(
    vertices: np.ndarray,
    triangle_idxs: np.ndarray,
    aabb_min: np.ndarray,
    aabb_max: np.ndarray,
) -> bool:
    for triangle_idx in triangle_idxs:
        triangle = vertices[triangle_idx]

        if isTriangleIntersectAABBFast(triangle, aabb_min, aabb_max):
            return True

    return False
