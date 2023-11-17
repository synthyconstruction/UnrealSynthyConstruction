import unreal
import os
import json

# NOTE: Adapted from https://github.com/AlexQuevillon/UnrealPythonLibrary/blob/master/UnrealProject/UnrealPythonLibrary/Plugins/UnrealPythonLibraryPlugin/Content/Python/PythonLibraries/AssetFunctions.py

with open(r'C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\configs\props_config.json') as f:
    props_config = json.load(f)

def importAsset(fbx_path, fbx_dest, pname):
    static_mesh_task = buildImportTask(
        fbx_path, fbx_dest, buildStaticMeshImportOptions(pname)
    )
    executeImportTasks([static_mesh_task])


def buildImportTask(filename="", destination_path="", options=None):
    task = unreal.AssetImportTask()
    task.set_editor_property("automated", True)
    task.set_editor_property("destination_name", "")
    task.set_editor_property("destination_path", destination_path)
    task.set_editor_property("filename", filename)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    task.set_editor_property("options", options)

    return task


def executeImportTasks(tasks):
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    imported_asset_paths = []

    for task in tasks:
        for path in task.get_editor_property("imported_object_paths"):
            imported_asset_paths.append(path)

    return imported_asset_paths


def buildStaticMeshImportOptions(pname):
    options = unreal.FbxImportUI()
    scale = props_config['PROP_SCALE'][pname]

    # unreal.FbxImportUI
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_as_skeletal", False)  # Static Mesh

    # unreal.FbxMeshImportData
    options.static_mesh_import_data.set_editor_property("import_translation", unreal.Vector(0.0, 0.0, 0.0))
    options.static_mesh_import_data.set_editor_property("import_rotation", unreal.Rotator(0.0, 0.0, 0.0))
    options.static_mesh_import_data.set_editor_property("import_uniform_scale", scale)

    # unreal.FbxStaticMeshImportData
    options.static_mesh_import_data.set_editor_property("combine_meshes", True)
    options.static_mesh_import_data.set_editor_property("generate_lightmap_u_vs", True)
    options.static_mesh_import_data.set_editor_property("auto_generate_collision", True)

    return options