from octree_shape.Data.node import Node


def demo():
    root = Node()

    root.child_state = 195  # 0b11000011

    print("child_state:", root.child_state)

    child_idxs = root.toChildIdxs()

    print("child_idxs:", child_idxs)
    return True
