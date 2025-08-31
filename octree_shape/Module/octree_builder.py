import os
import torch
import trimesh
from typing import Union
from collections import deque

from octree_cpp import BVH, Vec3f, AABB

from octree_shape.Data.node import Node
from octree_shape.Method.mesh import normalizeMesh
from octree_shape.Method.intersect import isMeshIntersectAABB
from octree_shape.Method.render import renderOctree


class OctreeBuilder(object):
    def __init__(
        self,
        mesh_file_path: Union[str, None] = None,
        depth_max: int = 10,
        device: str = "cpu",
        dtype=torch.float64,
    ) -> None:
        self.device = device
        self.dtype = dtype

        self.node = Node()

        if mesh_file_path is not None:
            self.loadMeshFile(mesh_file_path, depth_max)
        return

    def reset(self) -> bool:
        self.node = Node()
        return True

    def loadMeshFile(self, mesh_file_path: str, depth_max: int = 10) -> bool:
        if not os.path.exists(mesh_file_path):
            print("[ERROR][OctreeBuilder::loadMeshFile]")
            print("\t mesh file not exist!")
            print("\t mesh_file_path:", mesh_file_path)
            return False

        mesh = trimesh.load(mesh_file_path)

        normalized_mesh = normalizeMesh(mesh)
        vertices = torch.from_numpy(normalized_mesh.vertices).to(
            self.device, dtype=self.dtype
        )
        triangles = torch.from_numpy(normalized_mesh.faces).to(
            self.device, dtype=torch.int64
        )

        vec_list = [Vec3f(v[0], v[1], v[2]) for v in normalized_mesh.vertices]

        bvh = BVH()
        bvh.build(vec_list, normalized_mesh.faces)

        queue = deque([self.node])
        while queue:
            node = queue.popleft()
            print("start solve node:", node.id, "with depth:", node.depth)

            for child_id in "01234567":
                aabb_min, aabb_max = Node(node.id + child_id).toAABB()

                query_box = AABB(Vec3f(*aabb_min), Vec3f(*aabb_max))

                hits = bvh.query_aabb(query_box)

                if len(hits) == 0:
                    continue

                aabb = (
                    Node(node.id + child_id)
                    .toAABBTensor()
                    .to(self.device, dtype=self.dtype)
                )

                hit_triangles = triangles[hits]

                if isMeshIntersectAABB(vertices, hit_triangles, aabb):
                    node.updateChildState(int(child_id), True)

                    if node.depth < depth_max - 1:
                        queue.append(node.child_dict[int(child_id)])

        return True

    def render(self) -> bool:
        renderOctree(self.node)
        return True
