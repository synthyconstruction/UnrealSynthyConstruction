import unreal
import json


def ParseElementLevel():
    '''
    Description: function to create the mapping of elements contained in each level and output a per level dictionary, indicating all the elements contained in there.\n 
    Args:\n
    Example:\n
    '''
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    meta_data_dict = {}
    levels = []
    for actor in actors:
        datasmith_usr_data = unreal.DatasmithContentLibrary.get_datasmith_user_data(actor)
        # print(actor.get_actor_label())
        if datasmith_usr_data:
            if "Item_Layer" in list(datasmith_usr_data.metadata.keys()):
                levels.append(datasmith_usr_data.metadata["Item_Layer"])
    levels = sorted(list(set(levels)))

    return levels


def GetElementAtSpecificLevel(level_name):
    '''
    Description: \n 
    Args:\n
    Example:\n
    '''
    targets = []
    print(level_name)
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        datasmith_usr_data = unreal.DatasmithContentLibrary.get_datasmith_user_data(actor)
        if datasmith_usr_data:
            if "Item_Layer" in list(datasmith_usr_data.metadata.keys()):
                if level_name.upper() in datasmith_usr_data.metadata["Item_Layer"].upper():
                    targets.append(actor)
    return targets


def ShowGivenElements(targets):
    '''
    Description: \n 
    Args:\n
    Example:\n
    '''
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if unreal.DatasmithContentLibrary.get_datasmith_user_data(actor):
            actor.set_is_temporarily_hidden_in_editor(True)
    for actor in targets:
        actor.set_is_temporarily_hidden_in_editor(False)


def GetActorElevation(targets):
    for actor in targets:
        if isinstance(actor, unreal.StaticMeshActor):
            print(actor.get_actor_label())
            center, bbox = actor.get_actor_bounds(only_colliding_components=False)
            print(center, bbox)
            bottom_z = center.z - bbox.z
            top_z = center.z + bbox.z
            break
    # Get Actor Bounds
    pass


if __name__ == '__main__':
    levels = ParseElementLevel()
    targets = GetElementAtSpecificLevel(levels[10])
    GetActorElevation(targets)
