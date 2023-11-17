import unreal
import os


def ImportTextures(texture_folder_path, save_dir):
    """
    Description:\n
    Args:\n
        texture_folder_path (str): The folder of texture images to be imported into Unreal\n
        save_dir (str): The folder where the material wil be saved\n
    Example:\n
    """
    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
    texture_path = texture_folder_path
    asset_importer_list = []
    for file in os.listdir(texture_path):
        asset_importer = unreal.AssetImportTask()
        asset_importer.filename = os.path.join(texture_path, file)
        asset_importer.destination_path = save_dir
        asset_importer.replace_existing = True
        asset_importer.factory = unreal.TextureFactory()
        asset_importer_list.append(asset_importer)
    assetTools.import_asset_tasks(asset_importer_list)
