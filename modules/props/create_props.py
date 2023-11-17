import unreal
import os
import sys

sys.path.append("..")  # Adds higher directory to python modules path.

from modules.materials.materials import CreateMaterialComplete
from modules.props.import_props import importAsset

def createProp(prop_directory):
    """
    The prop_directory must have the following structure:

    /path/to/prop/directory/
        |
        ├── type1_prop_folder
        |   |
        │   ├── propname1_1_fbx
        |   |   ├── propname1_1.fbx
        │   │   ├── textures
        │   │       ├── propname1_1_metallic.png
        │   │       ├── propname1_1_normal.png
        │   │       ├── propname1_1_specular.png
        │   │       ├── propname1_1_texture.png
        │   │       ├── propname1_1_diffusive.png
        |   |
        │   ├── propname1_2_fbx
        │       ├── propname1_2.fbx
        │       ├── textures
        │           ├── propname1_2_metallic.png
        │           ├── propname1_2_normal.png
        │           ├── propname1_2_specular.png
        │           ├── propname1_2_texture.png
        │           ├── propname1_2_diffusive.png
        |
        ├── type2_prop_folder
        |   |
        │   ├── propname2_1_fbx
        |   |   ├── ...
        |   |
        │   ├── propname2_2_fbx
        |   |   ├── ...
        |   |
        │   ├── propname3_1_fbx
        |   |   ├── ...
        |   |
        │   ├── propname3_2_fbx
        |   |   ├── ...

    Input args:
    - world: Unreal Engine created world. This instance will change depending on the UE version being used.
    - prop_directory (str): path to where FBX props are located.

    """

    prop_types = os.listdir(prop_directory)
    print("These are all the available prop categories")
    print(prop_types)

    for ptype in prop_types:
        all_prop_names = os.listdir(prop_directory + ptype)
        prop_names = [name for name in all_prop_names if name.endswith("fbx")]
        print(f"These are all the props within the {ptype} category")
        print(prop_names)

        for pname in prop_names:
            prop_path = prop_directory + ptype + "/" + pname
            ue_dest_folder = "/Game/PROPS/" + pname + "/"
            
            print(f"Loading the {pname} asset")
            importAsset(prop_path, "/Game/PROPS/", pname)  # Import current object geometry (FBX)
            CreateMaterialComplete(pname, ue_dest_folder)  # Create object material instance




