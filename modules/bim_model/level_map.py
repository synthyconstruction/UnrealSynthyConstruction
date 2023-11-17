import unreal


def ParseElementLevel(ue_version):
    '''
    Description: function to create the mapping of elements contained in each level and output a per level dictionary, indicating all the elements contained in there.\n 
    Args:\n
    Example:\n
    '''
    if ue_version > 4.27:
        actors = unreal.EditorActorSubsystem().get_all_level_actors()
    if ue_version < 5.0:
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
    meta_data_dict = {}
    levels = []
    for actor in actors:
        datasmith_usr_data = unreal.DatasmithContentLibrary.get_datasmith_user_data(actor)
        if datasmith_usr_data:
            if "Item_Layer" in list(datasmith_usr_data.metadata.keys()):
                levels.append(datasmith_usr_data.metadata["Item_Layer"])
    levels = sorted(list(set(levels)))

    return levels

#
