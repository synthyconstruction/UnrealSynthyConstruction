import unreal
import json
import os

with open(r'C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\configs\material_config.json') as f:
    mat_config = json.load(f)

def CreateMaterial(name, save_dir, texture, material_type="Concrete", uv=(1, 1)):
    """
    Description:\n
    Args:\n
        name (str): The asset name of the material\n
        save_dir (str): The folder where the material wil be saved\n
    Return:\n
        material (unreal Object): The created material instance\n
    Example:\n
    """

    if unreal.EditorAssetLibrary().does_asset_exist("/Game/MATERIALS/" + name):
        return

    metallic, specular, roughness = mat_config['MATERIAL_VALUE_DICT'][material_type]
    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    umf = unreal.MaterialFactoryNew()
    assetTools.create_asset(name, save_dir, unreal.Material, umf)
    target = unreal.EditorAssetLibrary().load_asset(os.path.join(save_dir, name))
    mel = unreal.MaterialEditingLibrary

    # texture
    node_tex = mel.create_material_expression(target, unreal.MaterialExpressionTextureSampleParameter2D, node_pos_x=-400, node_pos_y=0)
    texture_asset = unreal.load_asset(texture)
    node_tex.set_editor_property("texture", texture_asset)
    mel.connect_material_property(from_expression=node_tex, from_output_name="", property_=unreal.MaterialProperty.MP_BASE_COLOR)

    # texure uv coord
    node_texCoord = mel.create_material_expression(
        target,
        unreal.MaterialExpressionTextureCoordinate,
        node_pos_x=-600,
        node_pos_y=0,
    )
    node_texCoord.set_editor_property("UTiling", uv[0])
    node_texCoord.set_editor_property("VTiling", uv[1])
    mel.connect_material_expressions(
        from_expression=node_texCoord,
        from_output_name="",
        to_expression=node_tex,
        to_input_name="UVs",
    )

    # metalic
    metallic_string = texture + "_metallic"
    if unreal.EditorAssetLibrary().does_asset_exist(metallic_string):
        node_metallic = mel.create_material_expression(
            target,
            unreal.MaterialExpressionTextureSampleParameter2D,
            node_pos_x=-300,
            node_pos_y=250,
        )
        metallic_asset = unreal.load_asset(metallic_string)
        node_metallic.set_editor_property("texture", metallic_asset)
        mel.connect_material_property(
            from_expression=node_metallic,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_METALLIC,
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_metallic,
            to_input_name="UVs",
        )
    else:
        node_metallic = mel.create_material_expression(
            target, unreal.MaterialExpressionConstant, node_pos_x=-300, node_pos_y=250
        )
        node_metallic.set_editor_property("R", metallic)
        mel.connect_material_property(
            from_expression=node_metallic,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_METALLIC,
        )

    # specular
    specular_string = texture + "_specular"
    if unreal.EditorAssetLibrary().does_asset_exist(specular_string):
        node_specular = mel.create_material_expression(
            target,
            unreal.MaterialExpressionTextureSampleParameter2D,
            node_pos_x=-300,
            node_pos_y=350,
        )
        specular_asset = unreal.load_asset(specular_string)
        node_specular.set_editor_property("texture", specular_asset)
        mel.connect_material_property(
            from_expression=node_specular,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_SPECULAR,
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_specular,
            to_input_name="UVs",
        )
    else:
        node_specular = mel.create_material_expression(
            target, unreal.MaterialExpressionConstant, node_pos_x=-300, node_pos_y=350
        )
        node_specular.set_editor_property("R", specular)
        mel.connect_material_property(
            from_expression=node_specular,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_SPECULAR,
        )

    # roughness
    roughness_string = texture + "_roughness"
    if unreal.EditorAssetLibrary().does_asset_exist(roughness_string):
        node_roughness = mel.create_material_expression(
            target,
            unreal.MaterialExpressionTextureSampleParameter2D,
            node_pos_x=-300,
            node_pos_y=450,
        )
        roughness_asset = unreal.load_asset(roughness_string)
        node_roughness.set_editor_property("texture", roughness_asset)
        mel.connect_material_property(
            from_expression=node_roughness,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_ROUGHNESS,
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_roughness,
            to_input_name="UVs",
        )
    else:
        node_roughness = mel.create_material_expression(
            target, unreal.MaterialExpressionConstant, node_pos_x=-300, node_pos_y=450
        )
        node_roughness.set_editor_property("R", roughness)
        mel.connect_material_property(
            from_expression=node_roughness,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_ROUGHNESS,
        )

    # --------- NORMAL
    normal_string = texture + "_normal"
    if unreal.EditorAssetLibrary().does_asset_exist(normal_string):
        node_normal = mel.create_material_expression(target, unreal.MaterialExpressionTextureSampleParameter2D, node_pos_x=-300, node_pos_y=450)
        normal_asset = unreal.load_asset(normal_string)
        node_normal.set_editor_property("texture", normal_asset)
        mel.connect_material_property(
            from_expression=node_normal,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_NORMAL
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_normal,
            to_input_name="UVs")
        

    # --------- Ambient Occlusion
    ao_string = texture + "_ao"
    if unreal.EditorAssetLibrary().does_asset_exist(ao_string):
        node_ao = mel.create_material_expression(
            target, 
            unreal.MaterialExpressionTextureSampleParameter2D, 
            node_pos_x=-300, 
            node_pos_y=450
        )
        ao_asset = unreal.load_asset(ao_string)
        node_ao.set_editor_property("texture", ao_asset)
        mel.connect_material_property(
            from_expression=node_ao,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_AMBIENT_OCCLUSION
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_ao,
            to_input_name="UVs")

    mel.recompile_material(target)

    return target


