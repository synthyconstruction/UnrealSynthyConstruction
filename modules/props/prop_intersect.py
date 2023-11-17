import unreal


def propIntersect(prop_actor, world):
    # Get the camera's location and forward vector
    prop_actor_location = prop_actor.get_actor_location()
    prop_actor_forward = prop_actor.get_actor_forward_vector()

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

def propFloating(prop, world, distance=800):
    # Get the camera's location and forward vector
    prop_location = prop.get_actor_location()
    prop_down_vector = unreal.Vector(float(0), float(0), float(-1))

    # Perform the line trace
    hit_result = unreal.SystemLibrary.line_trace_single(world,
                                                        start=prop_location,
                                                        end=prop_location + prop_down_vector * distance,
                                                        trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                        trace_complex=True,
                                                        actors_to_ignore=[None],
                                                        draw_debug_type=unreal.DrawDebugTrace.PERSISTENT,
                                                        ignore_self=True
                                                        )

    # Check if the line trace hit anything
    if hit_result is not None:
        propFloating_state = False
    else:
        propFloating_state = True

    return propFloating_state
