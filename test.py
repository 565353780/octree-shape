import torch
import numpy as np

import octree_cpp

# 准备数据：使用 NumPy 数组并确保数据类型为 float32
boxcenter = np.array([0.0, 0.0, 0.0], dtype=np.float32)
boxhalfsize = np.array([1.0, 1.0, 1.0], dtype=np.float32)
triverts = np.array([[-1.0, -1.0, 0.0],
                     [1.0, -1.0, 0.0],
                     [0.0, 1.0, 0.0]], dtype=np.float32)

# 调用函数
result = octree_cpp.triBoxOverlap(boxcenter, boxhalfsize, triverts)
print(f"Overlap result: {result}") # 1 表示相交，0 表示不相交

# 准备测试数据
box_center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
box_half_size = np.array([1.0, 1.0, 1.0], dtype=np.float32)

# 创建三角形数据 (N, 9) 形状的数组
# 每个三角形由9个浮点数表示: [v0x, v0y, v0z, v1x, v1y, v1z, v2x, v2y, v2z]
triangles = np.array([
    # 第一个三角形
    [-1.0, -1.0, 0.0, 1.0, -1.0, 0.0, 0.0, 1.0, 0.0],
    # 第二个三角形
    [2.0, 2.0, 2.0, 3.0, 2.0, 2.0, 2.5, 3.0, 2.0],
    # 更多三角形...
], dtype=np.float32)

# 调用函数
result = octree_cpp.any_intersection(box_center, box_half_size, triangles)
print(f"Intersection found: {result}")
