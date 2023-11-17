import unreal

import os
import pdb
import json
import time
import random
import argparse
import matplotlib
import numpy as np
from collections import defaultdict

# BIM Model functions
from modules.bim_model.property_parse import GetElementAtSpecificLevel  # , propertyParse
from modules.bim_model.level_map import ParseElementLevel
from modules.bim_model.elem_visibility import showGivenElements
from modules.bim_model.query_floor import queryFloor
from modules.bim_model.bounding_box import bboxCompute
from modules.bim_model.set_collision import setCollision

# Material creation functions
from modules.materials.textures import ImportTextures
from modules.materials.materials import CreateMaterial, ApplyMaterial, propApplyMaterial
from modules.materials.labels import CreateLabelRGBMaterial, ApplyLabels
from modules.materials.perelement import CreatePerElementRGBMaterial
from modules.materials.depth import createDepthMaterial, applyDepthMaterial

# Camera creation & manipulation functions
from modules.cameras.camera_grid_create import cameraGridCreate
from modules.cameras.camera_create import cameraCreate, cameraCanonical
# from modules.cameras.take_photo import cameraCapture, canonicalCameraCapture
from modules.cameras.camera_intersect import cameraIntersect, cameraNear, cameraFloating

# Light source creation and simulation functions
from modules.light.light_positions import lightPoses
from modules.light.light_create import lightCreate
from modules.light.intensity_set import intensitySet
from modules.light.light_switch import lightSwitch
from modules.light.light_floating import lightFloating
from modules.light.create_post_process_volume import createPostProcessVol

# Props loading, creation, and placement
from modules.props.create_props import createProp
from modules.props.place_prop import propPoses, placeProp
from modules.props.prop_intersect import propFloating

"""
V2.2 details:

    - [camera] Support for all cubemap direction camera deployment in a single script
    - [camera] Better camera grid estimation now eliminates cameras that are floating in space due to estimation of uneven bounding boxes of non rectangular floor objects. 
    - [camera] Canonical camera functionality now supported. Per class image collection is one at a time
    - [material] Support for automatic material mapping (before it was based on element manual selection) on ALL element layers
    - [material] Support for automatic custom depth material assignemnt on all material levels
    - [bim_model] Support for automated floor object selection for deploying camera grid.
    - [main.py] A more organized code structure.

V2.3 TODO work:
    [X] [light] Automated point light deployment on random camera coordinates (150 above camera level)
    - [camera] Automated canonical camera collection for all classes simultaneously
    [X] [main.py] Argument based code execution
    [X] [bim_model] Random activation of elements per class (randomization)

"""

class cameraCapture(object):
    '''
    Description: Execution function to take photos of selected cameras in the editor
    '''

    def __init__(self, camera_actors, suffix='', resolution=[480, 480]):
        # self.ue_verison = ue_version
        # if ue_version < 5.0:
        #     unreal.EditorLevelLibrary.editor_set_game_view(True)
        #     self.cameras = unreal.GameplayStatics.get_all_actors_of_class(
        #         unreal.EditorLevelLibrary.get_editor_world(), unreal.CameraActor)
        # elif ue_version > 4.27:
        #     unreal.LevelEditorSubsystem().editor_set_game_view(True)
        #     self.cameras = unreal.GameplayStatics.get_all_actors_of_class(
        #         unreal.UnrealEditorSubsystem().get_editor_world(), unreal.CameraActor)
        unreal.LevelEditorSubsystem().editor_set_game_view(True)
        self.cameras = iter(camera_actors)
        # self.cameras = (actor for actor in unreal.EditorLevelLibrary.get_selected_level_actors())
        self.on_pre_tick = unreal.register_slate_pre_tick_callback(self.__pretick__)
        self.resolution = resolution
        self.suffix = suffix

    def __pretick__(self, deltatime):
        try:
            # Extracting camera actor name & positional parameters
            camera = next(self.cameras)
            camera_name = camera.get_actor_label()
            camera_location = camera.get_actor_location()
            camera_rotation = camera.get_actor_rotation()

            # Place viewport at camera's view
            unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera_location, camera_rotation)

            # Rendering settings of the editor
            view_setting = unreal.AutomationViewSettings()
            view_setting.set_editor_property("bloom", False)
            view_setting.set_editor_property("anti_aliasing", True)
            view_setting.set_editor_property("contact_shadows", True)
            view_setting.set_editor_property("distance_field_ao", True)
            view_setting.set_editor_property("eye_adaptation", False)
            view_setting.set_editor_property("motion_blur", False)
            view_setting.set_editor_property("screen_space_ao", True)
            view_setting.set_editor_property("screen_space_reflections", True)
            view_setting.set_editor_property("temporal_aa", False)
            unreal.AutomationLibrary.get_default_screenshot_options_for_rendering().view_settings = view_setting

            export_filename = f"{camera_name}{self.suffix}.png"
            unreal.AutomationLibrary.take_high_res_screenshot(
                *self.resolution, export_filename, mask_enabled=False, capture_hdr=True, delay=0.000000,
                comparison_tolerance=unreal.ComparisonTolerance.HIGH)

            unreal.EditorLevelLibrary.eject_pilot_level_actor()

        except Exception as error:
            print(error)
            unreal.unregister_slate_pre_tick_callback(self.on_pre_tick)

