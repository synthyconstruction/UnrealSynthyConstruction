import unreal
import random


def showGivenElements(world, state, prob=0.2):
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

    def _inloop_apply_all_childs(root_actor, state, prob):
        child_actors = root_actor.get_attached_actors()
        for child_actor in child_actors:
            if isinstance(child_actor, unreal.StaticMeshActor):

                if state == "all_on":
                    child_actor.set_is_temporarily_hidden_in_editor(False)
                elif state == "all_off":
                    child_actor.set_is_temporarily_hidden_in_editor(True)
                elif state == "random":
                    turn_off_state = decision(prob)
                    child_actor.set_is_temporarily_hidden_in_editor(turn_off_state)

            _inloop_apply_all_childs(child_actor, state, prob)

    datasmith_parent_actors = unreal.GameplayStatics.get_all_actors_of_class(
        world, unreal.DatasmithSceneActor)

    for ds_actor in datasmith_parent_actors:
        _inloop_apply_all_childs(ds_actor, state, prob)
