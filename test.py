import torch
import numpy as np

import octree_cpp
from octree_cpp import BVH, Vec3f, AABB

# 准备数据：使用 NumPy 数组并确保数据类型为 float32
boxcenter = np.array([0.0, 0.0, 0.0], dtype=np.float32)
boxhalfsize = np.array([1.0, 1.0, 1.0], dtype=np.float32)
triverts = np.array(
    [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32
)

# 调用函数
result = octree_cpp.triBoxOverlap(boxcenter, boxhalfsize, triverts)
print(f"Overlap result: {result}")  # 1 表示相交，0 表示不相交

# 构造 AABB
boxcenter = np.array([0.0, 0.0, 0.0], dtype=np.float32)
boxhalfsize = np.array([1.0, 1.0, 1.0], dtype=np.float32)

# 构造 N 个三角形 (N, 9)
N = 10000
triangles = np.random.uniform(-5, 5, size=(N, 9)).astype(np.float32)

# 放一个相交三角形在第一个位置
triangles[0] = np.array(
    [
        -0.5,
        -0.5,
        0.0,
        0.5,
        -0.5,
        0.0,
        0.0,
        0.5,
        0.0,
    ],
    dtype=np.float32,
)

# 调用接口
result = octree_cpp.isMeshBoxOverlap(boxcenter, boxhalfsize, triangles)

print("是否有三角形与AABB相交？", bool(result))
