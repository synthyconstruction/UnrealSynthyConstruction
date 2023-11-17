import unreal
import matplotlib
import numpy as np
import os
import copy
import colorsys


def CreateLabelRGBMaterial(world, rgb_map, save_dir='/Game/LABELS/', override=True, target_dtype=unreal.DatasmithSceneActor):
    '''
    Description: Use the top parent as the label set\n
    Args:\n
        save_dir (str): The folder where the rgb material for labels wil be saved\n
    Return:\n
        void() \n
    Example:\n
    '''
    if override:
        unreal.EditorAssetLibrary().delete_directory(save_dir)
    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    umf = unreal.MaterialFactoryNew()
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, target_dtype)
    
    color_idx = np.linspace(0, 1, len(actors))
    cmap = matplotlib.cm.get_cmap('hsv')
    
    label_dict = {}

    for actor, cid in zip(actors, color_idx):
        name = actor.get_actor_label()
        color = rgb_map[name]#cmap(cid)
        color = [x / 255 for x in color]
        # color = colorsys.rgb_to_hsv(*color/255)
        
        assetTools.create_asset(name, save_dir, unreal.Material, umf)
        label_dict[name] = color

    mel = unreal.MaterialEditingLibrary
    for mat, color in label_dict.items():
        target = unreal.EditorAssetLibrary().load_asset(os.path.join(save_dir, mat))

        # rgb base color
        node_constant3d = mel.create_material_expression(target, 
                                                         unreal.MaterialExpressionConstant3Vector, 
                                                         node_pos_x=-300, node_pos_y=250)
        (r, g, b) = color
        node_constant3d.set_editor_property("Constant", unreal.LinearColor(r, g, b, 1.0))
        mel.connect_material_property(from_expression=node_constant3d, 
                                      from_output_name="",
                                      property_=unreal.MaterialProperty.MP_BASE_COLOR)
        mel.recompile_material(target)


def ApplyLabels(world, mat_root='/Game/LABELS/', target_dtype=unreal.DatasmithSceneActor):
    '''
    Description: The function will search the material the same name as DatasmithSceneActor in the `mat_root` folder\n
    Args:\n
        save_dir (str): The folder where the rgb material for labels wil be saved\n
    Return:\n
        void() \n
    Example:\n
    '''
    def _inloop_apply_all_childs(root_actor, mat):
        child_actors = root_actor.get_attached_actors()
        for child_actor in child_actors:
            if isinstance(child_actor, unreal.StaticMeshActor):
                hidden_state = child_actor.is_hidden_ed()
                mat_component = child_actor.get_component_by_class(unreal.StaticMeshComponent)

                max_index = 10
                for idx in range(max_index):
                    try:
                        mat_component.set_material(idx, mat)
                    except:
                        break

                child_actor.set_is_temporarily_hidden_in_editor(hidden_state)
            _inloop_apply_all_childs(child_actor, mat)

    parent_actors = unreal.GameplayStatics.get_all_actors_of_class(
        world, target_dtype)
    for ds_actor in parent_actors:
        mat_path = os.path.join(mat_root, ds_actor.get_actor_label())
        if unreal.EditorAssetLibrary().does_asset_exist(mat_path):
            target_material = unreal.EditorAssetLibrary().load_asset(mat_path)
            _inloop_apply_all_childs(ds_actor, target_material)
        else:
            unreal.log_warning(f'No existing material for {ds_actor.get_actor_label()}')
