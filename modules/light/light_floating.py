import unreal


def lightFloating(light, world, distance=800):
    # Get the camera's location and forward vector
    light_location = light.get_actor_location()
    light_down_vector = unreal.Vector(float(0), float(0), float(-1))

    # Perform the line trace
    hit_result = unreal.SystemLibrary.line_trace_single(world,
                                                        start=light_location,
                                                        end=light_location + light_down_vector * distance,
                                                        trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                        trace_complex=True,
                                                        actors_to_ignore=[None],
                                                        draw_debug_type=unreal.DrawDebugTrace.PERSISTENT,
                                                        ignore_self=True
                                                        )

    # Check if the line trace hit anything
    if hit_result is not None:
        lightFloating_state = False
    else:
        lightFloating_state = True

    return lightFloating_state
