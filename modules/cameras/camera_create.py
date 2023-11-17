import unreal
import numpy as np


def cameraCreate(xloc, yloc, zloc, xrot, yrot, zrot):
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
    camera_object = unreal.CameraActor
    camera_location = unreal.Vector(float(xloc), float(yloc), float(zloc))
    camera_rotation = unreal.Rotator(xrot, yrot, zrot)
    created_camera = unreal.EditorLevelLibrary.spawn_actor_from_class(camera_object, camera_location, camera_rotation)

    # # --------------------------| Collect camera properties after creation
    camera_components = unreal.CameraComponent(created_camera)
    camera_components.set_field_of_view(90.0)
    camera_components.set_use_field_of_view_for_lod(True)
    camera_components.set_aspect_ratio(1.0)

    return created_camera


def cameraCanonical(n_cams, elem_center, radius):

    # REFERENCE: https://stackoverflow.com/questions/53966695/points-on-sphere
    # Other references:
    #   https://stackoverflow.com/questions/33976911/generate-a-random-sample-of-points-distributed-on-the-surface-of-a-unit-sphere
    #   https://stackoverflow.com/questions/29398875/how-can-i-obtain-the-coordinates-for-a-sphere-using-python

    # generate the random quantities
    phi = np.random.uniform(0, 2*np.pi, size=(n_cams,))
    theta_cos = np.random.uniform(-1,       1, size=(n_cams,))
    u = np.random.uniform(0,       1, size=(n_cams,))

    # calculate sin(theta) from cos(theta)
    theta_sin = np.sqrt(1 - theta_cos**2)
    r = radius * np.cbrt(u)

    sphere_coordinates = np.array([np.array([elem_center.x + r[i] * theta_sin[i] * np.cos(phi[i]),
                                             elem_center.y + r[i] * theta_sin[i] * np.sin(phi[i]),
                                             elem_center.z + r[i] * theta_cos[i]]) for i in range(n_cams)])

    return sphere_coordinates
