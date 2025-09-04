import os
from octree_shape.Module.octree_builder import OctreeBuilder


def demo():
    home = os.environ["HOME"]

    mesh_file_path = home + "/chLi/Dataset/Famous/bunny-v2.ply"
    # mesh_file_path = home + "/chLi/Dataset/vae-eval/mesh/002.obj"
    depth_max = 8

    octree_builder = OctreeBuilder(mesh_file_path, depth_max)

    leaf_num = octree_builder.leafNum
    shape_code = octree_builder.getShapeCode()

    print("shape leaf num:", leaf_num)
    print("shape code size:", len(shape_code))

    octree_builder.render()

    octree_builder.loadShapeCode(shape_code)

    leaf_num = octree_builder.leafNum
    shape_code = octree_builder.getShapeCode()

    print("shape leaf num:", leaf_num)
    print("shape code size:", len(shape_code))

    octree_builder.render()
    return True
