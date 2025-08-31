import os
from octree_shape.Module.octree_builder import OctreeBuilder


def demo():
    home = os.environ["HOME"]

    mesh_file_path = home + "/chLi/Dataset/Famous/bunny-v2.ply"
    # mesh_file_path = home + "/chLi/Dataset/vae-eval/mesh/002.obj"
    depth_max = 9

    octree_builder = OctreeBuilder(mesh_file_path, depth_max)

    leaf_num = octree_builder.svo.root.leafNum()
    shape_value = octree_builder.svo.root.getShapeValue()

    print("shape leaf num:", leaf_num)
    print("shape value size:", len(shape_value))

    octree_builder.render()
    return True
