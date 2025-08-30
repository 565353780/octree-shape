from octree_shape.Module.octree_builder import OctreeBuilder


def demo():
    mesh_file_path = "/Users/chli/chLi/Dataset/Famous/bunny-v2.ply"
    depth_max = 4

    octree_builder = OctreeBuilder(mesh_file_path, depth_max)

    shape_value = octree_builder.node.getShapeValue()

    print(shape_value)
    print(shape_value.shape)

    octree_builder.render()
    return True
