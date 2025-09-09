import numpy as np


def toCentersOcc(centers: np.ndarray, resolution: int) -> np.ndarray:
    occ = np.zeros([resolution, resolution, resolution], dtype=bool)

    node_idxs = np.floor((centers + 0.5) * resolution).astype(int)

    occ[tuple(node_idxs.T)] = True

    return occ


def toOccCenters(occ: np.ndarray) -> np.ndarray:
    resolution = occ.shape[0]

    indices = np.argwhere(occ)

    centers = (indices + 0.5) / resolution - 0.5

    return centers
