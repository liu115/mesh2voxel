import numpy as np
import trimesh
from transform import transform_mesh


if __name__ == '__main__':
    mesh = trimesh.load('.\scene0000_00\scene0000_00_vh_clean_2.ply')
    
    voxel = transform_mesh(mesh)
    np.save('voxel.npy', voxel)