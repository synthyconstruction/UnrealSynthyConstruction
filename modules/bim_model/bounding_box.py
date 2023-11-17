import unreal
from collections import defaultdict


def bboxCompute(objects, floor_UID):

    floor_bbox = []

    for object in objects:
        datasmith_usr_data = unreal.DatasmithContentLibrary.get_datasmith_user_data(object)

        if 'Datasmith_UniqueId' in list(datasmith_usr_data.metadata.keys()):
            unique_id = ''.join(list(datasmith_usr_data.metadata['Datasmith_UniqueId']))

            if unique_id in floor_UID:
                print(f'Collecting floor objects in level id {unique_id} to compute camera grids')

                bounding_box_coords = defaultdict(list)
                center, bbox = object.get_actor_bounds(only_colliding_components=False)

                min_z, max_z = (center.z - bbox.z), (center.z + bbox.z)  # Min-Max Z Coordinates
                min_x, max_x = (center.x - bbox.x), (center.x + bbox.x)  # Min-Max X Coordinates
                min_y, max_y = (center.y - bbox.y), (center.y + bbox.y)  # Min-Max Y Coordinates

                bounding_box_coords[str(object)].append([min_x, max_x, min_y, max_y, min_z, max_z])
                floor_bbox.append(bounding_box_coords)  # Bounding Box Values for Floor objects in current level

            else:
                continue

        else:
            continue

    return floor_bbox