def CreateMaterialComplete(name, save_dir, uv=(1, 1)):
    """
    Description: a material instance creating function that loads actual texture files for normals, metallic, etc.
    Args:\n
        name (str): The asset name of the material\n
        save_dir (str): The folder where the material wil be saved\n
    Return:\n
        material (unreal Object): The created material instance\n
    Example:\n
    """

    name = name[:-4]  # eliminating the "_fbx" at the end of the name
    if unreal.EditorAssetLibrary().does_asset_exist(save_dir + name + "_mat"):
        return

    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    umf = unreal.MaterialFactoryNew()
    assetTools.create_asset(name + "_mat", save_dir, unreal.Material, umf)
    target = unreal.EditorAssetLibrary().load_asset(
        os.path.join(save_dir, name + "_mat")
    )
    mel = unreal.MaterialEditingLibrary

    # --------- TEXTURE UV COORD
    node_texCoord = mel.create_material_expression(
        target,
        unreal.MaterialExpressionTextureCoordinate,
        node_pos_x=-600,
        node_pos_y=0,
    )
    node_texCoord.set_editor_property("UTiling", uv[0])
    node_texCoord.set_editor_property("VTiling", uv[1])

    # --------- TEXTURE
    texture_string = save_dir + "textures/" + name + "_texture"
    if unreal.EditorAssetLibrary().does_asset_exist(texture_string):
        node_tex = mel.create_material_expression(
            target,
            unreal.MaterialExpressionTextureSampleParameter2D,
            node_pos_x=-400,
            node_pos_y=0,
        )

        texture_asset = unreal.load_asset(texture_string)
        node_tex.set_editor_property("texture", texture_asset)
        mel.connect_material_property(
            from_expression=node_tex,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_BASE_COLOR,
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_tex,
            to_input_name="UVs",
        )

    # --------- METALLICITY
    metallic_string = save_dir + "textures/" + name + "_metallic"
    if unreal.EditorAssetLibrary().does_asset_exist(metallic_string):
        node_metallic = mel.create_material_expression(
            target,
            unreal.MaterialExpressionTextureSampleParameter2D,
            node_pos_x=-300,
            node_pos_y=250,
        )
        metallic_asset = unreal.load_asset(metallic_string)
        node_metallic.set_editor_property("texture", metallic_asset)
        mel.connect_material_property(
            from_expression=node_metallic,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_METALLIC,
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_metallic,
            to_input_name="UVs",
        )

    # --------- SPECULAR
    specular_string = save_dir + "textures/" + name + "_specular"
    if unreal.EditorAssetLibrary().does_asset_exist(specular_string):
        node_specular = mel.create_material_expression(
            target,
            unreal.MaterialExpressionTextureSampleParameter2D,
            node_pos_x=-300,
            node_pos_y=350,
        )
        specular_asset = unreal.load_asset(specular_string)
        node_specular.set_editor_property("texture", specular_asset)
        mel.connect_material_property(
            from_expression=node_specular,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_SPECULAR,
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_specular,
            to_input_name="UVs",
        )

    # --------- ROUGHNESS
    roughness_string = save_dir + "textures/" + name + "_roughness"
    if unreal.EditorAssetLibrary().does_asset_exist(roughness_string):
        node_roughness = mel.create_material_expression(
            target,
            unreal.MaterialExpressionTextureSampleParameter2D,
            node_pos_x=-300,
            node_pos_y=450,
        )
        roughness_asset = unreal.load_asset(roughness_string)
        node_roughness.set_editor_property("texture", roughness_asset)
        mel.connect_material_property(
            from_expression=node_roughness,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_ROUGHNESS,
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_roughness,
            to_input_name="UVs",
        )

    # --------- NORMAL
    normal_string = save_dir + "textures/" + name + "_normal"
    if unreal.EditorAssetLibrary().does_asset_exist(normal_string):
        node_normal = mel.create_material_expression(
            target, 
            unreal.MaterialExpressionTextureSampleParameter2D, 
            node_pos_x=-300, 
            node_pos_y=450
        )
        normal_asset = unreal.load_asset(normal_string)
        node_normal.set_editor_property("texture", normal_asset)
        mel.connect_material_property(
            from_expression=node_normal,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_NORMAL
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_normal,
            to_input_name="UVs")
        
    # --------- Ambient Occlusion
    ao_string = save_dir + "textures/" + name + "_ao"
    if unreal.EditorAssetLibrary().does_asset_exist(ao_string):
        node_ao = mel.create_material_expression(
            target, 
            unreal.MaterialExpressionTextureSampleParameter2D, 
            node_pos_x=-300, 
            node_pos_y=450
        )
        ao_asset = unreal.load_asset(ao_string)
        node_ao.set_editor_property("texture", ao_asset)
        mel.connect_material_property(
            from_expression=node_ao,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_AMBIENT_OCCLUSION
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_ao,
            to_input_name="UVs")
        
    # --------- Emissive Color
    ec_string = save_dir + "textures/" + name + "_ec"
    if unreal.EditorAssetLibrary().does_asset_exist(ec_string):
        node_ec = mel.create_material_expression(
            target, 
            unreal.MaterialExpressionTextureSampleParameter2D, 
            node_pos_x=-300, 
            node_pos_y=450
        )
        ec_asset = unreal.load_asset(ec_string)
        node_ec.set_editor_property("texture", ec_asset)
        mel.connect_material_property(
            from_expression=node_ec,
            from_output_name="",
            property_=unreal.MaterialProperty.MP_EMISSIVE_COLOR 
        )
        mel.connect_material_expressions(
            from_expression=node_texCoord,
            from_output_name="",
            to_expression=node_ec,
            to_input_name="UVs")

    mel.recompile_material(target)

    return target


