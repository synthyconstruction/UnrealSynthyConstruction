import unreal


def cameraIntersect(camera, world, distance=200):
    # Get the camera's location and forward vector
    camera_location = camera.get_actor_location()
    camera_forward = camera.get_actor_forward_vector()

    # Perform the line trace
    hit_result = unreal.SystemLibrary.line_trace_single(world,
                                                        start=camera_location,
                                                        end=camera_location + camera_forward * distance,
                                                        trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                        trace_complex=True,
                                                        actors_to_ignore=[None],
                                                        draw_debug_type=unreal.DrawDebugTrace.PERSISTENT,
                                                        ignore_self=True
                                                        )

    # Check if the line trace hit anything
    if hit_result is not None:
        cameraIntersect_state = True
    else:
        cameraIntersect_state = False

    return cameraIntersect_state


def cameraFloating(camera, world, distance=200):
    # Get the camera's location and forward vector
    camera_location = camera.get_actor_location()
    camera_down_vector = unreal.Vector(float(0), float(0), float(-1))

    # Perform the line trace
    hit_result = unreal.SystemLibrary.line_trace_single(world,
                                                        start=camera_location,
                                                        end=camera_location + camera_down_vector * distance,
                                                        trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                        trace_complex=True,
                                                        actors_to_ignore=[None],
                                                        draw_debug_type=unreal.DrawDebugTrace.PERSISTENT,
                                                        ignore_self=True
                                                        )

    # Check if the line trace hit anything
    if hit_result is not None:
        cameraFloating_state = False
    else:
        cameraFloating_state = True

    return cameraFloating_state


def cameraNear(camera, distance, objects):

    # Get the camera's forward vector
    camera_forward = camera.get_actor_forward_vector()

    # Get all the actors in the level

    # Check if the camera is near any actor in the direction of the camera lens
    for actor in objects:
        # Skip the camera actor
        if actor == camera:
            continue

        # Get the direction vector from the camera to the other actor
        direction = (actor.get_actor_location() - camera.get_actor_location()).normalize()

        # Check if the direction vector is parallel to the camera's forward vector
        if direction.is_parallel(camera_forward):
            # Get the distance between the actors
            distance_between_actors = (camera.get_actor_location() - actor.get_actor_location()).size()

        # Check if the distance is less than the specified distance
        if distance_between_actors < distance:
            return True

    return False
