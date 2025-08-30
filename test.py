import torch
import octree_cpp
import numpy as np

# 准备数据：使用 NumPy 数组并确保数据类型为 float32
boxcenter = np.array([0.0, 0.0, 0.0], dtype=np.float32)
boxhalfsize = np.array([1.0, 1.0, 1.0], dtype=np.float32)
triverts = np.array([[-1.0, -1.0, 0.0],
                     [1.0, -1.0, 0.0],
                     [0.0, 1.0, 0.0]], dtype=np.float32)

# 调用函数
result = octree_cpp.triBoxOverlap(boxcenter, boxhalfsize, triverts)
print(f"Overlap result: {result}") # 1 表示相交，0 表示不相交
