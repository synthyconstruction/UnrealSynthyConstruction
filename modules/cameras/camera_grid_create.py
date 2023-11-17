import unreal
import os

def cameraGridCreate(min_x, max_x, min_y, max_y, min_z, max_z, spacing):

    num_points_x = int(round((max_x - min_x) / spacing))
    num_points_y = int(round((max_y - min_y) / spacing))
    # camera_height = max_z + 150
    camera_height = min_z + 150

    # Initialize an empty list for the coordinates
    coordinates = []

    # Generate the grid coordinates
    for i in range(num_points_x):
        x = min_x + (i * spacing)

        for j in range(num_points_y):
            y = min_y + (j * spacing)

            coordinates.append((x, y, camera_height))

    return coordinates
