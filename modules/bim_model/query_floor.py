import unreal


def queryFloor(floor_class_names, world):

    unique_floor_ids = []

    def _inloop_apply_all_childs(root_actor, unique_ids):
        child_actors = root_actor.get_attached_actors()
        for child_actor in child_actors:
            if isinstance(child_actor, unreal.StaticMeshActor):
                datasmith_usr_data = unreal.DatasmithContentLibrary.get_datasmith_user_data(child_actor)
                unique_ids.append(''.join(list(datasmith_usr_data.metadata['Datasmith_UniqueId'])))
            _inloop_apply_all_childs(child_actor, unique_ids)

    datasmith_classes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.DatasmithSceneActor)

    for ViS_WP_class in datasmith_classes:
        class_name = ViS_WP_class.get_actor_label()

        if class_name in floor_class_names:
            _inloop_apply_all_childs(ViS_WP_class, unique_floor_ids)

            return unique_floor_ids

        else:
            continue
