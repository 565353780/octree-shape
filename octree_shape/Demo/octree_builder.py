from octree_shape.Module.octree_builder import OctreeBuilder


def demo():
    mesh_file_path = "/Users/chli/chLi/Dataset/Famous/bunny-v2.ply"
    depth_max = 3

    octree_builder = OctreeBuilder(mesh_file_path, depth_max)

    octree_builder.render()
    return True
