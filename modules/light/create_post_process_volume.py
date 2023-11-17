import unreal

def createPostProcessVol():
    post_process_volume_class = unreal.PostProcessVolume.static_class()  # Get the PostProcessVolume class
    post_process_volume = unreal.EditorLevelLibrary.spawn_actor_from_class(
        post_process_volume_class, unreal.Vector(0, 0, 0),
        unreal.Rotator(0, 0, 0))  # Spawn the PostProcessVolume actor
    post_process_volume.unbound = True
    post_process_setting = unreal.PostProcessSettings