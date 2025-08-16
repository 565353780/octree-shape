import numpy as np


class Node:
    def __init__(
        self,
        id: str = "0",
        child_state: np.uint8 = np.uint8(0),
    ):
        self.id = id
        self.child_state = np.uint8(child_state)

        self.child_dict = {}
        return

    def setChildState(self, child_state: np.uint8) -> bool:
        self.child_state = np.uint8(child_state)
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

    def toChildIdxs(self) -> np.ndarray:
        child_idxs = []
        for i in range(8):
            if (self.child_state >> i) & 1:
                child_idxs.append(i)
        return np.asarray(child_idxs)

    def toAABB(self) -> np.ndarray:
        return

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
