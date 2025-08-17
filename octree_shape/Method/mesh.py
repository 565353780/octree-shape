import trimesh


def normalizeMesh(mesh: trimesh.Trimesh, length: float = 0.99) -> trimesh.Trimesh:
    vertices = mesh.vertices
    min_bounds = vertices.min(axis=0)
    max_bounds = vertices.max(axis=0)
    center = (min_bounds + max_bounds) / 2.0
    size = (max_bounds - min_bounds).max()

    scale = length / size

    normalized_vertices = (vertices - center) * scale

    normalized_mesh = trimesh.Trimesh(
        vertices=normalized_vertices, faces=mesh.faces, process=False
    )

    return normalized_mesh
