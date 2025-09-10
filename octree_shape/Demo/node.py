from octree_shape.Data.node import Node
from octree_shape.Method.render import renderNodesMesh


def demo():
    node = Node("07", 195)  # 0b11000011

    print("child_state:", node.child_state)

    child_idxs = node.toChildIdxs()

    print("child_idxs:", child_idxs)

    aabb_min, aabb_max = node.toAABB()

    print("aabb:")
    print(aabb_min)
    print(aabb_max)

    renderNodesMesh([node])
    return True
