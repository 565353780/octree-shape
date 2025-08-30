import os
from octree_shape.Module.octree_builder import OctreeBuilder


def demo():
    home = os.environ["HOME"]

    mesh_file_path = home + "/chLi/Dataset/Famous/bunny-v2.ply"
    depth_max = 8
    device = "cuda"

    octree_builder = OctreeBuilder(mesh_file_path, depth_max, device)

    shape_value = octree_builder.node.getShapeValue()

    print(shape_value)
    print(shape_value.shape)

    octree_builder.render()
    return True
