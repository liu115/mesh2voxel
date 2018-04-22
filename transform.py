import numpy as np
import trimesh

VOXEL_SIZE = 48 # mm

def voxel_center(xyz):
    assert(len(xyz) == 3)
    x, y, z = [i * VOXEL_SIZE + VOXEL_SIZE / 2.0 for i in xyz]

    return (x, y, z)

def point2voxelID(xyz):
    assert(len(xyz) == 3)
    x, y, z = [int(i / VOXEL_SIZE) for i in xyz]

    return (x, y, z)

def point_in_voxel(xyz, voxel_xyz):
    voxel_c = voxel_center(voxel_xyz)
    voxel_bounday = [[axis - VOXEL_SIZE / 2, axis + VOXEL_SIZE / 2] for axis in voxel_c]

    flag = True
    for axis, boundary in enumerate(voxel_bounday):
        if xyz[axis] < boundary[0] or xyz[axis] > boundary[1]:
            flag = False

    return flag

def calc_intersect(voxel_xyz, face):
    assert(len(voxel_xyz) == 3)
    assert face.shape == (3, 3)
    
    voxel_c = voxel_center(voxel_xyz)
    voxel_bounday = [[axis - VOXEL_SIZE / 2, axis + VOXEL_SIZE / 2] for axis in voxel_c]

    for i, v1 in enumerate(face):
        v2 = face[(i+1) % len(face)]
        
        v1_to_v2 = v2 - v1
        for axis, boundary in enumerate(voxel_bounday):

            # Calculate the intersection between the line of v1_to_v2 and each boundary
            if v1_to_v2[axis] == 0.0:
                continue

            for boundary_side in boundary:
                t = (boundary_side - v1[axis]) / v1_to_v2[axis]
                intersect = v1 + t * v1_to_v2
                axis1 = (axis + 1) % 3
                axis2 = (axis + 2) % 3

                if t >= 0 and t <= 1 \
                    and intersect[axis1] >= voxel_bounday[axis1][0] \
                    and intersect[axis1] <= voxel_bounday[axis1][1] \
                    and intersect[axis2] >= voxel_bounday[axis2][0] \
                    and intersect[axis2] <= voxel_bounday[axis2][1]:
                    
                    return True
                
    # Special case: the triangle lies inside voxel
    if point_in_voxel(face[0], voxel_xyz) and point_in_voxel(face[1], voxel_xyz) and point_in_voxel(face[2], voxel_xyz):
        return True
    return False

def transform_mesh(mesh):
    max_cord = np.amax(mesh.vertices, axis=0)
    min_cord = np.amin(mesh.vertices, axis=0)

    min_x, min_y, min_z = min_cord
    max_x, max_y, max_z = max_cord
    print("Size of mesh (m):", (max_x, max_y, max_z))
    print("Transformed size (per voxel):", point2voxelID(max_cord * 1e3))

    # check if the cordinate start from positive
    assert round(min_x) == 0 and round(min_y) == 0 and round(min_z) == 0

    voxel_space_size = point2voxelID(max_cord * 1e3) + (4,)
    print(voxel_space_size)
    voxel_space = np.zeros(voxel_space_size)

    faces = mesh.faces
    print("Number of faces:", len(faces))
    
    sum_size = np.zeros((3,))
    for face_idx, face in enumerate(faces):
        face_vertices = mesh.vertices[face]

        mesh_max = np.amax(face_vertices, axis=0)
        mesh_min = np.amin(face_vertices, axis=0)
        
        max_voxel = point2voxelID(mesh_max * 10e3)
        min_voxel = point2voxelID(mesh_min * 10e3)
        sum_size += np.array(max_voxel) - np.array(min_voxel)
        
        for ix in range(min_voxel[0], max_voxel[0] + 1):
            for iy in range(min_voxel[1], max_voxel[1] + 1):
                for iz in range(min_voxel[2], max_voxel[2] + 1):
                    
                    # Calculate if the block has intersection with the face
                    if calc_intersect((ix, iy, iz), face_vertices):
                        color = np.copy(mesh.visual.face_colors[face_idx])
                        voxel_space[ix, iy, iz] = np.concatenate([[1], color[:3]])

    print("Mean covered voxel size: ", sum_size / len(faces))

    return voxel_space
    
