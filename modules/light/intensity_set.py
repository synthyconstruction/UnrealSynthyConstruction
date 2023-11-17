import unreal
import random


def intensitySet(ue_version, unique_intensity, random_state, intensity_set):
    '''
    Function to assign a light intensity value to a light object depending on the precomputed values.
    '''

    # if ue_version > 4.27:
    #     all_actors = unreal.EditorActorSubsystem().get_all_level_actors()
    # if ue_version < 5.0:
    #     all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    lights = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.PointLight)
    for light in lights:
        if isinstance(light, unreal.PointLight):
            light_components = unreal.PointLightComponent(light)
            if random_state == True:  # randomly assign the intensity of the ligth based on a value from the intensity set
                intensity_val_selected = random.choice(intensity_set)
                light_components.set_editor_properties({'intensity': intensity_val_selected})
            else:
                light_components.set_editor_properties({'intensity': unique_intensity})
    return
