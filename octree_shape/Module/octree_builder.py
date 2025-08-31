import os
import torch
import trimesh
from time import time
from typing import Union
from collections import deque

from octree_cpp import SVO

from octree_shape.Method.mesh import normalizeMesh
from octree_shape.Method.render import renderOctree


class OctreeBuilder(object):
    def __init__(
        self,
        mesh_file_path: Union[str, None] = None,
        depth_max: int = 10,
        device: str = "cpu",
    ) -> None:
        self.device = device

        self.svo = SVO()

        if mesh_file_path is not None:
            self.loadMeshFile(mesh_file_path, depth_max)
        return

    def reset(self) -> bool:
        self.svo.reset()
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
            self.device, dtype=torch.float64
        )
        triangles = torch.from_numpy(normalized_mesh.faces).to(
            self.device, dtype=torch.int64
        )

        self.svo.loadMesh(vertices, triangles, depth_max)
        return True

    def render(self) -> bool:
        renderOctree(self.svo.root)
        return True
