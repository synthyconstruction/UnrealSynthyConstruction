import unreal
from collections import defaultdict
# from ..etc import deprecated


def GetElementAtSpecificLevel(level_name, ue_version):
    '''
    Description: \n 
    Args:\n
    Example:\n
    '''
    targets = []

    if ue_version > 4.27:
        actors = unreal.EditorActorSubsystem().get_all_level_actors()
    if ue_version < 5.0:
        actors = unreal.EditorLevelLibrary.get_all_level_actors()

    for actor in actors:
        datasmith_usr_data = unreal.DatasmithContentLibrary.get_datasmith_user_data(actor)
        if datasmith_usr_data:
            if "Item_Layer" in list(datasmith_usr_data.metadata.keys()):
                if level_name.upper() in datasmith_usr_data.metadata["Item_Layer"].upper() and not actor.is_hidden_ed():
                    targets.append(actor)
    return targets


def propertyParse(obj):
    '''
    Input:
        targets (list): A list of Datasmith actor objects

    Output:
        properties (list): A list of all properties of all passed objects

    '''
    properties = []
    datasmith_usr_data = unreal.DatasmithContentLibrary.get_datasmith_user_data(obj)

    name = list(datasmith_usr_data.metadata['Element_Name'])
    category = list(datasmith_usr_data.metadata['Element_Category'])
    family = list(datasmith_usr_data.metadata['Element_Family'])
    material = list(datasmith_usr_data.metadata['Item_Material'])

    properties.append([name, category, family, material])

    return properties


# @deprecated
def GetActorBoundingBox(actor):

    bounding_box_coords = defaultdict(list)

    center, bbox = actor.get_actor_bounds(only_colliding_components=False)
    print(center, bbox)

    # Min-Max Z Coordinates
    min_z = center.z - bbox.z
    max_z = center.z + bbox.z

    # Min-Max X Coordinates
    min_x = center.x - bbox.x
    max_x = center.x + bbox.x

    # Min-Max Y Coordinates
    min_y = center.y - bbox.y
    max_y = center.y + bbox.y

    bounding_box_coords[str(actor)].append((min_x, max_x,
                                            min_y, max_y,
                                            min_z, max_z))

    return bounding_box_coords  # Get Actor Bounds
