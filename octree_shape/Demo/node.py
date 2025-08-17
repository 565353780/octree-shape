from octree_shape.Data.node import Node


def demo():
    root = Node("07", 195)  # 0b11000011

    print("child_state:", root.child_state)

    child_idxs = root.toChildIdxs()

    print("child_idxs:", child_idxs)

    aabb_min, aabb_max = root.toAABB()

    print("aabb:")
    print(aabb_min)
    print(aabb_max)
    return True
