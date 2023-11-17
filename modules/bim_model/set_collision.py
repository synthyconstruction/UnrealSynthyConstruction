import unreal


def setCollision(world):
    """
    Description:
    Args:\n
        world: ...\n
    Return:\n
        void() \n
    Example:\n
    """

    def _inloop_apply_all_childs(root_actor):
        child_actors = root_actor.get_attached_actors()
        for child_actor in child_actors:
            if isinstance(child_actor, unreal.StaticMeshActor):
                child_actor.set_actor_enable_collision(True)


            _inloop_apply_all_childs(child_actor)

    datasmith_parent_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.DatasmithSceneActor)

    for ds_actor in datasmith_parent_actors:
        _inloop_apply_all_childs(ds_actor)