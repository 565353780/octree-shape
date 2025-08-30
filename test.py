import torch

from octree_shape.Method.sat import aabb_tri_intersect


aabb = torch.tensor([[0,0,0,1,1,1],
                     [-1,-1,-1,0,0,0]], dtype=torch.float32)
tri  = torch.tensor([[[0.5,0.5,0.5],
                      [1.5,0.5,0.5],
                      [0.5,1.5,0.5]],
                     [[-2,-2,-2],
                      [-2,-2,-2],
                      [-2,-2,-2]]], dtype=torch.float32)

print(aabb_tri_intersect(aabb, tri))   # tensor([True, False])
