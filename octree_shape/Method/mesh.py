import trimesh
import numpy as np
from typing import Union


def normalizeMesh(
    mesh: trimesh.Trimesh,
    normalize_scale: float = 0.99,
) -> trimesh.Trimesh:
    vertices = mesh.vertices
    min_bounds = vertices.min(axis=0)
    max_bounds = vertices.max(axis=0)
    center = (min_bounds + max_bounds) / 2.0
    size = (max_bounds - min_bounds).max()

    scale = normalize_scale / size

    normalized_vertices = (vertices - center) * scale

    normalized_mesh = trimesh.Trimesh(
        vertices=normalized_vertices, faces=mesh.faces, process=False
    )

    return normalized_mesh


def focusMesh(
    mesh: trimesh.Trimesh,
    focus_center: Union[np.ndarray, list] = [0, 0, 0],
    focus_length: float = 1.0,
    normalize_scale: float = 0.99,
) -> trimesh.Trimesh:
    if isinstance(focus_center, list):
        focus_center = np.array(focus_center)

    normalized_mesh = normalizeMesh(mesh, normalize_scale)

    vertices = normalized_mesh.vertices

    focus_vertices = (vertices - focus_center) / focus_length

    focus_mesh = trimesh.Trimesh(
        vertices=focus_vertices, faces=mesh.faces, process=False
    )
    return focus_mesh
