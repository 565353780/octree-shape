import numpy as np

from octree_shape.Data.node import Node


def getDepthNodes(node: Node, depth: int) -> list:
    if node.depth() == depth:
        return [node]

    depth_nodes = []

    for child_node in node.child_dict.values():
        depth_nodes += getDepthNodes(child_node, depth)

    return depth_nodes


def toNodeCenters(nodes: list) -> np.ndarray:
    center_list = []

    for node in nodes:
        center = node.toCenter()
        center_list.append(center)

    centers = np.vstack(center_list)
    return centers


def toNodeAABBs(nodes: list) -> np.ndarray:
    aabb_list = []

    for node in nodes:
        aabb = node.toAABB(1.0)
        aabb_list.append(aabb)

    aabbs = np.vstack(aabb_list)
    return aabbs