def parse_args():
    parser = argparse.ArgumentParser(description="Official Implementation of the Unreal-ViS-WP Synthetic dataset collector")
    parser.add_argument("--ue_version", type=float, help="specify the unreal version")

    # ----------- Camera Arguments
    parser.add_argument("--create_cameras", action="store_true", help="Create a set of cameras in all directions")
    parser.add_argument("--create_canonical", action="store_true", help="Create a set of canonical cameras around each individual object class")
    parser.add_argument("--take_photos", action="store_true", help="Take photos with selected cameras")
    parser.add_argument("--camera_spacing", type=int, default=250, help="Spacing between each camera in centimeters")
    parser.add_argument("--camera_intersect", type=int, default=100, help="Distance in centimeters that cameras are allowed to be in proximity of other elements. 100 is ideal for upward vectors, 200 for any other regular distance. Might keep it all at 200")
    parser.add_argument("--camera_floating", type=int, default=200, help="Distance in centimeters used to detect whether or not the camera is floating. 200 is ideal to determine if camera is floating in the air, and not on top of the actual slab")

    # ----------- Light arguments
    parser.add_argument("--post_process", action="store_true", help="Create a post process volume")
    parser.add_argument("--create_lights", action="store_true", help="Create a set of lights")
    parser.add_argument("--light_radius", type=int, default=300, help="unique light intensity in Lumens")
    parser.add_argument("--set_light_intensity", action="store_true", help="Set the intensity of already existing light components")
    parser.add_argument("--light_intensity", type=int, default=750, help="unique light intensity in Lumens")
    parser.add_argument("--random_intensities", action="store_true", help="Decision to randomly assign light intensities")
    parser.add_argument("--intensity_set", type=list, default=[750, 300, 150], help="set of light intensities in Lumens")
    parser.add_argument("--light_spacing", type=int, default=500, help="Spacing between each light in centimeters")
    parser.add_argument("--light_floating", type=int, default=800, help="Distance in centimeters used to detect whether or not the light is floating and not on top of a slab area. 800 is ideal")
    parser.add_argument("--light_switch", action="store_true", help="Whether or not to turn on or off light elements")
    parser.add_argument("--light_switch_state", type=str, default="on", help="Decision on turning lights based on: on, off, random")

    # ----------- Material & Texture Arguments
    parser.add_argument("--import_textures", action="store_true", help="Import textures from the defined path")
    parser.add_argument("--texture_path", type=str, default=r"C:\Users\shh\Documents\ShunHsiangHsu\Textures", help="Path to texture folder")
    parser.add_argument("--create_material", action="store_true", help="Whether or not to create material instances with loaded Textures")
    parser.add_argument("--apply_material", action="store_true", help="Whether or not apply materials to each ASTM Uniformat class. WARNING: this requires material instances to be created.")
    parser.add_argument("--create_depth", action="store_true", help="Whether or not apply the custom depth material instance to all elements")
    parser.add_argument("--apply_depth", action="store_true", help="Whether or not apply the custom depth material instance to all elements")

    # ----------- Class Label Arguments
    parser.add_argument("--create_labels", action="store_true", help="Create labels as material instances for each loaded element class")
    parser.add_argument("--apply_labels", action="store_true", help="Apply created labels to all objects. WARNING: this requires labels to be created")
    parser.add_argument("--per_element_map", action="store_true", help="Create and apply per element labels to compute visibility metrics")

    # ------------ BIM Elements Arguments
    parser.add_argument("--bim_visibility", type=str, default="all_on", help="set visibilty of BIM elements by: all_on, all_off, or random")
    parser.add_argument("--vis_prob", type=float, default=0.2, help="Likelihood of a BIM element randomly being set to hidden")

    # ------------ Props for random elements in jobsites
    parser.add_argument("--props_path", type=str, default="<your/path/to/construction/props>", help="Root path to where FBX props are stored")
    parser.add_argument("--create_props", action="store_true", help="Load props assets from the SIEProps library. NOTE: This routine will only load FBX models given a project recipe. In addition, this routine will already load each with their corresponding materials.")
    parser.add_argument("--prop_recipe", type=str, default=None, help="String keyword that determines which types of props can be placed in this project (e.g., do not place cement bags on a stick frame structure)")
    parser.add_argument("--prop_spacing", type=int, default=800, help="Likelihood of a Prop element being randomly placed.")
    parser.add_argument("--placement_prob", type=float, default=0.1, help="Likelihood of a Prop element being randomly placed.")
    parser.add_argument("--prop_floating", type=int, default=100, help="Distance in centimeters used to detect whether or not the prop is floating and not on top of a slab area. 100 is ideal")
    

    # ----------- Other Arguments
    parser.add_argument("--count_elements", action="store_true", help="Return the total count of active elements")
    parser.add_argument("--no_level_structure", action="store_true", help="Use this flag if there is no existing level structure in the loaded model")
    parser.add_argument("--level_structure", action="store_true", help="Use this flag if there is no existing level structure in the loaded model")

    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    with open(r'C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\configs\camera_config.json') as f:
        camera_config = json.load(f)
    with open(r'C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\ue_master\unreal_viswp\configs\class_label_config.json') as f:
        class_label_config = json.load(f)

    assert (args.ue_version), "Please specify the Unreal Engine version you are running the script on"

    # Checking argument combination compatibility:
    if (args.create_cameras and args.take_photos) or (args.create_canonical and args.take_photos):
        raise ValueError("Creating cameras and taking photos cannot be both specified")
    
    if ((args.apply_material and args.apply_depth) or (args.apply_labels and args.apply_depth) or (args.apply_labels and args.apply_material)):
        raise ValueError("Two types of material cannot be simultaneously applied")

    # ------------- Environment Configs
    # CREATE_CANONICAL_CAMERAS = False
    CAPTURE_CANONICAL_ELEMS = False
    # CREATE_PER_ELEMENT_MAP = True
    # COUNT_ELEMS = False


    # Creating post process volume
    if args.post_process:
        createPostProcessVol()

    # ------------------------------------------------------------------------------ #
    # ----------------------| GLOBAL CODE executions: Levels |---------------------- #
    # ------------------------------------------------------------------------------ #
    # NOTE: Floor IDs must be manually collected from the editor. This makes the process easy and organized for now.
    # Also, this allows a controlled execution to know which camera numbers belong to which floors and directions
    level_list = ParseElementLevel(args.ue_version)  # list of levels in model

    if args.ue_version < 5:
        world = unreal.EditorLevelLibrary.get_editor_world()
    if args.ue_version > 4.27:
        world = unreal.UnrealEditorSubsystem().get_editor_world()

    floor_class_names = ["floor-concrete", "floor"]
    floor_UID = queryFloor(floor_class_names, world)

    # --------------------------------------------------------------------------------------- #
    # ----------------------| GLOBAL CODE executions: Texture Loading |---------------------- #
    # --------------------------------------------------------------------------------------- #
    # NOTE: Textures MUST exist in the used directory
    texture_save_dir = "/Game/TEXTURES/"
    if args.import_textures:
        ImportTextures(
            args.texture_path,
            texture_save_dir,
        )

    # --------------------------------------------------------------------------------------------------- #
    # ----------------------| GLOBAL CODE executions: Rendered Material Instances |---------------------- #
    # --------------------------------------------------------------------------------------------------- #
    if args.create_material:
        viswp_present_classes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.DatasmithSceneActor)
        for viswp_class in viswp_present_classes:
            viswp_class = viswp_class.get_actor_label()
            CreateMaterial(viswp_class, "/Game/MATERIALS", "/Game/TEXTURES/" + class_label_config["CLASS_TO_TEXTURE_MAP"][viswp_class],
                            material_type=class_label_config["CLASS_TEXTURE_PROPERTY_MAP"][viswp_class])
    if args.apply_material:
        ApplyMaterial(world)
    if args.create_depth:
        depth_name = "customDepth"
        createDepthMaterial(depth_name, "/Game/MATERIALS")
    if args.apply_depth:
        depth_name = "customDepth"  # This is the name of the depth material created on the Game/ directory in the Content Browser
        applyDepthMaterial(world, "/Game/MATERIALS/", depth_name=depth_name)

    # ------------------------------------------------------------------------------------------------ #
    # ----------------------| GLOBAL CODE executions: Label Material Instances |---------------------- #
    # ------------------------------------------------------------------------------------------------ #
    if args.create_labels:
        CreateLabelRGBMaterial(world=world, rgb_map=class_label_config["CLASS_RGB_MAP"])  # Creating label material instances in game

    if args.apply_labels:
        ApplyLabels(world)  # Applying labels

    if args.per_element_map:
        CreatePerElementRGBMaterial(world)

    # -------------------------------------------------------------------------------- #
    # ----------------------| GLOBAL CODE executions: Loading SIEProps |---------------------- #
    # -------------------------------------------------------------------------------- #
    if args.create_props:
        print("Creating props")
        createProp(args.props_path)

    # ------------------------------------------------------------------ #
    # ----------------------| Starting Main Loop |---------------------- #
    # ------------------------------------------------------------------ #

    objects = []
    if args.ue_version > 4.27:
        actors = unreal.EditorActorSubsystem().get_all_level_actors()
    if args.ue_version < 5.0:
        actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # Set actors to be collisionable. This allows elements to return True when intersecting with other elements:
    setCollision(world)

    if args.no_level_structure:
        # -----------------------| Label Material Instances
        if args.create_labels:
            CreateLabelRGBMaterial(world)  # Creating label material instances in game
        if args.apply_labels:
            ApplyLabels(world)  # Applying labels
        if args.per_element_map:
            CreatePerElementRGBMaterial(world)

        # -----------------------| Turning off or on BIM elements
        showGivenElements(world, state=args.bim_visibility, prob=args.vis_prob)
        for actor in actors:
            if isinstance(actor, unreal.StaticMeshActor):  # and actor.is_hidden_ed():
                objects.append(actor)

        if args.create_lights:
            # ----------------------| Collect bounding boxes for floor elements to determine camera grids
            floor_bbox = bboxCompute(objects, floor_UID)
            print("------------------------------------------------------------------")

            # ----------------------| Creating Light Grids based on floor bbox
            print("Creating light coordinates based on floor grid")
            light_grid = []

            for bbox in floor_bbox:
                for key in list(bbox):
                    min_x, max_x, min_y, max_y, min_z, max_z = bbox[key][0]
                    light_coords = lightPoses(
                        min_x, max_x, min_y, max_y, min_z, max_z, args.light_spacing
                    )
                    light_grid.append(light_coords)
            print("-------------------------------------------------")

            light_no = 0
            for light_coords_set in light_grid:
                for light_coords in light_coords_set:
                    light_no += 1
                    print("Spawning new light:", "PointLight" + str(light_no))

                    created_light = lightCreate(
                        light_coords[0],
                        light_coords[1],
                        light_coords[2],
                        args.light_radius,
                    )

                    created_light.set_actor_label("PointLight" + str(light_no))

                    # ----------------------| Check if light is floating outside of floor slabs
                    if lightFloating(
                        light=created_light, world=world, distance=args.light_floating
                    ):
                        print(
                            "purging current light due to out of bounds from floor slab"
                        )
                        created_light.destroy_actor()

            unreal.SystemLibrary.flush_persistent_debug_lines(
                world_context_object=world
            )

        if args.set_light_intensity:
            intensitySet(
                ue_version=args.ue_version,
                unique_intensity=args.light_intensity,
                random_state=args.random_intensities,
                intensity_set=args.intensity_set,
            )

        if args.light_switch:
            lightSwitch(args.ue_version, args.light_switch_state, prob=0.7)

        if not args.prop_recipe == None:
                prop_no = 0
                # ----------------------| Creating Light Grids based on floor bbox
                print("Creating props coordinates based on floor grid")
                prop_grid = []

                for bbox in floor_bbox:
                    for key in list(bbox):
                        min_x, max_x, min_y, max_y, min_z, max_z = bbox[key][0]
                        prop_coords = propPoses(min_x, max_x, min_y, max_y, min_z, max_z, args.prop_spacing)
                        
                        if random.random() < args.placement_prob: # add the coordinate based on a probability value
                            prop_grid.append(prop_coords)
                print("-------------------------------------------------")

                for prop_coords_set in prop_grid:
                    for prop_coords in prop_coords_set:
                        prop_no += 1
                        print("Spawning new prop:", "Prop" + str(prop_no))

                        prop_name, created_prop = placeProp(args.prop_recipe, prop_coords[0], prop_coords[1], prop_coords[2])
                        created_prop.set_folder_path("/ue_viswp/props")
                        created_prop.set_actor_label(prop_name + '_' + str(prop_no))

                        # # ----------------------| Add the material to the prop
                        propApplyMaterial(created_prop, prop_mat_root="/Game/PROPS/"+prop_name +"/", prop_name=prop_name)

                        # ----------------------| Check if prop intersects with other objects
                        # if len(created_prop.get_overlapping_components()) != 0:
                        #         print("purging current prop due to intersection with obstacle")
                        #         created_prop.destroy_actor()
                        
                        # ----------------------| Check if prop is floating outside of floor slabs
                        if propFloating(prop=created_prop, world=world, distance=args.prop_floating):
                            print("purging current light due to out of bounds from floor slab")
                            created_prop.destroy_actor()

                unreal.SystemLibrary.flush_persistent_debug_lines(world_context_object=world)

        if args.create_cameras:
            # ----------------------| Collect bounding boxes for floor elements to determine camera grids
            floor_bbox = bboxCompute(objects, floor_UID)
            print("------------------------------------------------------------------")

            # ----------------------| Creating Camera Grids based on floor bbox
            print("Creating camera coordinates based on floor grid")
            camera_grid = []

            for bbox in floor_bbox:
                for key in list(bbox):
                    min_x, max_x, min_y, max_y, min_z, max_z = bbox[key][0]
                    camera_coords = cameraGridCreate(min_x, max_x, min_y, max_y, min_z, max_z, args.camera_spacing)
                    camera_grid.append(camera_coords)
            print("-------------------------------------------------")

            camera_no = 0
            for camera_coords_set in camera_grid:
                for cubemap_idx in range(len(CUBEMAP_DIR)):
                    for camera_coords in camera_coords_set:
                        camera_no += 1
                        print("Spawning new camera:", "CameraActor" + str(camera_no) + "_" + CUBEMAP_NAME[cubemap_idx])

                        created_camera = cameraCreate(camera_coords[0], camera_coords[1], camera_coords[2],
                            CUBEMAP_DIR[cubemap_idx][0], CUBEMAP_DIR[cubemap_idx][1], CUBEMAP_DIR[cubemap_idx][2])

                        created_camera.set_folder_path("/ue_viswp/cameras")
                        created_camera.set_actor_label("CameraActor" + str(camera_no) + "_" + CUBEMAP_NAME[cubemap_idx])

                        # ----------------------| Check if camera intersects with other objects
                        # Create an overlap query
                        if cameraIntersect(
                            camera=created_camera,
                            world=world,
                            distance=args.camera_intersect,
                        ):
                            print("purging current camera due to proximity or obstacle")
                            created_camera.destroy_actor()

                        if cameraFloating(camera=created_camera, world=world, distance=args.camera_floating):
                            print("purging current camera due to out of bounds from floor slab")
                            created_camera.destroy_actor()


            unreal.SystemLibrary.flush_persistent_debug_lines(world_context_object=world)

    if args.level_structure:
        showGivenElements(world, state=args.bim_visibility, prob=args.vis_prob)
        camera_no = 0

        for level_id in level_list:
            print(f"Going over objects in {level_id}")

            # ----------------------| Show only objects in current level
            objects = GetElementAtSpecificLevel(level_id, args.ue_version)  # Elements in current level

            # ----------------------| Collect bounding boxes for floor elements to determine camera grids
            floor_bbox = bboxCompute(objects, floor_UID)
            print("------------------------------------------------------------------")
            
            if args.create_lights:
                light_no = 0
                # ----------------------| Creating Light Grids based on floor bbox
                print("Creating light coordinates based on floor grid")
                light_grid = []

                for bbox in floor_bbox:
                    for key in list(bbox):
                        min_x, max_x, min_y, max_y, min_z, max_z = bbox[key][0]
                        light_coords = lightPoses(min_x, max_x, min_y, max_y, min_z, max_z, args.light_spacing)
                        light_grid.append(light_coords)
                print("-------------------------------------------------")

                for light_coords_set in light_grid:
                    for light_coords in light_coords_set:
                        light_no += 1
                        print("Spawning new light:", "PointLight" + str(light_no))

                        created_light = lightCreate(light_coords[0], light_coords[1], light_coords[2], args.light_radius)
                        created_light.set_folder_path("/ue_viswp/lights")
                        created_light.set_actor_label("PointLight" + str(light_no))

                        # ----------------------| Check if light is floating outside of floor slabs
                        if lightFloating(light=created_light, world=world, distance=args.light_floating):
                            print("purging current light due to out of bounds from floor slab")
                            created_light.destroy_actor()

                unreal.SystemLibrary.flush_persistent_debug_lines(world_context_object=world)

            if args.set_light_intensity:
                intensitySet(ue_version=args.ue_version, 
                             unique_intensity=args.light_intensity, 
                             random_state=args.random_intensities, 
                             intensity_set=args.intensity_set)

            if args.light_switch:
                lightSwitch(args.ue_version, args.light_switch_state, prob=0.7)
       
            if not args.prop_recipe == None:
                prop_no = 0
                # ----------------------| Creating Light Grids based on floor bbox
                print("Creating props coordinates based on floor grid")
                prop_grid = []

                for bbox in floor_bbox:
                    for key in list(bbox):
                        min_x, max_x, min_y, max_y, min_z, max_z = bbox[key][0]
                        prop_coords = propPoses(min_x, max_x, min_y, max_y, min_z, max_z, args.prop_spacing)
                        
                        if random.random() < args.placement_prob: # add the coordinate based on a probability value
                            prop_grid.append(prop_coords)
                print("-------------------------------------------------")

                for prop_coords_set in prop_grid:
                    for prop_coords in prop_coords_set:
                        prop_no += 1
                        print("Spawning new prop:", "Prop" + str(prop_no))

                        prop_name, created_prop = placeProp(args.prop_recipe, prop_coords[0], prop_coords[1], prop_coords[2])
                        created_prop.set_folder_path("/ue_viswp/props")
                        created_prop.set_actor_label(prop_name + '_' + str(prop_no))

                        # # ----------------------| Add the material to the prop
                        propApplyMaterial(created_prop, prop_mat_root="/Game/PROPS/"+prop_name +"/", prop_name=prop_name)

                        # ----------------------| Check if prop intersects with other objects
                        # if len(created_prop.get_overlapping_components()) != 0:
                        #         print("purging current prop due to intersection with obstacle")
                        #         created_prop.destroy_actor()
                        
                        # ----------------------| Check if prop is floating outside of floor slabs
                        if propFloating(prop=created_prop, world=world, distance=args.prop_floating):
                            print("purging current light due to out of bounds from floor slab")
                            created_prop.destroy_actor()

                unreal.SystemLibrary.flush_persistent_debug_lines(world_context_object=world)
            
            if args.create_cameras:
                # ----------------------| Creating Camera Grids based on floor bbox
                print("Creating camera coordinates based on floor grid")
                camera_grid = []

                for bbox in floor_bbox:
                    for key in list(bbox):
                        min_x, max_x, min_y, max_y, min_z, max_z = bbox[key][0]
                        camera_coords = cameraGridCreate(min_x, max_x, min_y, max_y, min_z, max_z, args.camera_spacing)
                        camera_grid.append(camera_coords)
                print("-------------------------------------------------")

                for camera_coords_set in camera_grid:
                    for cubemap_idx in camera_config["CUBEMAP_NAME"]:
                        for camera_coords in camera_coords_set:
                            camera_no += 1
                            print("Spawning new camera:", "CameraActor" + str(camera_no) + "_" + str(camera_config["CUBEMAP_DIR"][cubemap_idx]))

                            created_camera = cameraCreate(camera_coords[0], camera_coords[1], camera_coords[2],
                                camera_config["CUBEMAP_DIR"][cubemap_idx][0], camera_config["CUBEMAP_DIR"][cubemap_idx][1], camera_config["CUBEMAP_DIR"][cubemap_idx][2])

                            created_camera.set_folder_path("/ue_viswp/cameras")
                            created_camera.set_actor_label("CameraActor" + str(camera_no) + "_" + str(cubemap_idx))

                            # ----------------------| Check if camera intersects with other objects
                            # Create an overlap query
                            if cameraIntersect(camera=created_camera, world=world, distance=args.camera_intersect):
                                print("purging current camera due to proximity or obstacle")
                                created_camera.destroy_actor()

                            if cameraFloating(camera=created_camera, world=world, distance=args.camera_floating):
                                print("purging current camera due to out of bounds from floor slab")
                                created_camera.destroy_actor()

                            # created_camera.set_actor_label("CameraActor" + str(camera_no) + "_" + CUBEMAP_NAME[cubemap_idx])

                unreal.SystemLibrary.flush_persistent_debug_lines(world_context_object=world)
                
                print("||||---------------END OF LEVEL---------------||||")

    if args.create_canonical:
        obj_per_class = {
            "bath-tub": (["8d6743f08adc8021a26c718ac9ad256f"]),
            "cabinet": (
                [
                    "5c8a0b4f1312e6ba498e39dbdd38c7d3",
                    "179cf7ec6180e9e096cc99dc030c3a4e",
                    "d20eabdbc47ba4b796cda187138236e3",
                    "15ebaef3daf72eb8f913ac9f3c52c001",
                ]
            ),
            "ceiling-framing-wood": (["61d67e5bcd6018675bfb152c200869cc"]),
            "ceiling-gypsumboard": (["518ddf7159b98c1f235dc0df59970e83"]),
            "door": (["a2a2a8099df22bfe13b264cc47ded4bc"]),
            "drywall-framing-wood": (
                [
                    "bff909a91072875a7a15bb4cca9a6004",
                    "3c5472488509d4347fda9ddcb35a536c",
                    "cbf7099a1d4c106a40cea09599c43dda",
                    "b8e3c980cee26c585f4a460ceca28d70",
                    "dfc40d34bd5745ff738269327ab1354e",
                ]
            ),
            "drywall-plastered": (
                [
                    "eed29f0c668da168c7c5c49708c95cdd",
                    "08407528457e59d309955b3e4f1bc7bf",
                    "44e02aa6144b0cea3d31bb1825f7d3ee",
                    "f4c0978898b2a5a8b016e6704e27cbc1",
                    "74095bd59e7021560f1c9e36a8c072f3",
                    "dbaa2d9d193152992757b77aad0c1c5a",
                ]
            ),
            "duct-uninsulated": (
                [
                    "b45b4ebf5e640a588409770d61be0345",
                    "ecb64131917245ca33f91d939c3cb1d8",
                    "ccfe0020c40a3b34ac6a96080bf86496",
                    "87d25dd88a44bca615cc790ffb1df204",
                    "154ae2896b7f0f0df3394089c7eaf310",
                    "1044bd8dbccc08f11bdfc63bede5cd42",
                    "7b8e65a7608ceb7a922b9be69f559d2f",
                    "e40343f12d8ebb7a7f48458d7d989bd8",
                ]
            ),
            "electrical-box": (["7417070699e8b59296f943de8ea052b8"]),
            "electrical-conduit": (["c25cded8d2380881efee8627ef843d1d"]),
            "fan": (["860f7201c6c20422b442acda25b6936e"]),
            "floor": (
                [
                    "6a3b64ed2dd15e86e40944377dc42db0",
                    "973b7124355e95932fdc077fef177b31",
                    "b83614e17f5bd8ce6fe54b2165c5606f",
                ]
            ),
            "foundation-concrete": (["4a4008a916b34dfeab5bfb4b3e8e4021"]),
            "light": (["4f18c81d269021ae8f96b0980d490a39"]),
            "pipe-uninsulated": (
                [
                    "72c4b9cda421f8b28915bb646450f3e6",
                    "e4dd9bc95134ad5e3655dec04ebb8a32",
                    "c66062eefb75efc432691ba411b151d3",
                    "188ef300932e495469a102dbb129ab20",
                    "ec8e3c615788ba0b5f9b91f58f186e5f",
                    "f090c2fcca1840191c9029738e8a1bc6",
                    "86dc856df3c78865727354819fc9e462",
                    "e30e70c99ac7b29ee8a2d4c45947ff8c",
                    "3b8ddc72794b3d4418cbdf610abd662e",
                    "62e858d202010093685b99acd2a7c5ed",
                    "cc00629bff1fb45fa17a69822efce933",
                    "48cad5272227b9596f38a6ab711da270",
                    "ab14f4377042873b10345be2d3ad3af6",
                    "0a5bb2e39815a4ee1832b168a34877d7",
                    "19741701a8c6bcf78c707426dada33e6",
                    "a4349cb34286755e0b8c6d0edc7a9864",
                    "9212afb0da580380724358aa4567fc85",
                    "3eaf7666cf7c595b071c79716511b1ea",
                    "02f87a9787b38da186e12bcbb17e4995",
                    "517ed788a13238471a6369a65bb1d9cc",
                    "3adc377885cbaf1e884d97ce8733a335",
                    "d38991385daa50fd9923a76be5ee527a",
                    "5d2f6221a5c9d27d3609c45b81157dd8",
                    "3d069007f2e81b91fd7b0cb26a38ad4f",
                    "5430f80b7475d46f1df362287d129115",
                    "e7a5a693ed586fd3304d3a9e82e05df9",
                    "a8b2d94e99c0a90c4cb9198bfce59df3",
                    "050ffb926c8e2b0c4e9d0377ffaf356d",
                    "c765993498c2cd03fa7028c91dfc9386",
                    "111e49a9fcb7f7a164a75883ac949357",
                ]
            ),
            "railing": (["23d7edf493b2e82d133e62f469d58daa"]),
            "sink": (
                [
                    "ec8b76c9e2d471ce94027b8ed2023f0d",
                    "20b4f2a9e876edfbb33a118eb7c30961",
                    "bb1d56e0f97950f2d6ecda1b7807aeca",
                    "4ccc991a193b90afab6a709db5ec867a",
                    "9973caf61cc8f6b8de08233073aa9131",
                ]
            ),
            "stairs": (
                [
                    "8b64bb661df704086ed447769cfe1390",
                    "b51843f370f8a5f29c9ce179bda7bfe2",
                    "403503b402c86ed150bca92885cdde2d",
                ]
            ),
            "toilet": (["79bb47fb2e603939240e74b4ca1e1bb3"]),
            "vent": (["14c2becb01d3e0559583f594ee706780"]),
            "waterheater": (["7456c926e5ac07ffb7d90b73d1956606"]),
        }

        viswp_present_classes = unreal.GameplayStatics.get_all_actors_of_class(
            world, unreal.DatasmithSceneActor
        )
        for viswp_class in viswp_present_classes:
            target_list = obj_per_class[viswp_class.get_actor_label()]

            for level_id in level_list:
                print("Parsing for targeted element in:", level_id)

                # ----------------------| Show only objects in current level
                objects = GetElementAtSpecificLevel(
                    level_id
                )  # Elements in current level

                for object in objects:
                    datasmith_usr_data = (
                        unreal.DatasmithContentLibrary.get_datasmith_user_data(object)
                    )

                    if "Datasmith_UniqueId" in list(datasmith_usr_data.metadata.keys()):
                        unique_id = "".join(
                            list(datasmith_usr_data.metadata["Datasmith_UniqueId"])
                        )

                        if unique_id in target_list[0]:
                            bounding_box_coords = defaultdict(list)
                            center, bbox = object.get_actor_bounds(
                                only_colliding_components=False
                            )

                            sphere_coordinates = cameraCanonical(
                                n_cams=50, elem_center=center, radius=500
                            )
                            camera_no = 0

                            for camera_coords in sphere_coordinates:
                                rotator_vector = unreal.Vector(
                                    *camera_coords
                                ).direction_unit_to(center)
                                rotator_angles = rotator_vector.rotator()

                                camera_no += 1

                                created_camera = cameraCreate(
                                    *camera_coords,
                                    rotator_angles.roll,
                                    rotator_angles.pitch,
                                    rotator_angles.yaw,
                                )

                                created_camera.set_actor_label(
                                    viswp_class.get_actor_label()
                                    + "_CameraActor"
                                    + str(camera_no)
                                )

                        else:
                            continue

                    else:
                        continue

    if CAPTURE_CANONICAL_ELEMS:
        target_class = "drywall-framing-wood"
        obj_per_class = {
            "bath-tub": (["8d6743f08adc8021a26c718ac9ad256f"]),
            "cabinet": (
                [
                    "5c8a0b4f1312e6ba498e39dbdd38c7d3",
                    "179cf7ec6180e9e096cc99dc030c3a4e",
                    "d20eabdbc47ba4b796cda187138236e3",
                    "15ebaef3daf72eb8f913ac9f3c52c001",
                ]
            ),
            "ceiling-framing-wood": (["61d67e5bcd6018675bfb152c200869cc"]),
            "ceiling-gypsumboard": (["518ddf7159b98c1f235dc0df59970e83"]),
            "door": (["a2a2a8099df22bfe13b264cc47ded4bc"]),
            "drywall-framing-wood": (
                [
                    "bff909a91072875a7a15bb4cca9a6004",
                    "3c5472488509d4347fda9ddcb35a536c",
                    "cbf7099a1d4c106a40cea09599c43dda",
                    "b8e3c980cee26c585f4a460ceca28d70",
                    "dfc40d34bd5745ff738269327ab1354e",
                ]
            ),
            "drywall-plastered": (
                [
                    "eed29f0c668da168c7c5c49708c95cdd",
                    "08407528457e59d309955b3e4f1bc7bf",
                    "44e02aa6144b0cea3d31bb1825f7d3ee",
                    "f4c0978898b2a5a8b016e6704e27cbc1",
                    "74095bd59e7021560f1c9e36a8c072f3",
                    "dbaa2d9d193152992757b77aad0c1c5a",
                ]
            ),
            "duct-uninsulated": (
                [
                    "b45b4ebf5e640a588409770d61be0345",
                    "ecb64131917245ca33f91d939c3cb1d8",
                    "ccfe0020c40a3b34ac6a96080bf86496",
                    "87d25dd88a44bca615cc790ffb1df204",
                    "154ae2896b7f0f0df3394089c7eaf310",
                    "1044bd8dbccc08f11bdfc63bede5cd42",
                    "7b8e65a7608ceb7a922b9be69f559d2f",
                    "e40343f12d8ebb7a7f48458d7d989bd8",
                ]
            ),
            "electrical-box": (["7417070699e8b59296f943de8ea052b8"]),
            "electrical-conduit": (["c25cded8d2380881efee8627ef843d1d"]),
            "fan": (["860f7201c6c20422b442acda25b6936e"]),
            "floor": (
                [
                    "6a3b64ed2dd15e86e40944377dc42db0",
                    "973b7124355e95932fdc077fef177b31",
                    "b83614e17f5bd8ce6fe54b2165c5606f",
                ]
            ),
            "foundation-concrete": (["4a4008a916b34dfeab5bfb4b3e8e4021"]),
            "light": (["4f18c81d269021ae8f96b0980d490a39"]),
            "pipe-uninsulated": (
                [
                    "72c4b9cda421f8b28915bb646450f3e6",
                    "e4dd9bc95134ad5e3655dec04ebb8a32",
                    "c66062eefb75efc432691ba411b151d3",
                    "188ef300932e495469a102dbb129ab20",
                    "ec8e3c615788ba0b5f9b91f58f186e5f",
                    "f090c2fcca1840191c9029738e8a1bc6",
                    "86dc856df3c78865727354819fc9e462",
                    "e30e70c99ac7b29ee8a2d4c45947ff8c",
                    "3b8ddc72794b3d4418cbdf610abd662e",
                    "62e858d202010093685b99acd2a7c5ed",
                    "cc00629bff1fb45fa17a69822efce933",
                    "48cad5272227b9596f38a6ab711da270",
                    "ab14f4377042873b10345be2d3ad3af6",
                    "0a5bb2e39815a4ee1832b168a34877d7",
                    "19741701a8c6bcf78c707426dada33e6",
                    "a4349cb34286755e0b8c6d0edc7a9864",
                    "9212afb0da580380724358aa4567fc85",
                    "3eaf7666cf7c595b071c79716511b1ea",
                    "02f87a9787b38da186e12bcbb17e4995",
                    "517ed788a13238471a6369a65bb1d9cc",
                    "3adc377885cbaf1e884d97ce8733a335",
                    "d38991385daa50fd9923a76be5ee527a",
                    "5d2f6221a5c9d27d3609c45b81157dd8",
                    "3d069007f2e81b91fd7b0cb26a38ad4f",
                    "5430f80b7475d46f1df362287d129115",
                    "e7a5a693ed586fd3304d3a9e82e05df9",
                    "a8b2d94e99c0a90c4cb9198bfce59df3",
                    "050ffb926c8e2b0c4e9d0377ffaf356d",
                    "c765993498c2cd03fa7028c91dfc9386",
                    "111e49a9fcb7f7a164a75883ac949357",
                ]
            ),
            "railing": (["23d7edf493b2e82d133e62f469d58daa"]),
            "sink": (
                [
                    "ec8b76c9e2d471ce94027b8ed2023f0d",
                    "20b4f2a9e876edfbb33a118eb7c30961",
                    "bb1d56e0f97950f2d6ecda1b7807aeca",
                    "4ccc991a193b90afab6a709db5ec867a",
                    "9973caf61cc8f6b8de08233073aa9131",
                ]
            ),
            "stairs": (
                [
                    "8b64bb661df704086ed447769cfe1390",
                    "b51843f370f8a5f29c9ce179bda7bfe2",
                    "403503b402c86ed150bca92885cdde2d",
                ]
            ),
            "toilet": (["79bb47fb2e603939240e74b4ca1e1bb3"]),
            "vent": (["14c2becb01d3e0559583f594ee706780"]),
            "waterheater": (["7456c926e5ac07ffb7d90b73d1956606"]),
        }

        # Hiding all other actors
        for actor in unreal.EditorLevelLibrary.get_all_level_actors():
            if unreal.DatasmithContentLibrary.get_datasmith_user_data(actor):
                actor.set_is_temporarily_hidden_in_editor(True)

        viswp_present_classes = unreal.GameplayStatics.get_all_actors_of_class(
            world, unreal.DatasmithSceneActor
        )
        for viswp_class in viswp_present_classes:
            viswp_class_name = viswp_class.get_actor_label()

            if viswp_class_name != target_class:
                continue

            target_list = obj_per_class[viswp_class_name]

            for level_id in level_list:
                print("Parsing for targeted element in:", level_id)
                objects = GetElementAtSpecificLevel(
                    level_id
                )  # Elements in current level

                for object in objects:
                    datasmith_usr_data = (
                        unreal.DatasmithContentLibrary.get_datasmith_user_data(object)
                    )

                    if "Datasmith_UniqueId" in list(datasmith_usr_data.metadata.keys()):
                        unique_id = "".join(
                            list(datasmith_usr_data.metadata["Datasmith_UniqueId"])
                        )

                        if unique_id in target_list:
                            object.set_is_temporarily_hidden_in_editor(False)

        # cameraCapture()

    if args.take_photos:
        cameras = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.CameraActor)
        cameraCapture(camera_actors=cameras)

    if args.count_elements:
        for level_id in level_list:
            print("Going over objects in", level_id)

            # ----------------------| Show only objects in current level
            objects = GetElementAtSpecificLevel(level_id)  # Elements in current level
            print("Total No. of Objects is:", len(objects))

if __name__ == "__main__":
    main()
