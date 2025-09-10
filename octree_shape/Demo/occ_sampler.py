import os
from tqdm import trange

from octree_shape.Module.occ_sampler import OccSampler


def demo():
    home = os.environ["HOME"]

    mesh_file_path = home + "/chLi/Dataset/Famous/bunny-v2.ply"
    # mesh_file_path = home + "/chLi/Dataset/vae-eval/mesh/002.obj"
    subdiv_depth = 3
    occ_depth = 7
    output_info = True

    occ_sampler = OccSampler(mesh_file_path, subdiv_depth, occ_depth, output_info)

    print("start test speed of queryOrderedOcc...")
    for i in trange(occ_sampler.subdiv_centers.shape[0]):
        occ = occ_sampler.queryOrderedOcc(i)
    exit()

    print("start renderMergeOcc...")
    occ_sampler.renderMergeOcc()

    for i in range(occ_sampler.subdiv_centers.shape[0]):
        occ = occ_sampler.queryOrderedOcc(i)

        print("occ shape:", occ.shape)
        occ_sampler.renderOcc(occ)
    return True
