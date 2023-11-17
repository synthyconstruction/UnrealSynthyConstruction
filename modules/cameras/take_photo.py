import unreal
import time
import os


class cameraCapture(object):
    '''
    Description: Execution function to take photos of selected cameras in the editor
    '''

    def __init__(self, camera_actors, suffix='', resolution=[480, 480]):

        unreal.LevelEditorSubsystem().editor_set_game_view(True)
        self.cameras = (actor for actor in unreal.EditorLevelLibrary.get_selected_level_actors())
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


class canonicalCameraCapture(object):
    '''
    Description: Execution function to take photos of selected cameras in the editor
    '''

    def __init__(self, viswp_class):
        unreal.EditorLevelLibrary.editor_set_game_view(True)
        self.actors = (actor for actor in unreal.EditorLevelLibrary.get_selected_level_actors())
        self.on_pre_tick = unreal.register_slate_pre_tick_callback(self.__pretick__)
        self.viswp_class = viswp_class

    def __pretick__(self, deltatime):
        try:
            # Extracting camera actor name & positional parameters
            actor = next(self.actors)
            actor_name = actor.get_name()

            while actor_name.split('_')[0] == self.viswp_class:
                actor_location = actor.get_actor_location()
                actor_rotation = actor.get_actor_rotation()

                # Place viewport at camera's view
                unreal.EditorLevelLibrary.set_level_viewport_camera_info(actor_location, actor_rotation)

                # unreal.EditorLevelLibrary.pilot_level_actor(actor)
                # time.sleep(3)

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

                unreal.AutomationLibrary.take_high_res_screenshot(
                    480, 480, actor_name + ".png", mask_enabled=False, capture_hdr=True, delay=0.000000,
                    comparison_tolerance=unreal.ComparisonTolerance.HIGH)

                unreal.EditorLevelLibrary.eject_pilot_level_actor()

        except Exception as error:
            print(error)
            unreal.unregister_slate_pre_tick_callback(self.on_pre_tick)