def ApplyMaterial(world, mat_root="/Game/MATERIALS/"):
    """
    Description: The function will search the material the same name as DatasmithSceneActor in the `mat_root` folder\n
    Args:\n
        save_dir (str): The folder where the rgb material for labels wil be saved\n
    Return:\n
        void() \n
    Example:\n
    """

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

    datasmith_parent_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.DatasmithSceneActor)

    for ds_actor in datasmith_parent_actors:
        mat_path = os.path.join(mat_root, ds_actor.get_actor_label())

        if unreal.EditorAssetLibrary().does_asset_exist(mat_path):
            target_material = unreal.EditorAssetLibrary().load_asset(mat_path)
            _inloop_apply_all_childs(ds_actor, target_material)
        else:
            unreal.log_warning(f"No existing material for {ds_actor.get_actor_label()}")


def propApplyMaterial(prop_actor, prop_mat_root, prop_name):
    """
    Description: A function that adds an already created material instance to a prop actor object.
    Args:\n
        prop_actor (object): Prop instance created in Unreal loader\n
        mat_path (str): Path to the material instance to apply\n
    Return:\n
        void() \n
    """

    prop_name = prop_name[:-4]  # eliminating the "_fbx" at the end of the name
    if unreal.EditorAssetLibrary().does_asset_exist(prop_mat_root + prop_name + "_mat"):
        target_material = unreal.EditorAssetLibrary().load_asset(prop_mat_root + prop_name + "_mat")
        if isinstance(prop_actor, unreal.StaticMeshActor) or isinstance(prop_actor, unreal.SkeletalMeshActor):
            hidden_state = prop_actor.is_hidden_ed()

            if isinstance(prop_actor, unreal.StaticMeshActor):
                mat_component = prop_actor.get_component_by_class(unreal.StaticMeshComponent)
            elif isinstance(prop_actor, unreal.SkeletalMeshActor):
                mat_component = prop_actor.get_component_by_class(unreal.SkeletalMeshComponent)
                
            max_index = 10
            for idx in range(max_index):
                try:
                    mat_component.set_material(idx, target_material)
                except:
                    break
            prop_actor.set_is_temporarily_hidden_in_editor(hidden_state)

    else:
        unreal.log_warning(f"No existing material for {prop_mat_root + prop_name}")

