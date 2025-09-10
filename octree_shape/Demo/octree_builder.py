import os
from octree_shape.Module.octree_builder import OctreeBuilder


def demo():
    home = os.environ["HOME"]

    mesh_file_path = home + "/chLi/Dataset/Famous/bunny-v2.ply"
    # mesh_file_path = home + "/chLi/Dataset/vae-eval/mesh/002.obj"
    depth_max = 8
    focus_center = [0, 0, 0.0]
    focus_length = 1.0
    normalize_scale = 0.99
    output_info = True

    octree_builder = OctreeBuilder(
        mesh_file_path,
        depth_max,
        focus_center,
        focus_length,
        normalize_scale,
        output_info,
    )

    leaf_num = octree_builder.leafNum
    shape_code = octree_builder.getShapeCode()

    print("shape leaf num:", leaf_num)
    print("shape code size:", len(shape_code))

    octree_builder.loadShapeCode(shape_code)

    leaf_num = octree_builder.leafNum
    shape_code = octree_builder.getShapeCode()

    print("shape leaf num:", leaf_num)
    print("shape code size:", len(shape_code))

    octree_builder.renderLeaf()

    for depth in range(1, depth_max + 1):
        octree_builder.renderDepth(depth)

    occ = octree_builder.getDepthOcc(8)
    print("occ shape:", occ.shape)
    octree_builder.renderDepthOcc(8)
    return True
