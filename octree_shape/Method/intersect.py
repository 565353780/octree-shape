import torch

import octree_cpp


@torch.no_grad()
def isMeshIntersectAABB(
    vertices: torch.Tensor,  # (V, 3)
    triangles: torch.Tensor,  # (T, 3)  int64
    aabb: torch.Tensor,  # (6,)    [xmin,ymin,zmin,xmax,ymax,zmax]
) -> bool:
    """
    box_center = (aabb[:3] + aabb[3:]) / 2.0
    box_half_size = (aabb[3:] - aabb[:3]) / 2.0

    box_center = box_center.cpu().numpy()
    box_half_size = box_half_size.cpu().numpy()
    reorder_triangles = vertices[triangles].reshape(-1, 9).cpu().numpy()

    result = octree_cpp.any_intersection(box_center, box_half_size, reorder_triangles)
    return result
    """

    device = vertices.device
    dtype = vertices.dtype

    # ---------- 1. 把 AABB 变成 center + half_size ----------
    box_min = aabb[:3]
    box_max = aabb[3:]
    box_center = (box_min + box_max) * 0.5
    box_half = (box_max - box_min) * 0.5

    # ---------- 2. 取出所有三角形顶点 ----------
    tri = vertices[triangles]  # (T, 3, 3)

    # ---------- 3. 快速 AABB 剔除 ----------
    tri_min = tri.min(dim=1)[0]  # (T, 3)
    tri_max = tri.max(dim=1)[0]

    overlap_mask = (tri_min <= box_max) & (tri_max >= box_min)  # (T, 3) -> (T,)
    overlap_mask = overlap_mask.all(dim=1)
    if not overlap_mask.any():
        return False

    tri = tri[overlap_mask]  # 只保留候选

    # ---------- 4. 搬到局部坐标 ----------
    tri = tri - box_center  # (K, 3, 3)

    # ---------- 5. 13 轴 SAT ----------
    v0, v1, v2 = tri.unbind(dim=1)  # 3×(K, 3)
    e0, e1, e2 = v1 - v0, v2 - v1, v0 - v2

    # 构造 13 条轴 (K, 13, 3)
    axes = torch.empty(tri.shape[0], 13, 3, device=device, dtype=dtype)
    axes[:, 0] = torch.tensor([1.0, 0.0, 0.0], device=device)
    axes[:, 1] = torch.tensor([0.0, 1.0, 0.0], device=device)
    axes[:, 2] = torch.tensor([0.0, 0.0, 1.0], device=device)
    n = torch.cross(e0, e1, dim=1)
    axes[:, 3] = n
    # 9 个叉积
    axes[:, 4] = torch.cross(e0, axes[:, 0])
    axes[:, 5] = torch.cross(e0, axes[:, 1])
    axes[:, 6] = torch.cross(e0, axes[:, 2])
    axes[:, 7] = torch.cross(e1, axes[:, 0])
    axes[:, 8] = torch.cross(e1, axes[:, 1])
    axes[:, 9] = torch.cross(e1, axes[:, 2])
    axes[:, 10] = torch.cross(e2, axes[:, 0])
    axes[:, 11] = torch.cross(e2, axes[:, 1])
    axes[:, 12] = torch.cross(e2, axes[:, 2])

    axes = torch.nan_to_num(axes, nan=0.0)
    norm = torch.norm(axes, dim=2, keepdim=True).clamp(min=1e-8)
    axes = axes / norm

    # 投影半径
    box_rad = torch.sum(box_half.abs() * axes.abs(), dim=2)  # (K, 13)

    # 三角形投影
    pts = torch.stack([v0, v1, v2], dim=1)  # (K, 3, 3)
    proj = torch.einsum("kni,kai->kna", pts, axes)  # (K, 3, 13)
    tri_min = proj.min(dim=1)[0]  # (K, 13)
    tri_max = proj.max(dim=1)[0]

    # 重叠检查
    overlap = (tri_max >= -box_rad) & (tri_min <= box_rad)  # (K, 13)
    return bool(overlap.all(dim=1).any())
