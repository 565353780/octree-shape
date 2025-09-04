import torch
import numpy as np
from typing import Tuple
from collections import deque

from octree_shape.Method.intersect import toMeshBoxOverlap


class Node:
    def __init__(
        self,
        id: str = "",
        child_state: np.uint8 = np.uint8(0),
    ):
        self.id = id
        self.child_state = np.uint8(child_state)

        self.child_dict = {}

        self.overlap_triangles = torch.empty(0)
        return

    def setId(self, id: str) -> bool:
        self.id = id
        return True

    def setChildState(self, child_state: np.uint8) -> bool:
        self.child_state = np.uint8(child_state)
        return True

    def setChildDict(self, child_dict: dict) -> bool:
        self.child_dict = child_dict

        bools = [i in self.child_dict for i in range(8)]

        byte = np.packbits(bools)[0]
        # byte = np.packbits(bools[::-1])[0]

        self.child_state = np.uint8(byte)
        return True

    def set(self, id: str, child_state: np.uint8) -> bool:
        if not self.setId(id):
            print("[ERROR][Node::set]")
            print("\t setId failed!")
            return False

        if not self.setChildState(child_state):
            print("[ERROR][Node::set]")
            print("\t setChildState failed!")
            return False

        return True

    def updateChildState(self, child_idx: int, is_child_exist: bool) -> bool:
        if child_idx < 0 or child_idx > 7:
            print("[ERROR][Node::addChild]")
            print("\t child_idx must be in [0, 7]")
            return False

        if is_child_exist:
            if child_idx in self.child_dict:
                return True

            self.child_state |= 1 << child_idx

            self.child_dict[child_idx] = Node(self.id + str(child_idx))

            return True

        if child_idx not in self.child_dict:
            return True

        self.child_state &= ~(1 << child_idx)

        self.child_dict.pop(child_idx)

        return True

    @property
    def depth(self) -> int:
        return len(self.id)

    @property
    def isLeaf(self) -> bool:
        return not self.child_dict

    @property
    def leafNum(self) -> int:
        if self.isLeaf:
            return 1

        leaf_num = 0
        for child_node in self.child_dict.values():
            leaf_num += child_node.leafNum

        return leaf_num

    def toChildIdxs(self) -> np.ndarray:
        child_idxs = []
        for i in range(8):
            if (self.child_state >> i) & 1:
                child_idxs.append(i)
        return np.asarray(child_idxs)

    def toAABB(self, scale: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        half_length = scale / 2.0
        aabb_min = np.array(
            [-half_length, -half_length, -half_length], dtype=np.float64
        )
        aabb_max = np.array([half_length, half_length, half_length], dtype=np.float64)

        for id_str in self.id:
            current_half_length = (aabb_max - aabb_min) / 2.0

            if id_str in "0246":
                aabb_max[0] -= current_half_length[0]
            else:
                aabb_min[0] += current_half_length[0]

            if id_str in "0145":
                aabb_max[1] -= current_half_length[1]
            else:
                aabb_min[1] += current_half_length[1]

            if id_str in "0123":
                aabb_max[2] -= current_half_length[2]
            else:
                aabb_min[2] += current_half_length[2]
        return aabb_min, aabb_max

    def toAABBTensor(self, scale: float = 1.0) -> torch.Tensor:
        aabb_min, aabb_max = self.toAABB(scale)

        aabb_tensor = torch.from_numpy(np.hstack([aabb_min, aabb_max]))
        return aabb_tensor

    def addChild(self, child_idx: int):
        if not self.updateChildState(child_idx, True):
            print("[ERROR][Node::addChild]")
            print("\t updateChildState failed!")
            return False

        return True

    def removeChild(self, child_idx: int):
        if not self.updateChildState(child_idx, False):
            print("[ERROR][Node::removeChild]")
            print("\t updateChildState failed!")
            return False

        return True

    def updateOverlaps(
        self,
        vertices: torch.Tensor,
        triangles: torch.Tensor,
        device: str = "cpu",
        dtype=torch.float64,
    ) -> bool:
        aabb = self.toAABBTensor().to(device, dtype=dtype)
        self.overlap_triangles = toMeshBoxOverlap(vertices, triangles, aabb)
        return True

    def updateChilds(
        self,
        vertices: torch.Tensor,
        triangles: torch.Tensor,
        device: str = "cpu",
        dtype=torch.float64,
    ) -> bool:
        for child_id in range(8):
            aabb = Node(self.id + str(child_id)).toAABBTensor().to(device, dtype=dtype)

            valid_triangles = triangles[self.overlap_triangles]

            overlap_triangles = toMeshBoxOverlap(vertices, valid_triangles, aabb)

            if len(overlap_triangles) == 0:
                continue

            self.updateChildState(child_id, True)

            mapped_overlap_triangles = self.overlap_triangles[overlap_triangles]

            self.child_dict[child_id].overlap_triangles = mapped_overlap_triangles
        return True

    def getLeafNodes(self) -> list:
        if self.isLeaf:
            return [self]

        leaf_nodes = []
        for child_node in self.child_dict.values():
            leaf_nodes += child_node.getLeafNodes()

        return leaf_nodes

    def getShapeCode(self) -> np.ndarray:
        shape_value = []

        queue = deque([self])
        while queue:
            node = queue.popleft()
            if node.isLeaf:
                continue

            shape_value.append(node.child_state)

            for child_id in range(8):
                if child_id not in node.child_dict.keys():
                    continue

                queue.append(node.child_dict[child_id])

        shape_value = np.array(shape_value, dtype=np.uint8)
        return shape_value
