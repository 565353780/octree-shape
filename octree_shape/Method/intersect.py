import torch
import numpy as np
from tqdm import trange

import octree_cpp

from octree_shape.Method.sat import aabb_tri_intersect


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

    # aabb: (B,6)  [min,max]   tri: (B,3,3)
    tri_min = tri.min(dim=1)[0]          # (B,3)
    tri_max = tri.max(dim=1)[0]          # (B,3)

# 快速不相交判定：三角形包围盒与 AABB 无重叠
    aabb_min = aabb[:, :3]
    aabb_max = aabb[:, 3:]
    mask = (tri_min <= aabb_max).all(-1) & (tri_max >= aabb_min).all(-1)

# 只在 mask=True 的样本上跑 SAT
    sat_result = torch.zeros(B, dtype=torch.bool, device=aabb.device)
    if mask.any():
        sat_result[mask] = aabb_tri_intersect(aabb[mask], tri[mask])

    aabb = np.hstack([aabb_min, aabb_max])
    triangle_tensor = torch.from_numpy(triangle).unsqueeze(0).to(torch.float32)
    aabb_tensor = torch.from_numpy(aabb).unsqueeze(0).to(torch.float32)

    for _ in trange(1000):
        aabb_tri_intersect(aabb_tensor, triangle_tensor)

    return bool(aabb_tri_intersect(aabb_tensor, triangle_tensor)[0].item())


def isMeshIntersectAABB(
    vertices: np.ndarray,
    triangles: np.ndarray,
    aabb_min: np.ndarray,
    aabb_max: np.ndarray,
) -> bool:
    vertices_tensor = torch.from_numpy(vertices).to(torch.float32)
    triangles_tensor = torch.from_numpy(triangles).to(torch.int64)
    aabb_tensor = torch.from_numpy(np.hstack([aabb_min, aabb_max])).to(torch.float32)

    return is_mesh_aabb_any_intersect(vertices_tensor, triangles_tensor, aabb_tensor)

@torch.no_grad()
def is_mesh_aabb_any_intersect(
        vertices: torch.Tensor,          # (V, 3)
        triangles: torch.Tensor,         # (T, 3)  int64
        aabb: torch.Tensor               # (6,)    [xmin,ymin,zmin,xmax,ymax,zmax]
    ) -> bool:
    """
    只要网格中任意一个三角形与给定 AABB 相交就返回 True。
    支持 GPU；全部在 PyTorch 内完成。
    """
    device = vertices.device
    dtype  = vertices.dtype

    # ---------- 1. 把 AABB 变成 center + half_size ----------
    box_min = aabb[:3]
    box_max = aabb[3:]
    box_center = (box_min + box_max) * 0.5
    box_half   = (box_max - box_min) * 0.5

    # ---------- 2. 取出所有三角形顶点 ----------
    tri = vertices[triangles]          # (T, 3, 3)

    # ---------- 3. 快速 AABB 剔除 ----------
    tri_min = tri.min(dim=1)[0]        # (T, 3)
    tri_max = tri.max(dim=1)[0]

    overlap_mask = (tri_min <= box_max) & (tri_max >= box_min)  # (T, 3) -> (T,)
    overlap_mask = overlap_mask.all(dim=1)
    if not overlap_mask.any():
        return False
    tri = tri[overlap_mask]            # 只保留候选

    # ---------- 4. 搬到局部坐标 ----------
    tri = tri - box_center             # (K, 3, 3)

    # ---------- 5. 13 轴 SAT ----------
    v0, v1, v2 = tri.unbind(dim=1)     # 3×(K, 3)
    e0, e1, e2 = v1 - v0, v2 - v1, v0 - v2

    # 构造 13 条轴 (K, 13, 3)
    axes = torch.empty(tri.shape[0], 13, 3, device=device, dtype=dtype)
    axes[:, 0] = torch.tensor([1.,0.,0.], device=device)
    axes[:, 1] = torch.tensor([0.,1.,0.], device=device)
    axes[:, 2] = torch.tensor([0.,0.,1.], device=device)
    n = torch.cross(e0, e1, dim=1)
    axes[:, 3] = n
    # 9 个叉积
    axes[:, 4]  = torch.cross(e0, axes[:, 0])
    axes[:, 5]  = torch.cross(e0, axes[:, 1])
    axes[:, 6]  = torch.cross(e0, axes[:, 2])
    axes[:, 7]  = torch.cross(e1, axes[:, 0])
    axes[:, 8]  = torch.cross(e1, axes[:, 1])
    axes[:, 9]  = torch.cross(e1, axes[:, 2])
    axes[:, 10] = torch.cross(e2, axes[:, 0])
    axes[:, 11] = torch.cross(e2, axes[:, 1])
    axes[:, 12] = torch.cross(e2, axes[:, 2])

    axes = torch.nan_to_num(axes, nan=0.0)
    norm = torch.norm(axes, dim=2, keepdim=True).clamp(min=1e-8)
    axes = axes / norm

    # 投影半径
    box_rad = torch.sum(box_half.abs() * axes.abs(), dim=2)   # (K, 13)

    # 三角形投影
    pts = torch.stack([v0, v1, v2], dim=1)                   # (K, 3, 3)
    proj = torch.einsum("kni,kai->kna", pts, axes)             # (K, 3, 13)
    tri_min = proj.min(dim=1)[0]                             # (K, 13)
    tri_max = proj.max(dim=1)[0]

    # 重叠检查
    overlap = (tri_max >= -box_rad) & (tri_min <= box_rad)   # (K, 13)
    return bool(overlap.all(dim=1).any())
