import unreal

def lightCreate(xloc, yloc, zloc, radius):
    '''
    Main function to create a camera in a given location with a
    given rotation.

    Inputs:
        - location (list): a set of x,y,z coordinates
        - rotation (list): a set of camera rotation values (in degrees)

    Output:
        Issue a command to spawn a camera.
    '''

    # # --------------------------| Create & spawn camera
    light_object = unreal.PointLight
    light_location = unreal.Vector(float(xloc), float(yloc), float(zloc))
    created_light = unreal.EditorLevelLibrary.spawn_actor_from_class(light_object, light_location)

    # # --------------------------| Collect camera properties after creation
    light_components = unreal.PointLightComponent(created_light)
    light_components.set_source_radius(radius)

    return created_light
