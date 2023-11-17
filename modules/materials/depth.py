import unreal
import os


def createDepthMaterial(name, save_dir, depth_limit=5000):
    '''
    Description:\n
    Args:\n
        name (str): The asset name of the material\n
        save_dir (str): The folder where the material wil be saved\n
    Return:\n
        material (unreal Object): The created material instance\n
    Example:\n
    '''

    if unreal.EditorAssetLibrary().does_asset_exist('/Game/MATERIALS/'+name):
        return

    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    umf = unreal.MaterialFactoryNew()
    assetTools.create_asset(name, save_dir, unreal.Material, umf)

    target = unreal.EditorAssetLibrary().load_asset(os.path.join(save_dir, name))
    mel = unreal.MaterialEditingLibrary
    target.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)

    # LERP Node conections
    lerp_node = mel.create_material_expression(
        target, unreal.MaterialExpressionLinearInterpolate, node_pos_x=-300, node_pos_y=200)
    mel.connect_material_property(from_expression=lerp_node, from_output_name="",
                                  property_=unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    # Depth color thresholds
    depth_min = mel.create_material_expression(
        target, unreal.MaterialExpressionConstant3Vector, node_pos_x=-500, node_pos_y=0)
    depth_max = mel.create_material_expression(
        target, unreal.MaterialExpressionConstant3Vector, node_pos_x=-500, node_pos_y=200)
    depth_min.set_editor_property("constant", unreal.LinearColor(r=0.0, g=0.0, b=0.0))
    depth_max.set_editor_property("constant", unreal.LinearColor(r=1.0, g=1.0, b=1.0))
    mel.connect_material_expressions(from_expression=depth_min, from_output_name="",
                                     to_expression=lerp_node, to_input_name="A")
    mel.connect_material_expressions(from_expression=depth_max, from_output_name="",
                                     to_expression=lerp_node, to_input_name="B")

    # Clamp node
    clamp_node = mel.create_material_expression(
        target, unreal.MaterialExpressionClamp, node_pos_x=-800, node_pos_y=300)
    mel.connect_material_expressions(from_expression=clamp_node, from_output_name="",
                                     to_expression=lerp_node, to_input_name="Alpha")

    # Divide Node
    divide_node = mel.create_material_expression(
        target, unreal.MaterialExpressionDivide, node_pos_x=-1000, node_pos_y=300)
    mel.connect_material_expressions(from_expression=divide_node, from_output_name="",
                                     to_expression=clamp_node, to_input_name="")

    # Pixel Depth data
    pix_data = mel.create_material_expression(
        target, unreal.MaterialExpressionPixelDepth, node_pos_x=-1200, node_pos_y=250)
    mel.connect_material_expressions(from_expression=pix_data,  from_output_name="",
                                     to_expression=divide_node, to_input_name="A")

    # depth limit
    node_depth = mel.create_material_expression(
        target, unreal.MaterialExpressionConstant, node_pos_x=-1200, node_pos_y=350)
    node_depth.set_editor_property("R", depth_limit)
    mel.connect_material_expressions(from_expression=node_depth,  from_output_name="",
                                     to_expression=divide_node, to_input_name="B")

    return target


# NOTE: # Class based approach: DO NOT DELETE, AS IT MIGHT BE USEFUL LATER
# class applyDepthMaterial(object):
#     def __init__(self, material_name='CustomDepth'):
#         unreal.EditorLevelLibrary.editor_set_game_view(True)
#         self.actors = (actor for actor in unreal.EditorLevelLibrary.get_selected_level_actors())
#         self.on_pre_tick = unreal.register_slate_pre_tick_callback(self.__pretick__)
#         self.depth_material = unreal.EditorAssetLibrary().load_asset('/Game/MATERIALS/'+material_name)

#     def __pretick__(self, deltatime):
#         try:
#             actor = next(self.actors)
#             mat_component = actor.get_component_by_class(unreal.StaticMeshComponent)
#             max_index = 10
#             for idx in range(max_index):
#                 try:
#                     mat_component.set_material(idx, self.depth_material)
#                 except:
#                     break

#         except Exception as error:
#             print(error)
#             unreal.unregister_slate_pre_tick_callback(self.on_pre_tick)


def applyDepthMaterial(world, mat_root='/Game/MATERIALS/', depth_name="customDepth"):
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

    datasmith_parent_actors = unreal.GameplayStatics.get_all_actors_of_class(
        world, unreal.DatasmithSceneActor)

    for ds_actor in datasmith_parent_actors:
        mat_path = mat_root+depth_name

        if unreal.EditorAssetLibrary().does_asset_exist(mat_path):
            target_material = unreal.EditorAssetLibrary().load_asset(mat_path)
            _inloop_apply_all_childs(ds_actor, target_material)
        else:
            unreal.log_warning(f'No existing material for {ds_actor.get_actor_label()}')
