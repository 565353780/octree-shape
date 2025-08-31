import os
import torch
import trimesh
from time import time
from typing import Union
from collections import deque

import octree_cpp

from octree_shape.Data.node import Node
from octree_shape.Method.mesh import normalizeMesh
from octree_shape.Method.intersect import (
    isMeshBoxOverlap,
    isMeshBoxOverlapTorch,
    toMeshBoxOverlap,
)
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

        timestamp = time()
        current_depth = 0

        self.node.updateOverlaps(vertices, triangles, self.device, self.dtype)

        queue = deque([self.node])
        while queue:
            node = queue.popleft()
            if node.depth != current_depth:
                curr_time = time()
                time_spend = curr_time - timestamp
                timestamp = curr_time
                print(
                    "finish solve node depth:",
                    current_depth,
                    ", time spend:",
                    time_spend,
                )
                current_depth = node.depth

            node.updateChilds(vertices, triangles, self.device, self.dtype)

            for child_node in node.child_dict.values():
                if node.depth < depth_max - 1:
                    queue.append(child_node)

        print(
            "finish solve node depth:",
            current_depth,
            ", time spend:",
            time() - timestamp,
        )
        return True

    def render(self) -> bool:
        renderOctree(self.node)
        return True
