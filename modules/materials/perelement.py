import unreal

import matplotlib
import numpy as np
import json
import os


def CreatePerElementRGBMaterial(world, save_dir='/Game/perElementLabel/', override=True):
    '''
    Description: Function that assigns unique color labels for each element instance in a selection
    Args:\n
        save_dir (str): The folder where the rgb material for labels wil be saved\n
    Return:\n
        void() \n
    '''
    if override:
        unreal.EditorAssetLibrary().delete_directory(save_dir)
    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    umf = unreal.MaterialFactoryNew()
    actors = unreal.GameplayStatics.get_all_actors_of_class(
        world, unreal.StaticMeshActor)  # unreal.DatasmithSceneActor)
    color_idx = np.linspace(0, 1, len(actors))
    cmap = matplotlib.cm.get_cmap('hsv')
    label_dict = {}

    for actor, cid in zip(actors, color_idx):
        datasmith_usr_data = unreal.DatasmithContentLibrary.get_datasmith_user_data(actor)
        name = ''.join(list(datasmith_usr_data.metadata['Datasmith_UniqueId']))
        color = cmap(cid)
        # name = actor.get_actor_label()
        assetTools.create_asset(name, save_dir, unreal.Material, umf)
        label_dict[name] = color

    mel = unreal.MaterialEditingLibrary
    for mat, color in label_dict.items():
        target = unreal.EditorAssetLibrary().load_asset(os.path.join(save_dir, mat))

        # rgb base color
        node_constant3d = mel.create_material_expression(
            target, unreal.MaterialExpressionConstant3Vector, node_pos_x=-300, node_pos_y=250)
        (r, g, b, a) = color
        node_constant3d.set_editor_property("Constant", unreal.LinearColor(r, g, b, a))
        mel.connect_material_property(from_expression=node_constant3d, from_output_name="",
                                      property_=unreal.MaterialProperty.MP_BASE_COLOR)
        mel.recompile_material(target)

    for actor in actors:
        datasmith_usr_data = unreal.DatasmithContentLibrary.get_datasmith_user_data(actor)
        name = ''.join(list(datasmith_usr_data.metadata['Datasmith_UniqueId']))
        # name = actor.get_actor_label()
        mat_path = os.path.join(save_dir, name)
        if unreal.EditorAssetLibrary().does_asset_exist(mat_path):
            target_material = unreal.EditorAssetLibrary().load_asset(mat_path)
            if isinstance(actor, unreal.StaticMeshActor):
                mat_component = actor.get_component_by_class(unreal.StaticMeshComponent)
                mat_component.set_material(0, target_material)

    with open('unique_color_map.json', 'w') as fp:
        json.dump(label_dict, fp)
