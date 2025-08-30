import torch

def aabb_tri_intersect(aabb: torch.Tensor, tri: torch.Tensor) -> torch.Tensor:
    """
    SAT-based AABB vs triangle intersection
    aabb : (B, 6)  [xmin, ymin, zmin, xmax, ymax, zmax]
    tri  : (B, 3, 3)  [v0, v1, v2]
    return (B,) bool
    """
    B = aabb.shape[0]
    device = aabb.device
    dtype = aabb.dtype

    # ---------- 1. 把 AABB 变成 center + half_size ----------
    box_min = aabb[:, :3]
    box_max = aabb[:, 3:]
    box_center = (box_min + box_max) * 0.5
    box_half = (box_max - box_min) * 0.5          # (B, 3)

    # ---------- 2. 把三角形顶点移到 AABB 局部坐标 ----------
    v0, v1, v2 = tri.unbind(dim=1)                 # each (B, 3)
    v0 = v0 - box_center
    v1 = v1 - box_center
    v2 = v2 - box_center

    # ---------- 3. 三角形边 ----------
    e0 = v1 - v0
    e1 = v2 - v1
    e2 = v0 - v2

    # ---------- 4. 构造 13 条分离轴 ----------
    # 3 AABB 轴 + 3 三角形法线 + 9 叉积
    axes = torch.empty(B, 13, 3, device=device, dtype=dtype)

    # (a) AABB 轴
    axes[:, 0] = torch.tensor([1.0, 0.0, 0.0], device=device)
    axes[:, 1] = torch.tensor([0.0, 1.0, 0.0], device=device)
    axes[:, 2] = torch.tensor([0.0, 0.0, 1.0], device=device)

    # (b) 三角形法线
    n = torch.cross(e0, e1, dim=1)
    axes[:, 3] = n

    # (c) 9 个叉积
    # e0 × {1,0,0}, {0,1,0}, {0,0,1}
    axes[:, 4] = torch.linalg.cross(e0, axes[:, 0])
    axes[:, 5] = torch.linalg.cross(e0, axes[:, 1])
    axes[:, 6] = torch.linalg.cross(e0, axes[:, 2])
    # e1
    axes[:, 7] = torch.linalg.cross(e1, axes[:, 0])
    axes[:, 8] = torch.linalg.cross(e1, axes[:, 1])
    axes[:, 9] = torch.linalg.cross(e1, axes[:, 2])
    # e2
    axes[:, 10] = torch.linalg.cross(e2, axes[:, 0])
    axes[:, 11] = torch.linalg.cross(e2, axes[:, 1])
    axes[:, 12] = torch.linalg.cross(e2, axes[:, 2])

    # ---------- 5. 投影测试 ----------
    # 把 NaN 轴设为 0（退化三角形时）
    axes = torch.nan_to_num(axes, nan=0.0)
    # 归一化避免数值爆炸
    norm = torch.norm(axes, dim=2, keepdim=True).clamp(min=1e-8)
    axes = axes / norm

    # AABB 投影半径
    box_rad = torch.sum(torch.abs(axes) * box_half.unsqueeze(1), dim=2)  # (B, 13)

    # 三角形投影区间
    def proj(pts, axis):
        # pts: (B, 3, 3)  axis: (B, 13, 3)
        # 希望返回 (B, 3, 13)
        return torch.einsum("bni,bai->bna", pts, axis)

    p0 = proj(torch.stack([v0, v1, v2], dim=1), axes)   # (B, 3, 13)
    tri_min = p0.min(dim=1)[0]                          # (B, 13)
    tri_max = p0.max(dim=1)[0]

    # 重叠检查
    overlap = (tri_max >= -box_rad) & (tri_min <= box_rad)  # (B, 13)

    # ---------- 6. 结果 ----------
    # 若 13 条轴全部重叠则相交
    intersect = overlap.all(dim=1)
    return intersect
