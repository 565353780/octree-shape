import os
import torch
import trimesh
import numpy as np
import open3d as o3d
from typing import Union

from octree_cpp import SVO

from octree_shape.Method.mesh import focusMesh
from octree_shape.Method.node import getDepthNodes, toNodeAABBs, toNodeCenters
from octree_shape.Method.occ import toCentersOcc, toOccCenters
from octree_shape.Method.render import (
    renderNodes,
    renderNodesPcd,
    renderPoints,
    toO3DBoxCentersMesh,
)


class OctreeBuilder(object):
    def __init__(
        self,
        mesh_file_path: Union[str, None] = None,
        depth_max: int = 8,
        focus_center: Union[np.ndarray, list] = [0, 0, 0],
        focus_length: float = 1.0,
        normalize_scale: float = 0.99,
    ) -> None:
        self.depth_max = depth_max
        self.focus_center = focus_center
        self.focus_length = focus_length
        self.normalize_scale = normalize_scale

        self.svo = SVO()

        if mesh_file_path is not None:
            self.loadMeshFile(
                mesh_file_path,
                depth_max,
                focus_center,
                focus_length,
                normalize_scale,
            )
        return

    def reset(self) -> bool:
        self.svo.reset()
        return True

    def loadMeshFile(
        self,
        mesh_file_path: str,
        depth_max: int = 8,
        focus_center: Union[np.ndarray, list] = [0, 0, 0],
        focus_length: float = 1.0,
        normalize_scale: float = 0.99,
    ) -> bool:
        self.reset()

        if not os.path.exists(mesh_file_path):
            print("[ERROR][OctreeBuilder::loadMeshFile]")
            print("\t mesh file not exist!")
            print("\t mesh_file_path:", mesh_file_path)
            return False

        mesh = trimesh.load(mesh_file_path)

        focus_mesh = focusMesh(mesh, focus_center, focus_length, normalize_scale)

        self.svo.loadMesh(
            focus_mesh.vertices.tolist(), focus_mesh.faces.tolist(), depth_max
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

    def getDepthOcc(self, depth: int) -> np.ndarray:
        depth_centers = self.getDepthCenters(depth)
        depth_resolution = 2**depth
        return toCentersOcc(depth_centers, depth_resolution)

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

    def renderDepthOcc(self, depth: int, is_pcd: bool = False) -> bool:
        depth_occ = self.getDepthOcc(depth)
        depth_centers = toOccCenters(depth_occ)
        depth_length = 0.5**depth
        if is_pcd:
            return renderPoints(depth_centers)
        else:
            depth_occ_box_mesh = toO3DBoxCentersMesh(depth_centers, depth_length)
            o3d.visualization.draw_geometries([depth_occ_box_mesh])
            return True
