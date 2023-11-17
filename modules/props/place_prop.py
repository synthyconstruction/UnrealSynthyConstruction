import unreal
import random
import json

with open(r'C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\configs\props_config.json') as f:
    props_config = json.load(f)

def propPoses(min_x, max_x, min_y, max_y, min_z, max_z, spacing):

    num_points_x = int(round((max_x - min_x) / spacing))
    num_points_y = int(round((max_y - min_y) / spacing))
    prop_height = min_z + 15

    # Initialize an empty list for the coordinates
    coordinates = []

    # Generate the grid coordinates
    for i in range(num_points_x):
        x = min_x + (i * spacing) + 300 # the + 300 is to create an offset from camera coordinates

        for j in range(num_points_y):
            y = min_y + (j * spacing) + 300 # the + 300 is to create an offset from camera coordinates

            coordinates.append((x, y, prop_height))

    return coordinates


def placeProp(prop_recipe, xloc, yloc, zloc):

    # from the final created list, select a single one of these objects (at random)
    selected_prop = random.sample(props_config['PROP_RECIPE'][prop_recipe], k=1)[0]
    
    prop_height_correction = props_config["HEIGHT_CORRECTION"][selected_prop]
    prop_rot_correction = props_config["ROT_CORRECTION"][selected_prop]

    ASSET_REGISTRY = unreal.AssetRegistryHelpers.get_asset_registry()

    # Use the coordinate to place the object
    ue_dest_folder = "/Game/PROPS/" + selected_prop + "/"
    prop_location = unreal.Vector(float(xloc), float(yloc), float(zloc + prop_height_correction))
    prop_rotation = unreal.Rotator(float(0 + prop_rot_correction[0]), float(0 + prop_rot_correction[0]), float(random.randrange(360) + prop_rot_correction[0]))

    prop_actor_data = ASSET_REGISTRY.get_asset_by_object_path(ue_dest_folder + selected_prop[:-4] + "." + selected_prop[:-4]).get_asset()

    prop_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(prop_actor_data, prop_location, prop_rotation)
    
    return selected_prop, prop_actor