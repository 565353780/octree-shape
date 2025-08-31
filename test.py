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


vertices = [Vec3f(0, 0, 0), Vec3f(1, 0, 0), Vec3f(0, 1, 0)]
triangles = [(0, 1, 2)]

bvh = BVH()
bvh.build(vertices, triangles)

query_box = AABB(Vec3f(0.1, 0.1, -1), Vec3f(0.9, 0.9, 1))
hits = bvh.query_aabb(query_box)

print("Candidate triangle indices:", hits)
