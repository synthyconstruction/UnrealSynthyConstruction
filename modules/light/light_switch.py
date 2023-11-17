import unreal
import random


def lightSwitch(ue_version, state, prob=0.5):
    '''
    Description: \n 
    Args:\n
    Example:\n
    '''

    if state == "all_on":
        print("Turning ON all static meshes")
    elif state == "random":
        print("Randomly turning ON static meshes by given PROBABILITY")
        print("Using a probability of:", prob)
    elif state == "all_off":
        print("Turning OFF all static meshes")

    def decision(probability):
        return random.random() < probability

    # if ue_version > 4.27:
    #     all_actors = unreal.EditorActorSubsystem().get_all_level_actors()
    # if ue_version < 5.0:
    #     all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    lights = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.PointLight)
    for light in lights:
        if isinstance(light, unreal.PointLight):
            if state == "on":
                light.set_is_temporarily_hidden_in_editor(False)
            elif state == "off":
                light.set_is_temporarily_hidden_in_editor(True)
            elif state == "random":
                turn_off_state = decision(prob)
                light.set_is_temporarily_hidden_in_editor(turn_off_state)
