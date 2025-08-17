import os
import trimesh
from typing import Union
from collections import deque

from octree_shape.Data.node import Node
from octree_shape.Method.mesh import normalizeMesh
from octree_shape.Method.intersect import isMeshIntersectAABB
from octree_shape.Method.render import renderOctree


class OctreeBuilder(object):
    def __init__(
        self,
        mesh_file_path: Union[str, None] = None,
        depth_max: int = 10,
    ) -> None:
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
        vertices = normalized_mesh.vertices
        triangle_idxs = normalized_mesh.faces

        queue = deque([self.node])
        while queue:
            node = queue.popleft()
            print("start solve node:", node.id, "with depth:", node.depth)

            for child_id in "01234567":
                aabb_min, aabb_max = Node(node.id + child_id).toAABB()

                if isMeshIntersectAABB(vertices, triangle_idxs, aabb_min, aabb_max):
                    node.updateChildState(int(child_id), True)

                    if node.depth < depth_max - 1:
                        queue.append(node.child_dict[int(child_id)])

        return True

    def render(self) -> bool:
        renderOctree(self.node)
        return True
