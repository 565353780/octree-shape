import os
import torch
import trimesh
import numpy as np
from typing import Union

from octree_cpp import SVO

from octree_shape.Method.mesh import normalizeMesh
from octree_shape.Method.node import getDepthNodes, toNodeAABBs, toNodeCenters
from octree_shape.Method.render import renderNodes, renderNodesPcd


class OctreeBuilder(object):
    def __init__(
        self,
        mesh_file_path: Union[str, None] = None,
        depth_max: int = 10,
    ) -> None:
        self.svo = SVO()

        if mesh_file_path is not None:
            self.loadMeshFile(mesh_file_path, depth_max)
        return

    def reset(self) -> bool:
        self.svo.reset()
        return True

    def loadMeshFile(self, mesh_file_path: str, depth_max: int = 10) -> bool:
        self.reset()

        if not os.path.exists(mesh_file_path):
            print("[ERROR][OctreeBuilder::loadMeshFile]")
            print("\t mesh file not exist!")
            print("\t mesh_file_path:", mesh_file_path)
            return False

        mesh = trimesh.load(mesh_file_path)

        normalized_mesh = normalizeMesh(mesh)

        self.svo.loadMesh(
            normalized_mesh.vertices.tolist(), normalized_mesh.faces.tolist(), depth_max
        )
        return True

    def loadShapeCode(self, shape_code: list) -> bool:
        self.reset()

        self.svo.loadShapeCode(shape_code)
        return True

    @property
    def leafNum(self) -> int:
        return self.svo.root.leafNum()

    def getLeafNodes(self) -> list:
        return self.svo.root.getLeafNodes()

    def getLeafCenters(self) -> np.ndarray:
        leaf_nodes = self.getLeafNodes()
        return toNodeCenters(leaf_nodes)

    def getLeafAABBs(self) -> np.ndarray:
        leaf_nodes = self.getLeafNodes()
        return toNodeAABBs(leaf_nodes)

    def getDepthNodes(self, depth: int) -> list:
        return getDepthNodes(self.svo.root, depth)

    def getDepthCenters(self, depth: int) -> np.ndarray:
        depth_nodes = self.getDepthNodes(depth)
        return toNodeCenters(depth_nodes)

    def getDepthAABBs(self, depth: int) -> np.ndarray:
        depth_nodes = self.getDepthNodes(depth)
        return toNodeAABBs(depth_nodes)

    def getShapeCode(self) -> list:
        return self.svo.root.getShapeCode()

    def renderLeaf(self, is_pcd: bool = False) -> bool:
        leaf_nodes = self.getLeafNodes()
        if is_pcd:
            return renderNodesPcd(leaf_nodes)
        else:
            return renderNodes(leaf_nodes)

    def renderDepth(self, depth: int, is_pcd: bool = False) -> bool:
        depth_nodes = self.getDepthNodes(depth)
        if is_pcd:
            return renderNodesPcd(depth_nodes)
        else:
            return renderNodes(depth_nodes)
