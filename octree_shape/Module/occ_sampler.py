import os
import trimesh
import numpy as np
import open3d as o3d
from tqdm import trange
from typing import Union

from octree_shape.Method.occ import toOccCenters
from octree_shape.Method.render import (
    createRandomColors,
    renderPoints,
    toO3DBoxCentersMesh,
    toPcd,
)
from octree_shape.Module.octree_builder import OctreeBuilder


class OccSampler(object):
    def __init__(
        self,
        mesh_file_path: Union[str, None] = None,
        subdiv_depth: int = 8,
        occ_depth: int = 8,
        output_info: bool = False,
    ) -> None:
        self.subdiv_depth = subdiv_depth
        self.occ_depth = occ_depth

        self.mesh = trimesh.Trimesh()
        self.subdiv_centers = np.array([])

        if mesh_file_path is not None:
            self.loadMeshFile(
                mesh_file_path,
                subdiv_depth,
                occ_depth,
                output_info,
            )
        return

    def reset(self) -> bool:
        self.mesh = trimesh.Trimesh()
        self.subdiv_centers = np.array([])
        return True

    def loadMesh(
        self,
        mesh: trimesh.Trimesh,
        subdiv_depth: int = 8,
        occ_depth: int = 8,
        output_info: bool = False,
    ) -> bool:
        self.subdiv_depth = subdiv_depth
        self.occ_depth = occ_depth

        self.reset()

        self.mesh = mesh

        subdiv_octree_builder = OctreeBuilder()

        subdiv_octree_builder.loadMesh(
            mesh,
            subdiv_depth,
            focus_center=[0, 0, 0],
            focus_length=1,
            normalize_scale=0.99,
            output_info=output_info,
        )

        self.subdiv_centers = subdiv_octree_builder.getDepthCenters(subdiv_depth)
        return True

    def loadMeshFile(
        self,
        mesh_file_path: str,
        subdiv_depth: int = 8,
        occ_depth: int = 8,
        output_info: bool = False,
    ) -> bool:
        if not os.path.exists(mesh_file_path):
            print("[ERROR][OccSampler::loadMeshFile]")
            print("\t mesh file not exist!")
            print("\t mesh_file_path:", mesh_file_path)
            return False

        mesh = trimesh.load(mesh_file_path)

        return self.loadMesh(mesh, subdiv_depth, occ_depth, output_info)

    def queryOrderedOcc(self, idx: int) -> np.ndarray:
        valid_idx = idx % self.subdiv_centers.shape[0]
        center = self.subdiv_centers[valid_idx]

        occ_octree_builder = OctreeBuilder()

        occ_octree_builder.loadMesh(
            self.mesh,
            self.occ_depth,
            focus_center=center,
            focus_length=0.5**self.subdiv_depth,
            normalize_scale=0.99,
            output_info=False,
        )

        depth_occ = occ_octree_builder.getDepthOcc(self.occ_depth)
        return depth_occ

    def queryRandomOcc(self) -> np.ndarray:
        random_idx = np.random.randint(0, self.subdiv_centers.shape[0])
        return self.queryOrderedOcc(random_idx)

    def renderOcc(self, occ: np.ndarray, is_pcd: bool = False) -> bool:
        centers = toOccCenters(occ)
        length = 0.5**self.occ_depth
        if is_pcd:
            return renderPoints(centers)
        else:
            occ_box_mesh = toO3DBoxCentersMesh(centers, length)
            o3d.visualization.draw_geometries([occ_box_mesh])
            return True

    def toMergeOccGeometry(
        self, is_pcd: bool = False
    ) -> Union[o3d.geometry.TriangleMesh, o3d.geometry.PointCloud]:
        length = 0.5**self.occ_depth
        scale_ratio = 0.5**self.subdiv_depth

        occ_num = self.subdiv_centers.shape[0]

        random_colors = createRandomColors(occ_num)

        print("[INFO][OccSampler::toMergeOcc]")
        if is_pcd:
            merge_pcd = o3d.geometry.PointCloud()

            print("\t start collect pcd...")
            for i in trange(occ_num):
                occ = self.queryOrderedOcc(i)
                centers = toOccCenters(occ)
                centers = centers * scale_ratio + self.subdiv_centers[i]
                centers_pcd = toPcd(centers, random_colors[i])

                merge_pcd += centers_pcd
            return merge_pcd
        else:
            merge_mesh = o3d.geometry.TriangleMesh()

            scaled_length = length * scale_ratio

            print("\t start collect mesh...")
            for i in trange(occ_num):
                occ = self.queryOrderedOcc(i)
                centers = toOccCenters(occ)
                centers = centers * scale_ratio + self.subdiv_centers[i]
                centers_mesh = toO3DBoxCentersMesh(
                    centers, scaled_length, random_colors[i]
                )

                merge_mesh += centers_mesh
            return merge_mesh

    def renderMergeOcc(self, is_pcd: bool = False) -> bool:
        occ_geometry = self.toMergeOccGeometry(is_pcd)
        o3d.visualization.draw_geometries([occ_geometry])
        return True
